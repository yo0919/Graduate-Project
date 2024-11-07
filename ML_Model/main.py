import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# 1. 데이터 로드
data = pd.read_csv("fio_data.csv")  # 데이터 파일 경로를 지정하세요

# 2. dataSize 열 변환 (MB 단위로 변환)
data['dataSize'] = data['dataSize'].apply(lambda x: int(x.replace('M', '')) if 'M' in x else int(x.replace('G', '')) * 1024)

# X와 y 설정
X = data.drop(columns=["iops"])  # 'iops' 대신 목표 성능 지표 열
y = data["iops"]

# 3. 데이터 전처리
# 필요에 따라 범주형 변수를 인코딩합니다.
X = pd.get_dummies(X, columns=["taskType", "readWriteRatio", "cacheUsage", "ioPriority"])

# 학습 시 사용한 특징 이름 저장
model_features = X.columns.tolist()  # 학습에 사용된 특징 이름 저장

# 4. 데이터 분할 (훈련 및 테스트)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. 모델 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. 모델 평가
score = model.score(X_test, y_test)
print(f"테스트 세트 R^2 스코어: {score}")

# 7. 모델과 특징 이름을 함께 저장
joblib.dump((model, model_features), "model.pkl")
print("모델과 특징 이름이 model.pkl 파일로 저장되었습니다.")
