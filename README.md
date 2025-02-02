# Notes Ninja 📝🚀

[HOSTED VERSION](https://goblin-complete-minnow.ngrok-free.app )

A **meeting transcription and summarization tool** powered by **Whisper** for speech-to-text and **Ollama** for AI-generated summaries.

---

## ⚡ Features

- **Speech-to-text conversion** using Whisper
- **AI-generated meeting summaries** using Ollama
- **Supports multiple input methods**: Text, voice, live recording, file upload
- **Processes audio in real-time** (but may be slow due to hardware limitations)
- **Hosted Version**: Accepts MP3/TXT file uploads only.
- **Local Version (`main.py`)**: All features unlocked.

---

## ⚙️ How It Works

1. **Audio Input:**
   - Users can either **record** live audio, **upload** an existing audio file (MP3/WAV), or **paste text**.
   - For audio files, MP3 files are automatically **converted to WAV** using FFmpeg.
   
2. **Speech Recognition:**
   - The recorded/uploaded audio is transcribed using **Whisper (Base model)**.
   
3. **Summarization:**
   - The transcript is sent to **Ollama** (default: `tinyllama`) for AI-generated summaries.
   
4. **Output:**
   - The final summary is **saved as a JSON file**.

---

## 🔧 Setup & Requirements

- **FFmpeg** (required for audio conversion)
- **Whisper** (for speech recognition)
- **Ollama** (for AI-generated summaries)
- **Flask** (for serving the web app)

---

## 🚀 Usage

### Hosted Version
- **Accepts**: MP3 and TXT file uploads.
- **How it works**: Upload an MP3 or TXT file, and it will automatically transcribe and generate a summary.

### Local Version (`main.py`)
- **Full functionality unlocked**:
   - **Text input**: Copy-paste your meeting transcript.
   - **Audio input**: Record live audio, upload an audio file (MP3/WAV), or use the manual/timed recording options.
   
---

## 📌 Limitations

- **No GPU acceleration** → Runs entirely on CPU, which may be slow.
- **Limited file processing** due to hardware constraints.
- **Refresh required before each upload** when using the hosted version.


---

## 🖥️ Technical Overview

### Local Version (`main.py`):
- **Recording Options**: Timed, manual, or file uploads (MP3/WAV).
- **Transcription**: Utilizes **Whisper** for converting audio to text.
- **Summarization**: Uses **Ollama** for generating concise summaries.
- **Web Interface**: Flask-based, supporting file upload, transcription, and summarization.

### Hosted Version (`app.py`):
- **File Upload**: Supports MP3 and TXT file uploads.
- **No Recording**: Limited to file-based input.
- **Transcription & Summarization**: Performs these steps on the server and returns the results.

---

## 🛠️ Key Libraries

- **Whisper**: For transcribing audio to text.
- **Ollama**: For generating AI-based summaries from text.
- **Flask**: For serving the web interface.
- **SoundDevice**: For capturing live audio.
- **Rich**: For displaying stylish logs in the console.
- **FFmpeg**: For audio format conversion (MP3 to WAV).

---

Enjoy using **Notes Ninja** to summarize your meetings efficiently! ⚡
