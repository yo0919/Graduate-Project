# ML_Model/find_optimized_settings.py

import pandas as pd
from itertools import product

# dataSize 변환 함수
def convert_size(size):
    if 'G' in size:
        return int(size.replace('G', '')) * 1024  # GB to MB 변환
    elif 'M' in size:
        return int(size.replace('M', ''))  # MB 유지
    else:
        raise ValueError("Invalid size format")

# 최적화된 설정을 찾는 함수 정의
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
