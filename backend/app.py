from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.interview_db

@app.route('/')
def home():
    return 'Welcome to your interview! I am a mini Apriora clone.'

@app.route('api/interviews', methods=['POST'])
def start_interview():
    # Begin session and recording
    # Store session ID in storage
    import uuid, datetime
    session_id = str(uuid.uuid4())
    start_time = datetime.datetime.now()

    sessions = db.sessions
    session = {"session_id": session_id, "start_time": start_time, "status": "active"}
    sessions.insert_one(session)

    return jsonify({"message": "Interview begun", "session_id": session_id}), 201

@app.route('api/interviews/<session_id>/end', methods=['POST'])
def end_interview(session_id):
    import datetime
    # End session
    # Update session status in storage

    sessions = db.sessions
    session = sessions.find_one({"session_id": session_id},
                                {"$set": {"end_time": end_time, "status": "completed"}})

    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    end_time = datetime.datetime.now()
    updated_session = sessions.update_one({"session_id": session_id})

    if updated_session.modified_count == 0:
        return jsonify({"error": "Session could not be updated"}), 500

    return jsonify({"message": "Interview ended succesfully", "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/record/start', methods=['POST'])
def start_recording(session_id):
    # Start recording logic (client-side)
    return jsonify({"message": "Recording begun", "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/record/stop', methods=['POST'])
def stop_recording(session_id):
    # Stop recording logic (client-side)
    # Store recordings in storage (MongoDB)
    return jsonify({"message": "Recording ended", "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/process', methods=['POST'])
def process_recording(session_id):
    # Send audio file for transcription
    transcription = ""
    return jsonify({"transcription": transcription, "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/response', methods=['POST'])
def ai_response(session_id):
    # Fetch OpenAI reponse from key
    ai_response = ""
    return jsonify({"ai_response": ai_response, "session_id": session_id}), 200

if __name__ == '__main__':
    app.run(debug=True)