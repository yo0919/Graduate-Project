import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# 1. 데이터 로드
data = pd.read_csv("fio_data.csv")

# 'dataSize' 열의 문자열 값을 숫자로 변환 ('M'이나 'G'를 숫자로 변경)
def convert_data_size(size):
    if size.endswith('M'):
        return float(size[:-1]) * 1e6  # 메가바이트(M)를 바이트로 변환
    elif size.endswith('G'):
        return float(size[:-1]) * 1e9  # 기가바이트(G)를 바이트로 변환
    else:
        return float(size)  # 다른 경우에는 그대로 숫자로 사용

data['dataSize'] = data['dataSize'].apply(convert_data_size)

# X와 y 분리
X = data.drop(columns=["iops"])
y = data["iops"]

# 2. 데이터 전처리 및 모델 학습
# 'readWriteRatio'도 원-핫 인코딩을 수행
X = pd.get_dummies(X, columns=["readWriteRatio", "taskType", "cacheUsage", "ioPriority"])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3. 예측
y_pred = model.predict(X_test)

# 4. 예측값과 실제값 비교 그래프
plt.figure(figsize=(10, 5))
plt.plot(y_test.values, label='Actual IOPS', marker='o')
plt.plot(y_pred, label='Predicted IOPS', marker='x')
plt.title("Actual vs Predicted IOPS")
plt.xlabel("Test Sample")
plt.ylabel("IOPS")
plt.legend()
plt.savefig("iops_prediction_comparison.png", format="png")
plt.show()
