# fio_performance_graph.py

import pandas as pd
import matplotlib.pyplot as plt

# 1. 데이터 로드
data = pd.read_csv("fio_data.csv")

# 2. IOPS와 BW 그래프 그리기
plt.figure(figsize=(12, 6))

# IOPS 그래프
plt.subplot(1, 2, 1)
plt.plot(data.index, data['iops'], marker='o', color='b', label='IOPS')
plt.title("IOPS Performance")
plt.xlabel("Test Case")
plt.ylabel("IOPS")
plt.legend()

# BW 그래프
plt.subplot(1, 2, 2)
plt.plot(data.index, data['bw'], marker='o', color='g', label='BW (KB/s)')
plt.title("Bandwidth (BW) Performance")
plt.xlabel("Test Case")
plt.ylabel("BW (KB/s)")
plt.legend()

plt.tight_layout()
plt.savefig("fio_performance_graph.png", format="png")
plt.show()
