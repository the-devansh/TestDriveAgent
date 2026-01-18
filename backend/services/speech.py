import torch
from transformers import pipeline
import soundfile as sf
import os
import io
import numpy as np

class SpeechService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Initialize STT (Whisper)
        self.stt_pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            device=self.device
        )
        
        # Initialize TTS (MMS-TTS)
        # MMS-TTS is fast and high quality for basic needs
        self.tts_pipe = pipeline(
            "text-to-speech",
            model="facebook/mms-tts-eng",
            device=self.device
        )

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text."""
        import soundfile as sf
        audio, sr = sf.read(audio_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Check if audio is basically silent
        if np.abs(audio).max() < 0.01:
            return ""

        result = self.stt_pipe(
            audio, 
            generate_kwargs={"language": "english", "task": "transcribe"}
        )
        return result["text"].strip()

    def synthesize(self, text: str, output_path: str):
        """Synthesize text to audio file."""
        if not text or len(text.strip()) < 2:
            text = "I'm sorry, I didn't catch that. Could you please repeat?"
            
        try:
            output = self.tts_pipe(text)
            audio_data = output["audio"][0]
            sampling_rate = output["sampling_rate"]
            sf.write(output_path, audio_data, sampling_rate)
            return output_path
        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback for failing TTS
            # Generate a tiny silent file to avoid frontend errors
            sf.write(output_path, np.zeros(16000), 16000)
            return output_path

if __name__ == "__main__":
    # Quick test
    service = SpeechService()
    print("Speech service initialized.")
