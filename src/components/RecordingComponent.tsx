import React, { useState } from 'react';
import { ReactMic } from 'react-mic';
import axios from 'axios';
import "../index.css"

interface RecordingComponentProps {
    sessionId: string;
}

const RecordingComponent: React.FC<RecordingComponentProps> = ({sessionId}) => {
    const [record, setRecord] = useState(false);
    const [blobURL, setBlobURL] = useState('');
    const [startTime, setStartTime] = useState<string | null>(null)
  
    const startRecording = () => {
      setRecord(true);
      const currentTime = new Date();
      setStartTime(currentTime.toISOString());
    };
  
    const stopRecording = () => {
      setRecord(false);
    };
  
    const onStop = (recordedBlob: any) => {
      setBlobURL(recordedBlob.blobURL);
      // Send the audio blob to the backend
      const formData = new FormData();
      formData.append('audio', recordedBlob.blob, 'recording.wav');
      formData.append('startTime', startTime || '')
      axios.post('http://localhost:5000/api/interviews/' + sessionId + '/record', formData)
        .then(response => {
          console.log('Audio file successfully sent to the server', response.data);
          console.log("startTime: ", startTime);
        })
        .catch(error => {
          console.error('Error sending audio file to the server', error);
        });
    };
  
    return (
      <div className="recorder-container">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>
        <button className="start-recording" onClick={startRecording} type="button">
          <i className="fas fa-microphone"></i>
        </button>
        <ReactMic
          record={record}
          className="sound-wave"
          onStop={onStop}
          mimeType="audio/wav"
          strokeColor="#ffffff"
          backgroundColor="#FF7F50" />
        <button className="stop-recording" onClick={stopRecording} type="button">
          <i className="fas fa-stop"></i>
        </button>
        </div>
    );
  };
  
  export default RecordingComponent;