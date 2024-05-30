import React, { useEffect, useState } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import "../index.css"

interface ChatComponentProps {
    sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({sessionId}) => {
    const [conversation, setConversation] = useState<string[]>([]);

    useEffect(() => {
        const socket = io('http://localhost:5000');
        socket.on('sync_chat', (data) => {
            setConversation(prev => [...prev, data]);
        });

        // axios.get('http://localhost:5000/api/interviews/' + sessionId + '/sync_chat')
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