import React, { useEffect, useState } from 'react';
import {usePubNub } from 'pubnub-react';
// import io from 'socket.io-client';
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
    const pubnub = usePubNub();

    // useEffect(() => {
    //     const url = window.location.origin
    //     console.log(url)
    //     const socket = io(url);
    //     socket.on('sync_chat', (data) => {
    //         setConversation(prev => [...prev, data]);
    //     });

    //     return () => {socket.off('sync_chat')};
    // }, [sessionId]);
    
    useEffect(() => {
        pubnub.subscribe({ channels: ['socket'] });
        pubnub.addListener({
          message: (event) => {
            console.log("PubNub Frontend: " + event.message)
            setConversation((msgs) => [...msgs, event.message]);
          }
        });
    
        return () => {
          pubnub.unsubscribeAll();
        };
      }, []);

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