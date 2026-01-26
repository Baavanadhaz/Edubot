import os
import base64
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
from dotenv import load_dotenv
import google.generativeai as genai
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
from elevenlabs.client import ElevenLabs
from db_manager import add_message, get_conversation, init_db

load_dotenv()

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# --- CLIENT INITIALIZATION ---
try:
    config = DeepgramClientOptions(verbose=0)
    deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
except Exception as e:
    print(f"ERROR: Could not initialize API clients. Check your .env file. Details: {e}")

# --- DATABASE INITIALIZATION ---
with app.app_context():
    init_db()

# --- HELPER FUNCTIONS ---
def generate_elevenlabs_audio(text):
    """Generates audio from text using ElevenLabs and returns the bytes."""
    audio_stream = elevenlabs_client.text_to_speech.stream(
        text=text,
        voice_id="IKne3meq5aSn9XLyUdCD",
        model_id="eleven_multilingual_v2"
    )
    return b"".join(audio_stream)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admissions')
def admissions():
    return render_template('admissions.html')

@app.route('/academics')
def academics():
    return render_template('academics.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/greet', methods=['POST'])
def greet():
    try:
        greeting_text = "Hello! I am Edubot! The voice assistant of Skadoosh University. How can I help you today?"
        audio_bytes = generate_elevenlabs_audio(greeting_text)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({'text': greeting_text, 'audio': audio_base64})
    except Exception as e:
        print(f"Error in /greet endpoint: {e}")
        return jsonify({'error': f"Error generating greeting: {e}"}), 500

@app.route('/respond', methods=['POST'])
def respond():
    """Handles the LLM and TTS part, receiving transcribed text."""
    data = request.get_json()
    user_input = data.get('text')
    session_id = data.get('session_id')

    if not user_input or not session_id:
        return jsonify({'error': 'Missing text or session_id'}), 400

    add_message(session_id, 'user', user_input)

    try:
        system_prompt = (
            "## Core Identity & Persona ##\n"
            "You are 'EduBot', the official voice assistant for Skadoosh University (SKDU). Your persona is professional, friendly, enthusiastic, and exceptionally helpful. Your goal is to be the most trustworthy first point of contact for prospective students.\n\n"

            "## Factual Knowledge Base ##\n"
            "This is your single source of truth. Base all your answers on these facts. Do not add or invent information not present here.\n"
            "- **University Name:** Skadoosh University (SKDU)\n"
            "- **Location:** Juniper City. It's a picturesque campus known for its beautiful architecture and tranquil learning environment.\n"
            "- **Key Programs:** World-renowned programs in Martial Arts, Philosophy, Inner Peace Studies, Digital Arts, Sustainable Agriculture, and Calligraphy. We also have growing faculties in Digital Arts and Sustainable Agriculture.\n"
            "- **Admissions Deadline:** The application deadline for the Fall semester is March 15th.\n"
            "- **Contact Information:** The main admissions office can be reached at admissions@skdu.edu via email or 9876-543-210 via phone.\n"
            "- **Unique Selling Proposition:** SKDU is unique for its 'Mentorship of Masters' program, where every student is paired with a seasoned master in their field for one-on-one guidance throughout their studies.\n\n"

            "## Guiding Principles & Mission ##\n"
            "1. **Prioritize Helpfulness:** Your main goal is to answer the user's questions clearly, accurately and concisely (less than 30 words per response) using the Factual Knowledge Base.\n"
            "2. **Be Conversational:** Do not just recite facts. Weave the information from your Knowledge Base into natural, conversational language.\n"
            "3. **Execute the Lead Capture Protocol:** After providing value by answering a question, your secondary goal is to help interested students connect with our team. Offer to send a brochure or arrange a call in exchange for their email or phone number. Handle refusal gracefully.\n\n"

            "## Protocol for Unknown Information (CRITICAL) ##\n"
            "This is the most important rule. If a user asks a question that CANNOT be answered from your 'Factual Knowledge Base' (e.g., 'What are the gym hours?', 'Do you have a swimming team?', 'What's the student-faculty ratio?'), you MUST follow this three-step process:\n"
            "1. **Acknowledge and Validate:** Positively acknowledge their question. (e.g., 'That's a great question about the specific campus facilities.')\n"
            "2. **State Your Limitation Honestly:** Clearly state that you do not have that specific detail. This builds trust. (e.g., 'I don't have the exact student-faculty ratio in my current information.')\n"
            "3. **Redirect to the Official Source:** Immediately provide a helpful, truthful next step by directing them to the experts. (e.g., 'For the most accurate and up-to-date details on that, the best thing to do is email our admissions team at admissions@skdu.edu. They have all that information and can answer your question fully.')\n"
            "**Under no circumstances should you invent, guess, or use placeholders like '[Insert Information Here]'. Always follow the Acknowledge-State-Redirect protocol.**"
        )
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )
        
        conversation_history = get_conversation(session_id)
        chat_history = [{'role': msg['role'], 'parts': [msg['content']]} for msg in conversation_history]
        chat = model.start_chat(history=chat_history[:-1])
        response = chat.send_message(user_input)
        llm_response = response.text
        add_message(session_id, 'model', llm_response)
    except Exception as e:
        print(f"Error in Gemini LLM: {e}")
        return jsonify({'error': f"Error with Gemini: {e}"}), 500

    try:
        audio_bytes = generate_elevenlabs_audio(llm_response)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({
            'ai_text': llm_response,
            'ai_audio': audio_base64
        })
    except Exception as e:
        print(f"Error in Elevenlabs TTS: {e}")
        return jsonify({'error': f"Error with Elevenlabs: {e}"}), 500

# --- WEBSOCKET ROUTE FOR LIVE TRANSCRIPTION ---
@sock.route('/listen')
def listen(ws): # CORRECTED: Removed 'async'
    """
    Handles the WebSocket connection using Deepgram's synchronous streaming client.
    """
    dg_connection = None
    try:
        # CORRECTED: Use the synchronous 'live' client, not 'asynclive'
        dg_connection = deepgram.listen.websocket.v("1")

        def on_message(self, result, **kwargs):
            transcript = result.channel.alternatives[0].transcript
            if len(transcript) > 0:
                # This callback is run in a background thread by the SDK.
                # It sends the transcript back to the client.
                ws.send(json.dumps({"transcript": transcript, "is_final": result.is_final}))
        
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2", language="en-US", smart_format=True,
            encoding="linear16", channels=1, sample_rate=16000,
            interim_results=True, endpointing=300,
        )
        
        # This starts the connection and background threads. It does not block.
        dg_connection.start(options)

        # This loop receives audio from the client and sends it to Deepgram.
        # It's the main blocking part of this function.
        while True:
            data = ws.receive()
            if data:
                dg_connection.send(data)
            else:
                break # Client closed connection

    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        # Ensure the Deepgram connection and its threads are cleanly closed.
        if dg_connection:
            dg_connection.finish()

if __name__ == '__main__':
    app.run(debug=True, port=5001)