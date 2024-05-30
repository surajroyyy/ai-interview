from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from openai import OpenAI
import os

API_KEY = "sk-proj-Afz7UVKlb8n6WVYYGTgNT3BlbkFJR6u07K4xuIeEMgRVvR9S"
openai_client = OpenAI(api_key=API_KEY)

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
    WELCOME = "Welcome to your virtual AI Interview. I am Apriora's little brother. \
                I will be interviewing you today for your role of Software Engineer I! \
                Why don't you go ahead and tell me about yourself."

    sessions = db.sessions
    session = {"session_id": session_id, "start_time": start_time, "status": "active", "transcript": [WELCOME]}
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

    # Transcribe message from audio file
    audio_file = open(filepath, "rb")
    transcription = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )        

    recording_data = {
        "file_path": filepath,
        "file_name": filename,
        "timestamp": timestamp
    }

    PROMPT = "You are an interviewer for a software engineering I position. \
                You will ask the user relevant questions pertaining to their role as SWE. \
                If necessary and depending on the user response, you will ask follow-up questions on their answer."

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": transcription.text}
        ]
    )

    interviewer_response = completion.choices[0].message.content

    sessions = db.sessions
    result = sessions.update_one(
        {"session_id": session_id},
        {"$push": {"recordings": recording_data, "transcript": {"$each": [transcription.text, interviewer_response] }}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Session not found"}), 404

    return jsonify({"message": "Recording saved successfully", "file_path": filepath, "timestamp": timestamp, "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/get_conversation', methods=['GET'])
def get_conversation(session_id):
    sessions = db.sessions
    conversation = sessions.find_one({"session_id": session_id}, {'_id': 0, 'transcript': 1})

    if conversation:
        return jsonify(conversation['transcript']), 200
    else:
        return jsonify({"error": "Session not found"}), 404

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