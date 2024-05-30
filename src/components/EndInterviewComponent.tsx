import React, { useState } from 'react';
import axios from 'axios';

interface EndButtonProps {
    sessionId: string;
}

const EndButtonComponent: React.FC<EndButtonProps> = ({sessionId}) => {
    const handleClick = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/interviews/' + sessionId + '/end');
        } catch (error) {
            console.log('Issue ending the interview', error)
        }
    };

    return (
        <div>
            <button onClick={handleClick} type="button">
                End Interview.
            </button>
        </div>
    )
};

export default EndButtonComponent;