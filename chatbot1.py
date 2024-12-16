import asyncio
import pyttsx3
import speech_recognition as sr
import uuid
import streamlit as st
from streamlit_chat import message
from characterai import aiocai
import time
import logging
import threading
from queue import Queue
import os
import subprocess
import torch
import torchvision
import cv2
import numpy as np
import librosa

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="InterviewBot - AI Interviewer", layout="wide", initial_sidebar_state="expanded")

# Initialize mode in session state
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'light'

# Handle theme toggle before any UI elements
component_value = st.session_state.get("_component_value")
if component_value is not None and component_value != st.session_state['mode']:
    st.session_state['mode'] = component_value
    st.rerun()

# Apply theme based on mode
if st.session_state['mode'] == 'dark':
    st.markdown("""
        <style>
        /* Dark theme */
        :root {
            --bg-color: #1E1E1E;
            --text-color: #FFFFFF;
            --chat-bg: #2D2D2D;
            --input-bg: #2D2D2D;
            --border-color: rgba(255, 255, 255, 0.1);
        }
        
        .stApp, div[data-testid="stAppViewContainer"] {
            background-color: var(--bg-color) !important;
        }
        
        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .stChatMessage, div[data-testid="stChatMessageContent"] {
            background-color: var(--chat-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .interview-message {
            background-color: var(--chat-bg) !important;
            color: var(--text-color) !important;
            padding: 15px !important;
            border-radius: 10px !important;
            margin: 10px 0 !important;
            border: 1px solid var(--border-color) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stMarkdown, .stMarkdown p {
            color: var(--text-color) !important;
        }
        
        section[data-testid="stSidebar"] {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        
        .camera-feed {
            background: var(--chat-bg) !important;
            border-radius: 15px !important;
            padding: 10px !important;
            border: 1px solid var(--border-color) !important;
        }
        
        h1, h2, h3, p, span, div {
            color: var(--text-color) !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        /* Light theme */
        :root {
            --bg-color: #FFFFFF;
            --text-color: #1d1d1f;
            --chat-bg: #F7F7F7;
            --input-bg: #FFFFFF;
            --border-color: rgba(0, 0, 0, 0.1);
        }
        
        .stApp, div[data-testid="stAppViewContainer"] {
            background-color: var(--bg-color) !important;
        }
        
        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .stChatMessage, div[data-testid="stChatMessageContent"] {
            background-color: var(--chat-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .interview-message {
            background-color: var(--chat-bg) !important;
            color: var(--text-color) !important;
            padding: 15px !important;
            border-radius: 10px !important;
            margin: 10px 0 !important;
            border: 1px solid var(--border-color) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        section[data-testid="stSidebar"] {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        
        .camera-feed {
            background: var(--chat-bg) !important;
            border-radius: 15px !important;
            padding: 10px !important;
            border: 1px solid var(--border-color) !important;
        }
        
        h1, h2, h3, p, span, div {
            color: var(--text-color) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Add modern theme toggle in sidebar
st.sidebar.markdown("""
    <style>
    /* Theme toggle styles */
    .theme-switch-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        margin: 20px 0;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: var(--chat-bg);
    }
    
    .theme-switch {
        position: relative;
        width: 60px;
        height: 30px;
        margin: 0 10px;
    }
    
    .theme-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .theme-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.2);
        transition: 0.4s;
        border-radius: 30px;
        padding: 2px;
    }
    
    .theme-slider:before {
        position: absolute;
        content: "🌞";
        display: flex;
        align-items: center;
        justify-content: center;
        height: 26px;
        width: 26px;
        left: 2px;
        bottom: 2px;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        transition: 0.4s;
        border-radius: 50%;
        font-size: 16px;
    }
    
    input:checked + .theme-slider {
        background: rgba(0, 0, 0, 0.4);
    }
    
    input:checked + .theme-slider:before {
        transform: translateX(30px);
        content: "🌙";
        background: linear-gradient(45deg, #2C3E50, #3498DB);
    }
    
    .theme-switch:hover .theme-slider:before {
        transform: scale(1.1);
    }
    
    .theme-switch input:checked:hover + .theme-slider:before {
        transform: translateX(30px) scale(1.1);
    }
    
    /* Glow effect */
    .theme-slider:before {
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
    }
    
    input:checked + .theme-slider:before {
        box-shadow: 0 0 8px rgba(52, 152, 219, 0.6);
    }
    
    .theme-label {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--text-color);
    }
    </style>
    
    <div class="theme-switch-container">
        <span class="theme-label">Light</span>
        <label class="theme-switch">
            <input type="checkbox" id="theme-toggle" 
                onchange="toggleTheme(this.checked)"
                """ + ('checked' if st.session_state['mode'] == 'dark' else '') + """>
            <span class="theme-slider"></span>
        </label>
        <span class="theme-label">Dark</span>
    </div>
    
    <script>
    function toggleTheme(isDark) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: isDark ? 'dark' : 'light'
        }, '*');
    }
    </script>
