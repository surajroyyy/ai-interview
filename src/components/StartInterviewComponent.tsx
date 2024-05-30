import React, { useState } from 'react';
import axios from 'axios';

interface StartButtonProps {
    onStart: (sessionId: string) => void;
}

const StartInterviewComponent: React.FC<StartButtonProps> = ({onStart}) => {
    const handleClick = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/interviews/start');
            const sessionId = response.data.session_id
            onStart(sessionId)
        } catch (error) {
            console.log('Issue starting the interview', error)
        }
    };

    return (
        <div>
            <button onClick={handleClick} type="button">
                Begin Interview!
            </button>
        </div>
    )
};

export default StartInterviewComponent;