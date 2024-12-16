import os
import subprocess
import pyttsx3
from pathlib import Path
import cv2

# Wav2Lip dependencies and configuration
WAV2LIP_DIR = "Wav2Lip"  # Path to Wav2Lip folder
MODEL_PATH = os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")
VIDEO_PATH = r"C:\Users\yogan\Downloads\5439078-uhd_3840_2160_25fps.mp4"

# Initialize text-to-speech
tts_engine = pyttsx3.init()

# Temporary file paths
AUDIO_OUTPUT_PATH = "output_audio.wav"
LIP_SYNC_OUTPUT_PATH = "lip_sync_result.mp4"


def text_to_speech(text: str, output_audio_path: str) -> None:
    """
    Convert the given text to speech and save the audio file.
    """
    tts_engine.save_to_file(text, output_audio_path)
    tts_engine.runAndWait()


def generate_lip_sync(input_video: str, input_audio: str, output_path: str) -> None:
    """
    Run Wav2Lip model to generate a lip-synced video.
    """
    command = [
        "python",
        os.path.join(WAV2LIP_DIR, "inference.py"),
        "--checkpoint_path", MODEL_PATH,
        "--face", input_video,
        "--audio", input_audio,
        "--outfile", output_path,
    ]
    subprocess.run(command, check=True)


def play_video(video_path: str) -> None:
    """
    Play the generated lip-synced video using OpenCV.
    """
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Lip-Synced Video", frame)

        # Close the window when the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def speak_and_lip_sync(text: str) -> None:
    """
    Integrate text-to-speech and lip-sync generation.
    """
    print(f"Bot: {text}")

    # Convert text to speech and save audio
    text_to_speech(text, AUDIO_OUTPUT_PATH)

    # Generate lip-synced video
    print("Generating lip-sync video...")
    generate_lip_sync(VIDEO_PATH, AUDIO_OUTPUT_PATH, LIP_SYNC_OUTPUT_PATH)

    # Play the lip-synced video
    print("Playing lip-sync video...")
    play_video(LIP_SYNC_OUTPUT_PATH)


# Example Usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter text for the bot to speak (or 'quit' to exit): ").strip()
        if user_input.lower() == "quit":
            break
        speak_and_lip_sync(user_input)
