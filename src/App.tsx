import React, { useState } from 'react';
import './App.css';
import './index.css'
import RecordingComponent from './components/RecordingComponent';
import StartInterviewComponent from './components/StartInterviewComponent';
import EndButtonComponent from './components/EndInterviewComponent';
import ChatComponent from './components/ChatComponent';

function App() {

  const [sessionId, setSessionid] = useState<string | null>(null);
  const [endSession, setEndSession] = useState<string | null>(null)

  const handleStart = (id: string) => {
    setSessionid(id)
  }

  const handleEnd = (status: string) => {
    setEndSession(status)
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
            {!endSession? (
              <div>
                <RecordingComponent sessionId={sessionId}/>
                <EndButtonComponent onEnd={handleEnd} sessionId={sessionId}/>
                <ChatComponent sessionId={sessionId}/>
              </div>
            ) : (
              <div><h1 className="end-title">Thank you! Your <span className="end-deco">interview</span> is now over.</h1></div>
            )}
            
          </div>
        )}
      </div>
    </div>
  );

}

export default App;
