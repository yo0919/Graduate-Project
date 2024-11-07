from flask import Flask, request, jsonify
from flask_cors import CORS
import paramiko
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)  # CORS 적용

# 모델 로드 (모델과 특징 이름을 함께 로드)
model, model_features = joblib.load("model.pkl")  # 학습한 모델 파일 경로

# dataSize 변환 함수
def convert_size(size):
    if 'G' in size:
        return int(size.replace('G', '')) * 1024  # GB to MB 변환
    elif 'M' in size:
        return int(size.replace('M', ''))  # MB 유지
    else:
        raise ValueError("Invalid size format")

# 최적화된 설정을 찾는 함수
def find_optimized_settings(model, base_settings, model_features):
    # 현재 dataSize를 MB로 변환
    base_data_size_mb = convert_size(base_settings["dataSize"])

    # ±500 MB 범위에서 dataSize 설정
    data_sizes = [base_data_size_mb - 500, base_data_size_mb, base_data_size_mb + 500]
    data_sizes = [size for size in data_sizes if size > 0]  # 0보다 큰 값만 사용

    # 다른 매개변수 변경 범위 설정
    read_write_ratios = [base_settings["readWriteRatio"], "randread", "rw"]
    task_types = [base_settings["taskType"], "seq", "rand"]
    cache_usages = [base_settings["cacheUsage"], not base_settings["cacheUsage"]]
    io_priorities = [base_settings["ioPriority"], "throughput", "latency"]

    max_iops = 0
    best_settings = base_settings.copy()

    # dataSize 범위와 다른 매개변수 조합 생성 및 예측
    for data_size in data_sizes:
        for rw_ratio in read_write_ratios:
            for task_type in task_types:
                for cache_usage in cache_usages:
                    for io_priority in io_priorities:
                        # 테스트할 설정 만들기
                        test_settings = base_settings.copy()
                        test_settings["dataSize"] = f"{data_size}M"  # dataSize를 MB 형식으로 설정
                        test_settings["readWriteRatio"] = rw_ratio
                        test_settings["taskType"] = task_type
                        test_settings["cacheUsage"] = cache_usage
                        test_settings["ioPriority"] = io_priority

                        # 데이터프레임 변환 및 전처리
                        df_test = pd.DataFrame([test_settings])
                        df_test['dataSize'] = df_test['dataSize'].apply(convert_size)
                        df_test = pd.get_dummies(df_test, columns=["taskType", "readWriteRatio", "cacheUsage", "ioPriority"])
                        df_test = df_test.reindex(columns=model_features, fill_value=0)

                        # 모델 예측
                        predicted_iops = model.predict(df_test)[0]

                        # 최고 IOPS 값을 제공하는 설정 업데이트
                        if predicted_iops > max_iops:
                            max_iops = predicted_iops
                            best_settings = test_settings.copy()

    return best_settings

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.json  # JSON 형식의 요청 데이터 받기
    print(data)  # 서버 콘솔에 출력

    # QEMU에서 fio 명령 실행
    try:
        output = run_fio_on_qemu()  # QEMU에서 fio 실행
        print(output)  # 콘솔에 출력
    except Exception as e:
        print(f"Error running fio on QEMU: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    # 데이터 전처리
    df = pd.DataFrame([data])  # 데이터프레임 생성

    # dataSize 열 변환
    try:
        df['dataSize'] = df['dataSize'].apply(convert_size)
    except ValueError as e:
        print(f"Error in dataSize conversion: {e}")
        return jsonify({"status": "error", "message": "Invalid dataSize format"}), 400

    # 범주형 변수 인코딩
    df = pd.get_dummies(df, columns=["taskType", "readWriteRatio", "cacheUsage", "ioPriority"])

    # 입력 데이터가 학습 시 사용된 특징 이름과 일치하도록 조정
    df = df.reindex(columns=model_features, fill_value=0)

    # 예측값 계산
    predicted_iops = model.predict(df)[0]  # 예측 IOPS 값

    # 최적화된 설정을 동적으로 생성
    optimized_settings = find_optimized_settings(model, data, model_features)

    return jsonify({
        "status": "success",
        "data": data,
        "performance_output": output,
        "predicted_iops": predicted_iops,
        "optimized_settings": optimized_settings
    }), 200  # 응답

def run_fio_on_qemu():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # QEMU SSH 연결 정보 (포트 2222 사용)
    ssh.connect('127.0.0.1', username='yo0919', password='Rayjeon12!', port=2222)

    command = 'fio --name=job1 --ioengine=libaio --rw=randwrite --bs=4k --size=1G --runtime=60s --time_based --group_reporting'
    stdin, stdout, stderr = ssh.exec_command(command)

    output = stdout.read().decode()
    error = stderr.read().decode()

    ssh.close()

    return output if not error else error

if __name__ == '__main__':
    app.run(debug=True)  # 디버그 모드로 실행
