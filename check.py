import pyttsx3
import io

def generate_audio(text):
    engine = pyttsx3.init()
    audio_io = io.BytesIO()
    engine.save_to_file(text, audio_io)
    engine.runAndWait()
    audio_io.seek(0)
    return audio_io.read()

# Test text-to-speech
audio_data = generate_audio("Hello World")
with open("output.wav", "wb") as f:
    f.write(audio_data)
