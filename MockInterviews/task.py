from moviepy.video.io.VideoFileClip import VideoFileClip
from vosk import Model, KaldiRecognizer
import wave
import json
import os
from .models import MockVideos
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer, SetLogLevel

def convert_to_wav(audio_path):
    audio = AudioSegment.from_file(audio_path)
    # Convert to mono and set frame rate to 16000 Hz
    audio = audio.set_channels(1).set_frame_rate(16000)
    wav_path = audio_path.replace(audio_path.split('.')[-1], "wav")
    audio.export(wav_path, format="wav")
    return wav_path

def extract_audio(video_path):
    """
    Extract audio from a video file and save it as a WAV file.
    """
    try:
        video = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + '.wav'
        video.audio.write_audiofile(audio_path)
        return convert_to_wav(audio_path)
    except Exception as e:
        raise RuntimeError(f"Audio extraction failed: {e}")

def transcribe_audio(audio_path):
    """
    Convert audio to text using Vosk speech-to-text library.
    """
    try:
        SetLogLevel(0)
        model_path = "C:/Users/HP PROBOOK 430 G4/AI-Driven Mock Interview System/MockSmart/voks-model/vosk-model-en-us-0.22"  
        model = Model(model_path)
        wf = wave.open(audio_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000):
            raise ValueError("Audio file must be WAV format mono PCM.")

        recognizer = KaldiRecognizer(model, wf.getframerate())
        transcription = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                transcription.append(json.loads(recognizer.Result())['text'])

        wf.close()
        return " ".join(transcription)
    except Exception as e:
        raise RuntimeError(f"Speech-to-text conversion failed: {e}")
