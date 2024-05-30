import React, { useEffect, useState } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import "../index.css"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/";

interface ChatComponentProps {
    sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({sessionId}) => {
    const [conversation, setConversation] = useState<string[]>([]);

    useEffect(() => {
        const socket = io(API_URL);
        socket.on('sync_chat', (data) => {
            if (conversation.length == 0) {
                setConversation([data])
            } else {
                setConversation(prev => [...prev, data]);
            }
        });

        // axios.get(API_URL + 'interviews/' + sessionId + '/sync_chat')
        //     .then(response => setConversation(response.data))
        //     .catch(error => console.error('Error fetching conversation:', error));

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