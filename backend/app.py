from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from openai import OpenAI
import os
import requests

API_KEY = "sk-proj-Afz7UVKlb8n6WVYYGTgNT3BlbkFJR6u07K4xuIeEMgRVvR9S"
openai_client = OpenAI(api_key=API_KEY)

app = Flask(__name__)
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins='*')
client = MongoClient('mongodb://localhost:27017/')
db = client.interview_db
assistant_id = None

PROMPT = "You are an interviewer for a software engineering I position. \
            You will ask the user relevant questions pertaining to their role as SWE. \
            If necessary and depending on the user response, you will ask follow-up questions on their answer. \
            When you feel the candidate has answered to the best of their ability, ask a new question. \
            Ensure you don't repeat questions. \
            If you have no more questions, end the interview with a closing remark."

WELCOME = "Welcome to your virtual AI Interview. I am Apriora's little brother. \
            I will be interviewing you today for your role of Software Engineer I! \
            Why don't you go ahead and tell me about yourself."

@app.route('/')
def home():
    return 'Welcome to your interview! I am a mini Apriora clone.'

def create_interviewer():
    response = openai_client.beta.assistants.create(
        model="gpt-4o",
        instructions=PROMPT,
        tools=[{"type": "code_interpreter"}]
    )
    return response.id

@app.route('/api/interviews/start', methods=['POST'])
def start_interview():
    # Begin session and recording
    # Store session ID in storage
    import uuid, datetime
    # global assistant_id

    session_id = str(uuid.uuid4())
    # assistant_id = create_interviewer()
    start_time = datetime.datetime.now()

    sessions = db.sessions
    session = {"session_id": session_id, "start_time": start_time, "status": "active", "transcript": [WELCOME]}
    sessions.insert_one(session)

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
    
    end_time = datetime.datetime.now()
    updated_session = sessions.update_one({"session_id": session_id},
                                          {"$set": {"end_time": end_time, "status": "completed"}})

    if updated_session.modified_count == 0:
        return jsonify({"error": "Session could not be updated"}), 500
    
    # # Remove uploads folder and data
    # try:
    #     folder_path = 'backend/uploads'
    #     shutil.rmtree(folder_path)
    # except:
    #     print('Folder could not be deleted')
    
    return jsonify({"message": "Interview ended succesfully", "session_id": session_id}), 200

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/interviews/<session_id>/process_response/', methods=['POST'])
def process_reponse(session_id):
    if session_id is None:
        return jsonify({"error": "Session is not yet initialized"}), 400
    
    sessions = db.sessions
    transcription = request.json.get('transcription')

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
        messages=messages,
    )

    interviewer_response = response.choices[0].message.content
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="fable"
    )
    
    result = sessions.update_one(
        {"session_id": session_id},
        {"$push": {"transcript": {"$each": [transcription, interviewer_response]}}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Session not found"}), 404
    
    socketio.emit('sync_chat', interviewer_response)
    return jsonify(interviewer_response), 200

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
    filename = f"audio-{uuid.uuid4()}.mp3"
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

    socketio.emit('sync_chat', transcription.text)
    response = requests.post(f'http://localhost:5000/api/interviews/{session_id}/process_response/', json={'transcription': transcription.text})
    return jsonify(response.json()), 200

@app.route('/api/interviews/<session_id>/sync_chat', methods=['GET'])
def sync_chat(session_id):
    conversation = get_convo(session_id)
    socketio.emit('sync_chat', conversation['transcript'])
    return jsonify(conversation['transcript']), 200

def get_convo(session_id):
    sessions = db.sessions 
    conversation = sessions.find_one({"session_id": session_id}, {'_id': 0, 'transcript': 1})
    if conversation:
        return conversation
    else:
        return jsonify({"error": "Conversation not found"}), 404


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
    socketio.run(app, debug=True)