""", unsafe_allow_html=True)

# Add modern styling for the app
st.markdown("""
    <style>
    /* Modern UI styles */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    }
    
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        font-weight: 600;
        letter-spacing: -0.5px;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    .interview-message {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .interview-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .camera-feed iframe {
        border-radius: 12px;
        transition: transform 0.3s ease;
    }
    
    .camera-feed iframe:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript for tab switching alert
st.markdown(
    """
    <script>
    document.addEventListener('visibilitychange', function() {
      if (document.hidden) {
        alert("Warning: You have switched tabs. This is not allowed during the interview.");
      }
    });
    </script>
    """,
    unsafe_allow_html=True
)

st.title("InterviewBot - AI Interviewer")

# Display video feed if camera is on
def show_live_camera_feed():
    """Displays a live camera feed in the sidebar with enhanced Apple-like styling."""
    with st.sidebar:
        st.markdown("""
            <style>
            .camera-container {
                position: relative;
                width: 340px;
                margin: 20px auto;
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                background: rgba(28, 28, 30, 0.6);
            }
            
            .camera-header {
                background: rgba(255, 255, 255, 0.08);
                padding: 12px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
            }
            
            .camera-title {
                color: #fff;
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 0.3px;
            }
            
            .camera-status {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background: #34c759;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            .status-text {
                color: rgba(255, 255, 255, 0.6);
                font-size: 13px;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .camera-feed {
                position: relative;
                width: 100%;
                height: 260px;
                background: #000;
            }
            
            .camera-feed iframe {
                width: 100%;
                height: 100%;
                border: none;
                display: block;
            }
            
            .camera-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                background: linear-gradient(
                    180deg, 
                    rgba(0,0,0,0.3) 0%, 
                    rgba(0,0,0,0) 15%, 
                    rgba(0,0,0,0) 85%, 
                    rgba(0,0,0,0.3) 100%
                );
            }
            
            .camera-controls {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 24px;
                align-items: center;
                z-index: 10;
            }
            
            .camera-button {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.8);
                cursor: pointer;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .camera-button:hover {
                background: rgba(255, 255, 255, 0.25);
                transform: scale(1.05);
            }
            
            .camera-button:active {
                transform: scale(0.95);
            }
            
            .record-button {
                width: 66px;
                height: 66px;
                background: rgba(255, 255, 255, 0.2);
            }
            
            .record-button::after {
                content: '';
                width: 24px;
                height: 24px;
                background: #ff3b30;
                border-radius: 50%;
                box-shadow: 0 0 12px rgba(255, 59, 48, 0.4);
                transition: all 0.2s ease;
            }
            
            .record-button:hover::after {
                transform: scale(1.1);
                box-shadow: 0 0 16px rgba(255, 59, 48, 0.6);
            }
            
            .side-button-left::before {
                content: '⟲';
                color: rgba(255, 255, 255, 0.9);
                font-size: 24px;
            }
            
            .side-button-right::before {
                content: '⚙️';
                font-size: 20px;
            }
            
            @media (prefers-color-scheme: dark) {
                .camera-container {
                    background: rgba(28, 28, 30, 0.8);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
                }
            }
            </style>
            
            <div class="camera-container">
                <div class="camera-header">
                    <div class="camera-title">Yogansh Singh</div>
                    <div class="camera-status">
                        <div class="status-dot"></div>
                        <div class="status-text">Live</div>
                    </div>
                </div>
                <div class="camera-feed">
                    <iframe src="http://127.0.0.1:5000/video_feed" frameborder="0"></iframe>
                    <div class="camera-overlay"></div>
                    <div class="camera-controls">
                        <div class="camera-button side-button-left"></div>
                        <div class="camera-button record-button"></div>
                        <div class="camera-button side-button-right"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

class SimpleLipSyncAnimator:
    def __init__(self, video_path):
        self.video_path = video_path
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def estimate_mouth_movement(self, audio_path):
        """
        Estimate mouth movement based on audio energy.
        This is a simplified approximation of lip-syncing.
        """
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Compute audio energy
        energy = librosa.feature.rms(y=y)[0]
        
        # Normalize energy
        energy = (energy - energy.min()) / (energy.max() - energy.min())
        
        return energy

    def generate_animated_video(self, audio_path):
        """
        Generate a simple animated video with mouth movement approximation.
        """
        try:
            # Load original video
            cap = cv2.VideoCapture(self.video_path)
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Prepare output video
            output_path = os.path.join(self.temp_dir, f"animated_video_{uuid.uuid4()}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Estimate mouth movement
            mouth_energy = self.estimate_mouth_movement(audio_path)
            
            # Process video frames
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Simulate mouth movement based on audio energy
                if frame_count < len(mouth_energy):
                    energy = mouth_energy[frame_count]
                    
                    # Modify frame to simulate mouth movement
                    # This is a very basic approximation
                    mouth_region = frame[height//2:height, width//4:width*3//4]
                    brightness_factor = 1 + (energy * 0.5)  # Adjust brightness based on energy
                    mouth_region = np.clip(mouth_region * brightness_factor, 0, 255).astype(np.uint8)
                    frame[height//2:height, width//4:width*3//4] = mouth_region
                
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            return output_path
        
        except Exception as e:
            st.error(f"Video animation error: {e}")
            return None

class InterviewBot:
    char = 'f4hEGbw8ywUrjsrye03EJxiBdooy--HiOWgU2EiRJ0s'  # Character ID
    token = '67c42f8f986f526fe33a8630b9bdbbf97b219783'  # API token
    tts_engine = None  # Initialize as None
    did_api_key = 'ew9nyw5zahniyxnretjaz21hawwuy29t:uLUZOCoiV5spKOw_hWegr'  # D-ID API key

    interviewer_icon_path = "C:\\Users\\yogan\\Downloads\\male-avatar-rgb-color-icon-human-resources-for-job-employee-for-company-career-corporate-businessman-man-for-interview-manager-in-suit-person-head-isolated-vector-illustration-700-219045181.jpg"
    interviewee_icon_path = "C:\\Users\\yogan\\Downloads\\2303808.png"
    video_path = r"C:\Users\yogan\Downloads\5439078-uhd_3840_2160_25fps.mp4"

    def __init__(self) -> None:
        if 'questions' not in st.session_state:
            st.session_state['questions'] = []
        if 'answers' not in st.session_state:
            st.session_state['answers'] = []
        if 'interview_step' not in st.session_state:
            st.session_state['interview_step'] = 0
        if 'tts_engine' not in st.session_state:
            st.session_state['tts_engine'] = pyttsx3.init()
            voices = st.session_state['tts_engine'].getProperty('voices')
            if voices:
                st.session_state['tts_engine'].setProperty('voice', voices[0].id)
            st.session_state['tts_engine'].setProperty('rate', 150)
            st.session_state['tts_engine'].setProperty('volume', 0.9)
        
        self.session_state = st.session_state
        self.tts_queue = Queue()
        self.tts_thread = None
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        self._initialize_tts_engine()
        self.lip_sync_animator = SimpleLipSyncAnimator(self.video_path)

    def _initialize_tts_engine(self):
        """Initialize the TTS engine if it hasn't been initialized yet."""
        if st.session_state['tts_engine'] is None:
            try:
                st.session_state['tts_engine'] = pyttsx3.init()
                voices = st.session_state['tts_engine'].getProperty('voices')
                if voices:
                    st.session_state['tts_engine'].setProperty('voice', voices[0].id)
                st.session_state['tts_engine'].setProperty('rate', 150)
                st.session_state['tts_engine'].setProperty('volume', 0.9)
            except Exception as e:
                logging.error(f"Error initializing TTS engine: {e}")

    async def start_chat(self):
        """Connect to Character.AI and start a chat."""
        try:
            client = aiocai.Client(self.token)
            me = await client.get_me()  # Retrieve your user information
            async with client as conn:
                new_chat = await conn.create_chat(self.char)  # Create a new chat using the character ID
                return conn, new_chat
        except Exception as e:
            st.write(f"An error occurred during chat connection: {e}")
            return None, None

    async def prepare_questions(self) -> list:
        """Prepares a list of predefined questions, including technical questions."""
        questions = [
            # First few questions to keep it simple
            "Hi! It's nice to meet you. What's your name?",
            "Why are you interested in this job?",
            "Can you tell me a bit about yourself?",
            "What do you consider your greatest strength?",
            "What is one of your weaknesses, and how do you manage it?"
        ]
        
        return questions

    def ask_question(self) -> None:
        """Ask the current interview question."""
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            text, key = self.session_state['questions'][self.session_state['interview_step']]
            self._text_to_speech_with_lipsync(text)
            # Display interviewer message with modern styling
            st.markdown(f"""
            <div class="interview-message interviewer-message">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" 
                         width="40" style="border-radius: 50%; margin-right: 10px;">
                    <span style="font-weight: 500;">AI Interviewer</span>
                </div>
                <p style="margin: 0; line-height: 1.5;">{text}</p>
            </div>
            """, unsafe_allow_html=True)
            self.session_state['current_question'] = text

    def _text_to_speech(self, text: str) -> None:
        """Convert text to speech and play it."""
        try:
            engine = self.session_state['tts_engine']
            engine.stop()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            st.error(f"Speech error: {str(e)}")
            self.session_state['tts_engine'] = pyttsx3.init()

    def _text_to_speech_with_lipsync(self, text: str) -> None:
        """Convert text to speech and generate simple animated video."""
        try:
            # Generate audio file
            audio_file = os.path.join(self.temp_dir, f"temp_audio_{uuid.uuid4()}.wav")
            engine = self.session_state['tts_engine']
            engine.save_to_file(text, audio_file)
            engine.runAndWait()

            # Generate animated video
            animated_video = self.lip_sync_animator.generate_animated_video(audio_file)

            if animated_video:
                # Display animated video
                video_file = open(animated_video, 'rb')
                video_bytes = video_file.read()
                st.video(video_bytes)
                video_file.close()

                # Clean up temporary files
                os.remove(audio_file)
                os.remove(animated_video)
            else:
                # Fallback to regular text-to-speech
                self._text_to_speech(text)

        except Exception as e:
            st.error(f"Lip-sync processing error: {e}")
            self._text_to_speech(text)

    def get_audio_answer(self) -> bool:
        """Get the user's response via audio."""
        logging.debug("Listening for audio answer...")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening for your answer...")
            audio = r.listen(source)

        try:
            answer = r.recognize_google(audio)
            logging.debug(f"Recognized answer: {answer}")
            st.write(f"You said: {answer}")
            self.session_state['answers'].append((answer, self._generate_uuid()))
            self.session_state['interview_step'] += 1
            return True

        except sr.UnknownValueError:
            logging.error("Could not understand the audio.")
            st.write("Sorry, I could not understand the audio. Please try again.")
            return False
        except sr.RequestError as e:
            logging.error(f"Speech recognition request failed: {e}")
            st.write(f"Could not request results from Google Speech Recognition service; {e}")
            return False

    def display_past_questions_and_answers(self) -> None:
        """Displays the conversation so far with modern styling."""
        for i in range(self.session_state['interview_step']):
            question_text, question_key = self.session_state['questions'][i]
            # Display interviewer message with modern styling
            st.markdown(f"""
            <div class="interview-message interviewer-message">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" 
                         width="40" style="border-radius: 50%; margin-right: 10px;">
                    <span style="font-weight: 500;">AI Interviewer</span>
                </div>
                <p style="margin: 0; line-height: 1.5;">{question_text}</p>
            </div>
            """, unsafe_allow_html=True)

            if i < len(self.session_state['answers']):
                answer_text, answer_key = self.session_state['answers'][i]
                # Display interviewee message with modern styling
                st.markdown(f"""
                <div class="interview-message interviewee-message" style="background: linear-gradient(135deg, #007AFF, #0055FF) !important; margin-left: auto; max-width: 80%;">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <img src="data:image/png;base64,{self._image_to_base64(self.interviewee_icon_path)}" 
                             width="40" style="border-radius: 50%; margin-right: 10px;">
                        <span style="font-weight: 500; color: white !important;">You</span>
                    </div>
                    <p style="margin: 0; line-height: 1.5; color: white !important;">{answer_text}</p>
                </div>
                """, unsafe_allow_html=True)

    def execute_interview(self) -> None:
        """Run the interview by displaying past questions, asking the next one, and getting audio input."""
        self.display_past_questions_and_answers()
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            self.ask_question()

            # Wait for the user's audio answer and only move to the next question if it's valid
            while not self.get_audio_answer():
                st.write("Please provide a valid answer.")
            time.sleep(5)  # Pause for 5 seconds after each question
            st.rerun()  # Rerun the app to move to the next question
        else:
            st.write("Interview complete!")

    def _image_to_base64(self, image_path):
        """Convert image file to base64 format."""
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a UUID for unique identification."""
        return str(uuid.uuid4())

def create_bot():
    """Create and initialize the InterviewBot with Streamlit UI."""
    # Initialize the interview bot
    bot = InterviewBot()
    
    # Streamlit UI for interview
    st.title("AI Interview Simulator")
    
    # Prepare questions
    questions = [
        "Hi! It's nice to meet you. What's your name?",
        "Why are you interested in this job?",
        "Can you tell me a bit about yourself?",
        "What do you consider your greatest strength?",
        "What is one of your weaknesses, and how do you manage it?"
    ]
    
    # Initialize session state
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    # Display current question
    if st.session_state.current_question_index < len(questions):
        current_question = questions[st.session_state.current_question_index]
        st.write(f"Question {st.session_state.current_question_index + 1}: {current_question}")
        
        # Text input for answer
        user_answer = st.text_input("Your Answer:")
        
        # Submit button
        if st.button("Submit Answer"):
            # Speak the question
            bot._text_to_speech_with_lipsync(current_question)
            
            # Move to next question
            st.session_state.current_question_index += 1
            st.experimental_rerun()
    else:
        st.success("Interview Completed! ")

# Streamlit UI
show_live_camera_feed()
create_bot()