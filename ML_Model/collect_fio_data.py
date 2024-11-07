import paramiko
import csv
from itertools import product

# SSH 연결 설정
QEMU_HOST = "127.0.0.1"  # QEMU 인스턴스의 IP 주소
QEMU_PORT = 2222  # QEMU 인스턴스의 SSH 포트
USERNAME = "yo0919"  # QEMU 인스턴스의 사용자 이름
PASSWORD = "Rayjeon12!"  # QEMU 인스턴스의 비밀번호

# 테스트할 매개변수 조합 정의
data_sizes = ['500M', '1G', '2G']
read_write_ratios = ['randwrite', 'randread', 'rw']
task_types = ['seq', 'rand']
cache_usages = [True, False]
io_priorities = ['throughput', 'latency']

# CSV 파일에 데이터를 저장할 헤더
headers = ['dataSize', 'readWriteRatio', 'taskType', 'cacheUsage', 'ioPriority', 'iops', 'bw']

# CSV 파일 생성 및 데이터 수집
with open('fio_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)  # 헤더 작성

    # Paramiko로 SSH 연결
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(QEMU_HOST, port=QEMU_PORT, username=USERNAME, password=PASSWORD)

    for data_size, rw_ratio, task_type, cache_usage, io_priority in product(data_sizes, read_write_ratios, task_types,
                                                                            cache_usages, io_priorities):
        # `fio` 명령어 구성
        fio_command = (
            f"fio --name=job1 --size={data_size} --rw={rw_ratio} --ioengine=libaio --bs=4k "
            f"--runtime=60s --time_based --group_reporting --unlink=1"  # 파일 자동 삭제 옵션 추가
        )

        if cache_usage:
            fio_command += " --buffered=1"
        if io_priority == "latency":
            fio_command += " --iodepth=1"
        else:
            fio_command += " --iodepth=16"

        try:
            # 원격에서 `fio` 명령어 실행
            stdin, stdout, stderr = ssh.exec_command(fio_command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            # 에러가 있으면 출력하고 넘어감
            if error:
                print(f"Error: {error}")
                continue

            # 5. 결과 파싱 (IOPS 및 대역폭(BW) 추출)
            iops_line = [line for line in output.split('\n') if 'IOPS=' in line]
            bw_line = [line for line in output.split('\n') if 'BW=' in line]

            if iops_line and bw_line:
                iops = int(iops_line[0].split('=')[1].split(',')[0].strip())
                bw = bw_line[0].split('=')[1].split(',')[0].strip()

                # 6. CSV 파일에 데이터 저장
                writer.writerow([data_size, rw_ratio, task_type, cache_usage, io_priority, iops, bw])
                print(
                    f"Collected data for {data_size}, {rw_ratio}, {task_type}, {cache_usage}, {io_priority}: IOPS={iops}, BW={bw}")

            # 캐시 해제 명령 실행
            ssh.exec_command("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null")

        except Exception as e:
            print(f"Failed to execute fio command on QEMU with error: {e}")

    # SSH 연결 닫기
    ssh.close()
