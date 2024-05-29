from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://localhost:27017/')
db = client.interview_db

@app.route('/')
def home():
    return 'Welcome to your interview! I am a mini Apriora clone.'

@app.route('/api/interviews/start', methods=['POST'])
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

@app.route('/api/interviews/<session_id>/end', methods=['POST'])
def end_interview(session_id):
    import datetime
    # End session
    # Update session status in storage
    sessions = db.sessions
    session = sessions.find_one({"session_id": session_id})

    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    end_time = datetime.datetime.now()
    updated_session = sessions.update_one({"session_id": session_id},
                                          {"$set": {"end_time": end_time, "status": "completed"}})

    if updated_session.modified_count == 0:
        return jsonify({"error": "Session could not be updated"}), 500

    return jsonify({"message": "Interview ended succesfully", "session_id": session_id}), 200

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/interviews/<session_id>/record/', methods=['POST'])
def record(session_id):
    import uuid
    # Start recording logic (client-side)
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400
    
    audio = request.files['audio']
    filename = f"audio-{uuid.uuid4()}.mp3"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio.save(filepath)

    timestamp = request.form.get('startTime')

    recording_data = {
        "file_path": filepath,
        "file_name": filename,
        "timestamp": timestamp
    }

    sessions = db.sessions
    result = sessions.update_one(
        {"session_id": session_id},
        {"$push": {"recordings": recording_data}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Session not found"}), 404

    return jsonify({"message": "Recording saved successfully", "file_path": filepath, "session_id": session_id}), 200

# @app.route('/api/interviews/<session_id>/record/stop', methods=['POST'])
# def stop_recording(session_id):
#     # Stop recording logic (client-side)
#     # Store recordings in storage (MongoDB)
#     return jsonify({"message": "Recording ended", "session_id": session_id}), 200

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