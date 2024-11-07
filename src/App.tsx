// src/App.tsx
import React from 'react';
import InputForm from './components/InputForm';
import './App.css'; // App 스타일 임포트 (필요시)

const App: React.FC = () => {
    return (
        <div className="App">
            <h1>스토리지 최적화 입력</h1>
            <InputForm />
        </div>
    );
};

export default App;
