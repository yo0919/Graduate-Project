import React, { useState } from 'react';
import '../styles/InputForm.css';

interface OptimizedSettings {
    dataSize: string;
    readWriteRatio: string;
    taskType: string;
    cacheUsage: boolean;
    ioPriority: string;
}

interface ServerResponse {
    predicted_iops: number;
    optimized_settings: OptimizedSettings;
    recommendations: string[];
    performance_output: string;
}

const InputForm: React.FC = () => {
    const [dataSize, setDataSize] = useState('');
    const [readWriteRatio, setReadWriteRatio] = useState('');
    const [taskType, setTaskType] = useState('순차');
    const [speedRequirement, setSpeedRequirement] = useState('보통');
    const [cacheUsage, setCacheUsage] = useState(false);
    const [ioPriority, setIoPriority] = useState('처리량 우선');

    // 응답 데이터를 저장할 상태 추가
    const [response, setResponse] = useState<ServerResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);  // 로딩 상태 추가

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = {
            dataSize,
            readWriteRatio,
            taskType,
            speedRequirement,
            cacheUsage,
            ioPriority,
        };

        setLoading(true);  // 요청 시작 시 로딩 상태 설정
        setError(null);     // 오류 초기화

        try {
            const res = await fetch('http://127.0.0.1:5000/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
            }

            const result: ServerResponse = await res.json();
            setResponse(result);
        } catch (err: any) {
            setError(err.message);
            setResponse(null);
        } finally {
            setLoading(false);  // 요청 완료 후 로딩 상태 해제
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>데이터 크기 (예: 500M, 1G): </label>
                    <input
                        type="text"
                        value={dataSize}
                        onChange={(e) => setDataSize(e.target.value)}
                        placeholder="500M, 1G 등"
                    />
                </div>

                <div>
                    <label>읽기/쓰기 비율 (예: 70% 읽기, 30% 쓰기): </label>
                    <input
                        type="text"
                        value={readWriteRatio}
                        onChange={(e) => setReadWriteRatio(e.target.value)}
                        placeholder="예: 70/30"
                    />
                </div>

                <div>
                    <label>작업 유형: </label>
                    <select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
                        <option value="순차">순차</option>
                        <option value="랜덤">랜덤</option>
                    </select>
                </div>

                <div>
                    <label>처리 속도 요구 사항: </label>
                    <select value={speedRequirement} onChange={(e) => setSpeedRequirement(e.target.value)}>
                        <option value="고속">고속</option>
                        <option value="보통">보통</option>
                        <option value="저속">저속</option>
                    </select>
                </div>

                <div>
                    <label>캐시 사용 여부: </label>
                    <input
                        type="checkbox"
                        checked={cacheUsage}
                        onChange={(e) => setCacheUsage(e.target.checked)}
                    />
                    <span>{cacheUsage ? "활성화" : "비활성화"}</span>
                </div>

                <div>
                    <label>I/O 스케줄링 우선순위: </label>
                    <select value={ioPriority} onChange={(e) => setIoPriority(e.target.value)}>
                        <option value="처리량 우선">처리량 우선</option>
                        <option value="지연 시간 최소화">지연 시간 최소화</option>
                    </select>
                </div>

                <button type="submit">최적화 요청</button>
            </form>
            {/* 로딩 상태일 때 표시 */}
            {loading && <p>로딩 중...</p>}
            {/* 서버 응답 결과 표시 */}
            {response && (
                <div className="response">
                    <h2>최적화 결과</h2>
                    <p><strong>예상 IOPS:</strong> {response.predicted_iops}</p>
                    <p><strong>최적화된 설정:</strong></p>
                    <ul>
                        <li>데이터 크기: {response.optimized_settings.dataSize}</li>
                        <li>읽기/쓰기 비율: {response.optimized_settings.readWriteRatio}</li>
                        <li>작업 유형: {response.optimized_settings.taskType}</li>
                        <li>캐시 사용: {response.optimized_settings.cacheUsage ? '활성화' : '비활성화'}</li>
                        <li>I/O 우선순위: {response.optimized_settings.ioPriority}</li>
                    </ul>
                    <p><strong>추천 사항:</strong></p>
                    <ul>
                        {response.recommendations ? (
                            response.recommendations.map((rec: string, index: number) => (
                                <li key={index}>{rec}</li>
                            ))
                        ) : (
                            <li>추천 사항이 없습니다.</li>
                        )}
                    </ul>
                </div>
            )}


            {/* 오류 메시지 표시 */}
            {error && <div className="error">오류: {error}</div>}
        </div>
    );
};

export default InputForm;
