import React, { useEffect, useState } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import "../index.css"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/";
const WELCOME = "Welcome to your virtual AI Interview. I am Apriora's little brother. \
            I will be interviewing you today for your role of Software Engineer I! \
            Why don't you go ahead and tell me about yourself."

interface ChatComponentProps {
    sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({sessionId}) => {
    const [conversation, setConversation] = useState<string[]>([WELCOME]);

    useEffect(() => {
        const socket = io(API_URL);
        socket.on('sync_chat', (data) => {
            setConversation(prev => [...prev, data]);
        });
        axios.get(API_URL + 'interviews/' + sessionId + '/sync_chat')
            .then(response => setConversation(response.data))
            .catch(error => console.error('Error fetching conversation:', error));

        return () => {socket.off('sync_chat')};
    }, [sessionId]);


    return (
        <div className="messages-container">
            {conversation.map((entry, index) => (
                <div key={index} className={`message ${index % 2 === 0 ? 'user' : 'interviewer'}`}>
                    {entry}
                </div>
            ))}
        </div>
    )
}

export default ChatComponent