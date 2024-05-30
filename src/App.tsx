import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';
import RecordingComponent from './components/RecordingComponent';
import StartInterviewComponent from './components/StartInterviewComponent';

function App() {

  const [sessionId, setSessionid] = useState<string | null>(null);

  const handleStart = (id: string) => {
    setSessionid(id)
  }

  return (
    <div className="App">
      <header>
        <h1>Welcome to your</h1>
        <h1>Interview</h1>
      </header>
      <body>
        {!sessionId? (
          <StartInterviewComponent onStart={handleStart}/>
        ) : (
          <RecordingComponent sessionId={sessionId}/>
        )}
      </body>
    </div>
  );

}

export default App;
