import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ChatComponentProps {
    sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({sessionId}) => {
    const [conversation, setConversation] = useState([])

    useEffect(() => {
        axios.get('http://localhost:5000/api/interviews/' + sessionId + '/get_conversation')
        .then(response => response.data)
        .then(data => setConversation(data))
        .catch(error => console.error('Error fetching conversation:', error))
    }, [sessionId])

    return (
        <div>
            {conversation.map((entry, index) => (
                <div key={index} className={`message ${index % 2 === 0 ? 'user' : 'interviewer'}`}>
                    {entry}
                </div>
            ))}
        </div>
    )
}

export default ChatComponent