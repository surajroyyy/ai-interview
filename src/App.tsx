import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';
import './index.css'
import RecordingComponent from './components/RecordingComponent';
import StartInterviewComponent from './components/StartInterviewComponent';
import EndButtonComponent from './components/EndInterviewComponent';
import ChatComponent from './components/ChatComponent';

function App() {

  const [sessionId, setSessionid] = useState<string | null>(null);

  const handleStart = (id: string) => {
    setSessionid(id)
  }

  return (
    <div className="App">
      <header>
        <h1 className="title">Welcome to your <span className="interview">Interview</span></h1>
      </header>
      <div className="content">
        {!sessionId? (
          <StartInterviewComponent onStart={handleStart}/>
        ) : (
          <div>
            <RecordingComponent sessionId={sessionId}/>
            <EndButtonComponent sessionId={sessionId}/>
            <ChatComponent sessionId={sessionId}/>
          </div>
        )}
      </div>
    </div>
  );

}

export default App;
