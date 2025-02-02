from flask import Flask, request, jsonify, send_from_directory , render_template
from pathlib import Path
import subprocess
import whisper
import json
import os
import ollama
import json
from datetime import datetime
from typing import Dict, List
import ollama
import logging
from pathlib import Path
import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
from rich import print as rprint
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import track
import wave
import time
import subprocess
import sys
import os

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Set up directories for file uploads and summaries
UPLOAD_FOLDER = 'uploads'
SUMMARY_FOLDER = 'summaries'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

# Load Whisper model (once, for efficiency)
audio_model = whisper.load_model("base")

def generate_summary(text):
    logging.debug(f"Generating summary for text: {text[:100]}...")  # Log the first 100 characters
    response = ollama.chat(
        model="tinyllama",  # Use your preferred model
        messages=[{"role": "user", "content": f"Summarize this text:\n\n{text}"}]
    )
    summary = response["message"]["content"]
    logging.debug(f"Summary generated: {summary}")  # Log the generated summary
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload the MP3 or TXT file and return the path to the saved file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file.filename.endswith('.mp3') or file.filename.endswith('.txt'):
        # Save the file
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        if file.filename.endswith('.txt'):
            content = file.read().decode('utf-8')
            # Process the content of the txt file
            return jsonify({"message": "TXT file uploaded successfully", "filepath": filepath, "content": content})
        else:
            return jsonify({"message": "File uploaded successfully", "filepath": filepath})
    elif request.form.get('pasted_text'):
        pasted_text = request.form['pasted_text']
        # Process the pasted text
        return jsonify({"message": "Pasted text processed successfully", "pasted_text": pasted_text})
    else:
        return jsonify({"error": "Only MP3 and TXT files are supported"})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe the uploaded audio file."""
    data = request.json
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Invalid file path"})
    
    if filepath.endswith('.mp3'):
        result = audio_model.transcribe(filepath)
        transcription = result['text']
        
        return jsonify({"transcription": transcription})
    elif filepath.endswith('.txt'):
        with open(filepath, 'r') as f:
            transcription = f.read()
        
        return jsonify({"transcription": transcription})
    else:
        return jsonify({"error": "Only MP3 and TXT files are supported"})

@app.route('/summarize', methods=['POST'])
def summarize():
    """Generate a summary for the given transcript."""
    data = request.json
    transcript = data.get('transcript')
    filepath = data.get('filepath')
    
    if not transcript and not filepath:
        return jsonify({"error": "No transcript or file path provided"})
    
    if filepath:
        if filepath.endswith('.txt'):
            with open(filepath, 'r') as f:
                content = f.read()
                # Generate a summary for the content
                summary = generate_summary(content)
                return jsonify({"summary": summary})
        elif filepath.endswith('.mp3'):
            result = audio_model.transcribe(filepath)
            transcription = result['text']
            summary = generate_summary(transcription)
            return jsonify({"summary": summary})
    elif transcript:
        summary = generate_summary(transcript)
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Only MP3 and TXT files are supported"})

@app.route('/paste_text', methods=['POST'])
def paste_text():
    """Process the pasted text."""
    pasted_text = request.form['pasted_text']
    # Generate a summary for the pasted text
    summary = generate_summary(pasted_text)
    return jsonify({"message": "Pasted text processed successfully", "pasted_text": pasted_text, "summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
