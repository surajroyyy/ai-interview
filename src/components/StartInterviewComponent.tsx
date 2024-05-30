import React, { useState } from 'react';
import axios from 'axios';
import "../index.css"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/";

interface StartButtonProps {
    onStart: (sessionId: string) => void;
}

const StartInterviewComponent: React.FC<StartButtonProps> = ({onStart}) => {
    const handleClick = async () => {
        try {
            const response = await axios.post(API_URL + 'api/interviews/start');
            const sessionId = response.data.session_id
            onStart(sessionId)
        } catch (error) {
            console.log('Issue starting the interview', error)
        }
    };

    return (
        <div>
            <button className="begin-interview" onClick={handleClick} type="button">
                Begin
            </button>
        </div>
    )
};

export default StartInterviewComponent;