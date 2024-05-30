import React, { useState } from 'react';
import axios from 'axios';
import '../index.css'

interface EndButtonProps {
    sessionId: string;
}

const EndButtonComponent: React.FC<EndButtonProps> = ({sessionId}) => {
    const handleClick = async () => {
        try {
            await axios.post('http://localhost:5000/api/interviews/' + sessionId + '/end');
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