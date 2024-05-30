import React, { useState } from 'react';
import { ReactMic } from 'react-mic';
import axios from 'axios';

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
      <div>
        <ReactMic
          record={record}
          className="sound-wave"
          onStop={onStop}
          mimeType="audio/wav"
          strokeColor="#000000"
          backgroundColor="#4f6ee0" />
        <div>
          <button onClick={startRecording} type="button">Start</button>
          <button onClick={stopRecording} type="button">Stop</button>
        </div>
        {/* {blobURL && <audio src={blobURL} controls />} */}
      </div>
    );
  };
  
  export default RecordingComponent;