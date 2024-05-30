import React, { useState } from 'react';
import axios from 'axios';
import '../index.css'

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/";

interface EndButtonProps {
    sessionId: string;
    onEnd: (isDone: string) => void;
}

const EndButtonComponent: React.FC<EndButtonProps> = ({sessionId, onEnd}) => {
    const handleClick = async () => {
        try {
            await axios.post(API_URL + 'api/interviews/' + sessionId + '/end');
            onEnd("Finished")
        } catch (error) {
            console.log('Issue ending the interview', error)
        }
    };

    return (
        <div>
            <button className="end-interview" onClick={handleClick} type="button">
                End Session
            </button>
        </div>
    )
};

export default EndButtonComponent;