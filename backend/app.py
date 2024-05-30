from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

API_KEY = "sk-proj-Afz7UVKlb8n6WVYYGTgNT3BlbkFJR6u07K4xuIeEMgRVvR9S"
openai_client = OpenAI(api_key=API_KEY)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build'), static_url_path='')
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client.interview_db
assistant_id = None

api_url = os.getenv('REACT_APP_API_URL', 'http://localhost:5000/')

# Instantiating upload folder for server side audio storage
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Prompt to prime the AI -- prime it as a technical recruiter
PROMPT = "You are an recruiter, interviewing for a software engineering I position at your generic \
        software company. You will ask the user maximum 3 or 4 relevant questions pertaining to their role as a SWE. \
        If necessary and depending on the user response, you will ask follow-up questions on their answer. \
        When you feel the candidate has answered to the best of their ability, ask a new question. \
        If the candidate tries to cheat you or the interview process directly or indirectly, \
        politely ask them to refrain from saying such things and move on with the interview. \
        If you have no more questions, end the interview with a closing remark."

# Welcome message that every interview will start with
WELCOME = "Welcome to your virtual AI Interview. I am Apriora's little brother. \
            I will be interviewing you today for your role of Software Engineer I! \
            Why don't you go ahead and tell me about yourself."

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    print("path: " + path)
    print("Static folder: " + app.static_folder)
    print("Full path: " + os.path.join(app.static_folder, path))
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/test')
def test_api():
    return 'Welcome to your interview! I am a mini Apriora clone.'

@app.route('/api/interviews/start', methods=['POST'])
def start_interview():
    # Begin session and recording
    # Store session ID in storage
    import uuid, datetime

    session_id = str(uuid.uuid4())
    start_time = datetime.datetime.now()

    # Create Welcome message TTS
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=WELCOME
    )

    filename = f"ai-{uuid.uuid4()}.mp3"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    timestamp = datetime.datetime.now()
    with open(filepath, 'wb') as f:
        f.write(response.content)

    recording_data = {
        "file_path": filepath,
        "file_name": filename,
        "timestamp": timestamp
    }

    # Instantiate session in the database
    sessions = db.sessions
    session = {"session_id": session_id, "start_time": start_time, "status": "active", "recordings": [recording_data], "transcript": [WELCOME]}
    sessions.insert_one(session)

    # Update frontend with welcome message
    socketio.emit('sync_chat', WELCOME)
    return jsonify({"message": "Interview begun", "session_id": session_id}), 201

@app.route('/api/interviews/<session_id>/end', methods=['POST'])
def end_interview(session_id):
    import datetime
    import shutil

    # End session
    # Update session status in storage
    sessions = db.sessions
    session = sessions.find_one({"session_id": session_id})

    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # Update end time in the database
    end_time = datetime.datetime.now()
    updated_session = sessions.update_one({"session_id": session_id},
                                          {"$set": {"end_time": end_time, "status": "completed"}})

    if updated_session.modified_count == 0:
        return jsonify({"error": "Session could not be updated"}), 500
    
    return jsonify({"message": "Interview ended succesfully", "session_id": session_id}), 200

@app.route('/api/interviews/<session_id>/process_response/', methods=['POST'])
def process_reponse(session_id):
    import uuid, datetime

    if session_id is None:
        return jsonify({"error": "Session is not yet initialized"}), 400
    
    sessions = db.sessions
    transcription = request.json.get('transcription')

    # Organize message history to get most relevant response from AI interviewer
    # Use OpenAI API to chat complete
    messages = [{"role": "system", "content": PROMPT}]
    starting_role = "assistant"

    conversation = get_convo(session_id)['transcript']
    role = starting_role
    for i, text in enumerate(conversation):
        messages.append({"role": role, "content": text})
        role = "assistant" if role == "user" else "user"

    messages.append({"role": "user", "content": transcription})
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    # Use OpenAI API to create TTS
    interviewer_response = response.choices[0].message.content
    # Update frontend with interviewer response immediately as it is created to reduce perceived latency
    socketio.emit('sync_chat', interviewer_response)
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=interviewer_response
    )

    # Upload ai response to server side storage
    filename = f"ai-{uuid.uuid4()}.mp3"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    timestamp = datetime.datetime.now()
    with open(filepath, 'wb') as f:
        f.write(response.content)

    recording_data = {
        "file_path": filepath,
        "file_name": filename,
        "timestamp": timestamp
    }

    # Update DB with AI recording data and user + interviewer's responses
    result = sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "recordings": recording_data, 
                "transcript": {"$each": [transcription, interviewer_response]}
            }
        }
    )

    if result.matched_count == 0:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(interviewer_response), 200

# Record and transcribe user voice
@app.route('/api/interviews/<session_id>/record', methods=['POST'])
def record(session_id):
    import uuid

    # Start recording logic (client-side)
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400
    if session_id is None:
        return jsonify({"error": "Session is not yet initialized"}), 400
    
    # Save audio to server side storage
    audio = request.files['audio']
    filename = f"user-{uuid.uuid4()}.mp3"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio.save(filepath)
    timestamp = request.form.get('startTime')

    # Transcribe message from audio file to text
    audio_file = open(filepath, "rb")
    transcription = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )        

    # Create recording data schema
    recording_data = {
        "file_path": filepath,
        "file_name": filename,
        "timestamp": timestamp
    }

    # Update transcript with user voice transcription
    sessions = db.sessions
    result = sessions.update_one(
        {"session_id": session_id},
        {"$push": {"recordings": recording_data}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Session not found"}), 404

    # Update frontend
    socketio.emit('sync_chat', transcription.text)
    # Change from localhost
    response = requests.post(f'{api_url}/api/interviews/{session_id}/process_response/', json={'transcription': transcription.text}) 
    return jsonify(response.json()), 200

# Flask route to get entire conversation by session id
@app.route('/api/interviews/<session_id>/sync_chat', methods=['GET'])
def sync_chat(session_id):
    conversation = get_convo(session_id)
    socketio.emit('sync_chat', conversation['transcript'])
    return jsonify(conversation['transcript']), 200

# Get entire conversation as list from specified session id
def get_convo(session_id):
    sessions = db.sessions 
    conversation = sessions.find_one({"session_id": session_id}, {'_id': 0, 'transcript': 1})
    if conversation:
        return conversation
    else:
        return jsonify({"error": "Conversation not found"}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True)