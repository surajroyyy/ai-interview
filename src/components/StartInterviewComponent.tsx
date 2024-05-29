import React, { useState } from 'react';
import axios from 'axios';


const StartInterviewComponent = () => {
    const handleClick = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/interviews/start');
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