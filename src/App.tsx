import React from 'react';
import logo from './logo.svg';
import './App.css';
import RecordingComponent from './components/RecordingComponent';
import StartInterviewComponent from './components/StartInterviewComponent';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Welcome to your</h1>
        <h1>Interview</h1>
      </header>
      <body>
        <StartInterviewComponent/>
        <RecordingComponent/>
      </body>
    </div>
  );
}

export default App;
