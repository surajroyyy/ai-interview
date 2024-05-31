import React, { useState } from 'react';
import './App.css';
import './index.css'
import PubNub from 'pubnub';
import RecordingComponent from './components/RecordingComponent';
import StartInterviewComponent from './components/StartInterviewComponent';
import EndButtonComponent from './components/EndInterviewComponent';
import ChatComponent from './components/ChatComponent';
import { PubNubProvider } from 'pubnub-react';

const pubnub = new PubNub({
  publishKey: 'pub-c-75a10f03-1958-47bd-a5af-5f40b9623158',
  subscribeKey: 'sub-c-9882b2d9-66e1-4299-87aa-075ef1bd0ed7',
  userId: 'apriora'
});

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
        <h1 className="title">Apriora <span className="interview">Mini</span></h1>
      </header>
      <PubNubProvider client={pubnub}>
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
      </PubNubProvider>
    </div>
  );

}

export default App;
