# Apriora Mini-Clone

Welcome to your AI Interview!

## System Design
I first tackled the project with a high-level system design understanding of what I need to do. I broke down my problem into its most basic components. Obviously I would need:

- Frontend (UI)
- Custom API routes (Communication between front and backend)
- Websocket Connection (Real-time updates on frontend)
- Database (Storage of all relevant data)
- OpenAI API Integration

## Implementation
I began my implementation by writing out basic API calls I would need (ex. POST /start-interview, POST /end-interview, POST /record, POST /process-answer, etc.). As I slowly implemented these and tested them through curl, I began working on a very basic front end. I added a start interview button, that would setup the database with the new session ID route to the interview page UI. 

Then I implemented the voice recording feature using the React-mic library. Linked to the MongoDB database, my web-app stores information in the following schema: 

session = {
    session_id: session_id,
    start_time: start_time,
    end_time: end_time,
    recordings: {[
        {
            "file_path": filepath,
            "file_name": filename,
            "timestamp": timestamp
        },
        {
            "file_path": filepath,
            "file_name": filename,
            "timestamp": timestamp
        },...
    ]},
    transcript: [
        "Hello, I am your interviewer. Tell me about yourself",
        "Hi, I am Bob. I am a CS graduate, excited to interview with you!",...
    ]
    status: completed
}

## Things to consider
So, it would be easy to create the side-by-side video replay and live transcript after the interview has ended. Unfortunately, due to time constraints, I was not able to implement this portion. However, I have set myself up to complete it rather quickly if I had more time (as all the voice recordings and timestamps are stored neatly in Mongo). 

## Things I accomplished
- Clean, polished UI
- Recording feature that transcribes user's speech to text
- Live chat log that updates with both candidate and interviewer's responses (less than 3s AI response latency)
- MongoDB database with all information regarding the transcript and audio files per each interview session