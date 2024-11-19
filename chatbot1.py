import asyncio
import pyttsx3
import speech_recognition as sr
import uuid
import streamlit as st
from streamlit_chat import message
from characterai import aiocai
import time

st.title("InterviewBot - AI Interview Chatbot")

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

# Camera feed function
def show_live_camera_feed():
    """Displays a live camera feed in the sidebar."""
    with st.sidebar:
        st.subheader("Live Camera Feed")
        st.markdown(
            '''
            <iframe src="http://127.0.0.1:5000/video_feed" width="320" height="240" frameborder="0"></iframe>
            ''',
            unsafe_allow_html=True
        )

class InterviewBot:
    char = 'f4hEGbw8ywUrjsrye03EJxiBdooy--HiOWgU2EiRJ0s'  # Character ID
    token = '67c42f8f986f526fe33a8630b9bdbbf97b219783'  # API token
    tts_engine = pyttsx3.init()
    did_api_key = 'ew9nyw5zahniyxnretjaz21hawwuy29t:uLUZOCoiV5spKOw_hWegr'  # D-ID API key

    interviewer_icon_path = "C:\\Users\\yogan\\Downloads\\male-avatar-rgb-color-icon-human-resources-for-job-employee-for-company-career-corporate-businessman-man-for-interview-manager-in-suit-person-head-isolated-vector-illustration-700-219045181.jpg"
    interviewee_icon_path = "C:\\Users\\yogan\\Downloads\\2303808.png"

    def __init__(self) -> None:
        if 'questions' not in st.session_state:
            st.session_state['questions'] = []
        if 'answers' not in st.session_state:
            st.session_state['answers'] = []
        if 'interview_step' not in st.session_state:
            st.session_state['interview_step'] = 0

        self.session_state = st.session_state

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

    async def prepare_questions(self) -> None:
        """Prepares a list of predefined questions."""
        questions = [
            "Hi! It's nice to meet you. What's your name?",
            "Why are you interested in this job?",
            # Additional questions omitted for brevity
        ]
        self.session_state['questions'] = [(question, self._generate_uuid()) for question in questions]

    def ask_question(self) -> None:
        """Ask the current interview question."""
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            text, key = self.session_state['questions'][self.session_state['interview_step']]
            self._text_to_speech(text)
            # Display interviewer message with icon
            st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
                <p>{text}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state['current_question'] = text
            st.write(f"Bot: {text}")

    def _text_to_speech(self, text: str) -> None:
        """Convert text to speech and play it."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def get_audio_answer(self) -> None:
        """Get the user's response via audio."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening for your answer...")
            audio = r.listen(source)

        try:
            answer = r.recognize_google(audio)
            st.write(f"You said: {answer}")
            self.session_state['answers'].append((answer, self._generate_uuid()))
            self.session_state['interview_step'] += 1
            # Continue running the Streamlit app (no stop)
            return True

        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio. Please try again.")
            return False
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
            return False

    def display_past_questions_and_answers(self) -> None:
        """Displays the conversation so far."""
        for i in range(self.session_state['interview_step']):
            question_text, question_key = self.session_state['questions'][i]
            # Display interviewer message with icon
            st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
                <p>{question_text}</p>
            </div>
            """, unsafe_allow_html=True)

            if i < len(self.session_state['answers']):
                answer_text, answer_key = self.session_state['answers'][i]
                # Display interviewee message with icon
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <img src="data:image/png;base64,{self._image_to_base64(self.interviewee_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
                    <p>{answer_text}</p>
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

def create_bot() -> None:
    """Create and initialize the InterviewBot."""
    bot = InterviewBot()
    if len(bot.session_state['questions']) == 0:
        intro_text = "Hey there! I'm your friendly interviewer bot. Let’s get started!"
        bot._text_to_speech(intro_text)
        # Display interviewer greeting with icon
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{bot._image_to_base64(bot.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
            <p>{intro_text}</p>
        </div>
        """, unsafe_allow_html=True)
        asyncio.run(bot.prepare_questions())

    bot.execute_interview()

# Streamlit UI
show_live_camera_feed()
create_bot()
