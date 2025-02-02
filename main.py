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

class MeetingSummarizer:
    def __init__(self, model_name: str = "tinyllama"):
        """Initialize the meeting summarizer with specified model."""
        self.model_name = model_name
        self.setup_logging()
        self.console = Console()
        
        # Verify system requirements
        self.verify_requirements()
        
    def verify_requirements(self):
        """Verify that all required components are available."""
        try:
            # Check FFmpeg
            result = subprocess.run(['ffmpeg', '-version'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.console.print("❌ FFmpeg not found! Please install FFmpeg first.", 
                                 style="bold red")
                sys.exit(1)
                
            # Initialize Whisper model
            self.console.print("🔄 Loading Whisper model...", style="bold yellow")
            self.audio_model = whisper.load_model("base")
            self.console.print("✓ Whisper model loaded", style="bold green")
            
            # Check Ollama
            try:
                ollama.list()
                self.console.print("✓ Ollama connection successful", style="bold green")
            except Exception as e:
                self.console.print("❌ Ollama not running or not installed!", 
                                 style="bold red")
                sys.exit(1)
                
        except FileNotFoundError:
            self.console.print(
                "\n❌ Error: FFmpeg not found! Please install FFmpeg:\n"
                "1. Download from https://www.gyan.dev/ffmpeg/builds/\n"
                "2. Extract and add to PATH\n"
                "   OR\n"
                "3. Run: choco install ffmpeg (if using Chocolatey)",
                style="bold red"
            )
            sys.exit(1)
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def record_audio(self, duration: int = None) -> str:
        """Record audio from microphone."""
        sample_rate = 16000
        self.console.print("\n🎤 Recording... Press Ctrl+C to stop", style="bold red")
        
        try:
            recordings_dir = Path("recordings")
            recordings_dir.mkdir(exist_ok=True)
            
            if duration:
                # Record for specified duration
                recording = sd.rec(int(duration * sample_rate), 
                                samplerate=sample_rate, channels=1)
                sd.wait()
            else:
                # Record until interrupted
                recording = []
                with sd.InputStream(samplerate=sample_rate, channels=1) as stream:
                    while True:
                        chunk, overflowed = stream.read(sample_rate)
                        recording.extend(chunk)
                        
        except KeyboardInterrupt:
            self.console.print("\n⏹️ Recording stopped", style="bold green")
        except Exception as e:
            self.console.print(f"\n❌ Recording error: {str(e)}", style="bold red")
            raise
            
        # Save recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = recordings_dir / f"meeting_audio_{timestamp}.wav"
        
        try:
            if duration:
                sf.write(str(filename), recording, sample_rate)
            else:
                sf.write(str(filename), np.array(recording), sample_rate)
            
            self.console.print(f"✓ Audio saved to {filename}", style="bold green")
            return str(filename)
            
        except Exception as e:
            self.console.print(f"\n❌ Error saving audio: {str(e)}", style="bold red")
            raise

    def transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio file to text using Whisper."""
        try:
            self.console.clear()  # Clear the console
            
            self.console.print("\n🔄 Transcribing audio...", style="bold yellow")
            
            # Verify audio file exists
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Verify file is readable
            try:
                with sf.SoundFile(audio_file) as f:
                    pass
            except Exception as e:
                raise ValueError(f"Invalid audio file: {str(e)}")
            
            result = self.audio_model.transcribe(audio_file)
            
            self.console.print("✓ Transcription complete", style="bold green")
            return result["text"]
            
        except Exception as e:
            self.console.print(f"\n❌ Transcription error: {str(e)}", style="bold red")
            raise


    def generate_summary(self, transcript: str) -> Dict[str, str]:
        try:
            self.console.print("\n🔄 Generating summary...", style="bold yellow")

            # Call Ollama's AI model to generate the summary
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": f"Summarize this meeting transcript:\n\n{transcript}"}]
            )

            summary_text = response["message"]["content"]

            self.console.print("✓ Summary generated", style="bold green")
            return {"summary": summary_text}

        except Exception as e:
            self.console.print(f"\n❌ Summary generation error: {str(e)}", style="bold red")
            raise

    def save_summary(self, summary_data: Dict[str, str]):
        try:
            summaries_dir = Path("summaries")
            summaries_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = summaries_dir / f"summary_{timestamp}.json"

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=4)

            self.console.print(f"✓ Summary saved to {summary_file}", style="bold green")

        except Exception as e:
            self.console.print(f"\n❌ Error saving summary: {str(e)}", style="bold red")
            raise


def main():
    console = Console()
    
    try:
        # ASCII art header
        console.print("""
        📝 Meeting Summarizer 3000 📝
        ----------------------------
        """, style="bold blue")
        
        # Initialize summarizer with small model
        summarizer = MeetingSummarizer(model_name="tinyllama")
        
        # Mode selection
        mode = Prompt.ask(
            "Choose mode",
            choices=["audio", "text"],
            default="text"
        )
        
        if mode == "audio":
            input_type = Prompt.ask(
                "Choose input method",
                choices=["record", "upload"],
                default="record"
            )

            if input_type == "record":
                duration_choice = Prompt.ask(
                    "Recording mode",
                    choices=["timed", "manual"],
                    default="manual"
                )

                if duration_choice == "timed":
                    duration = int(Prompt.ask("Enter recording duration in seconds", default="300"))
                    audio_file = summarizer.record_audio(duration=duration)
                else:
                    audio_file = summarizer.record_audio()
            
            else:  # upload MP3
                audio_file = Prompt.ask("Enter path to your MP3 file")

                # Convert MP3 to WAV (since Whisper prefers WAV)
                converted_wav = f"{Path(audio_file).stem}.wav"
                subprocess.run(["ffmpeg", "-i", audio_file, converted_wav, "-y"], check=True)
                audio_file = converted_wav

            # Now transcribe the audio file
            transcript = summarizer.transcribe_audio(audio_file)
        
        else:
            # Text input mode
            console.print("\nEnter/paste your meeting transcript (Ctrl+D or Ctrl+Z on Windows to finish):")
            transcript_lines = []
            try:
                while True:
                    line = input()
                    transcript_lines.append(line)
            except EOFError:
                transcript = '\n'.join(transcript_lines)

        # Generate and save summary with loading animation
        summary_data = summarizer.generate_summary(transcript)
        summarizer.save_summary(summary_data)

        
        # Display summary
        console.print("\n📊 Summary:", style="bold green")
        console.print(summary_data["summary"])
        
    except KeyboardInterrupt:
        console.print("\n\n⚠️ Program interrupted by user", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="bold red")
        logging.exception("An error occurred")
    finally:
        console.print("\n👋 Thank you for using Meeting Summarizer!", style="bold blue")

if __name__ == "__main__":
    main()
