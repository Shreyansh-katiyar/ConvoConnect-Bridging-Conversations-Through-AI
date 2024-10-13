import asyncio
import streamlit as st
from streamlit_chat import message
import uuid
import pyttsx3
import speech_recognition as sr
import requests
import base64
from streamlit.components.v1 import html

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
    tts_engine = pyttsx3.init()
    did_api_key = 'ew9nyw5zahniyxnretjaz21hawwuy29t:uLUZOCoiV5spKOw_hWegr'  # D-ID API key
    meta_api_key = 'your_meta_api_token_here'  # Replace this with your Meta AI token

    def __init__(self) -> None:
        if 'questions' not in st.session_state:
            st.session_state['questions'] = []
        if 'answers' not in st.session_state:
            st.session_state['answers'] = []
        if 'interview_step' not in st.session_state:
            st.session_state['interview_step'] = 0

        self.session_state = st.session_state

    async def prepare_questions(self) -> None:
        """Prepares a list of predefined questions."""
        questions = [
            "Hi! It's nice to meet you. What's your name?",
            "Why are you interested in this job?",
            "What skills do you bring to the table?",
            "What do you think is your greatest strength?",
        ]
        self.session_state['questions'] = [(question, self._generate_uuid()) for question in questions]

    def ask_question(self) -> None:
        """Ask the current interview question."""
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            text, key = self.session_state['questions'][self.session_state['interview_step']]
            self._text_to_speech(text)
            message(text, key=f'message_{key}')
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
            asyncio.run(self.ask_dynamic_question(answer))
            self.session_state['interview_step'] += 1
            st.experimental_rerun()

        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio. Please try again.")
            self.get_audio_answer()
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")

    def get_meta_ai_response(self, prompt: str) -> str:
        """Query Meta AI and get the response."""
        url = 'https://api.metaai.com/ask'
        headers = {'Authorization': f'Bearer {self.meta_api_key}', 'Content-Type': 'application/json'}
        data = {"prompt": prompt}

        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('response', 'No response found')
        else:
            return f"Error: {response.status_code} - {response.text}"

    async def ask_dynamic_question(self, user_answer: str) -> None:
        """Ask a dynamic question based on the user's answer."""
        try:
            prompt = f"{user_answer}"
            response = self.get_meta_ai_response(prompt)
            if response:
                follow_up = response.strip()
                self.session_state['questions'].append((follow_up, self._generate_uuid()))
                st.write(f"Bot: {follow_up}")
                self._text_to_speech(follow_up)
                await self.generate_avatar_video(follow_up)
            else:
                st.write("No valid response from Meta AI.")
        except Exception as e:
            st.write(f"An error occurred while sending the message: {e}")

    async def generate_avatar_video(self, text: str) -> None:
        """Generate a video of the avatar speaking the given text."""
        api_key_bytes = base64.b64encode(self.did_api_key.encode()).decode()
        url = "https://api.d-id.com/talks"
        headers = {
            'Authorization': f'Basic {api_key_bytes}',
            'Content-Type': 'application/json'
        }
        data = {
            "source_url": "https://media.istockphoto.com/id/1949501832/photo/handsome-hispanic-senior-business-man-with-crossed-arms-smiling-at-camera-indian-or-latin.jpg?s=2048x2048&w=is&k=20&c=nA6_fHYssGdzGF5GHu_l0Y8yVli4ndT4mV-WRPxarlk=",
            "script": {
                "type": "text",
                "input": text
            }
        }

        response = requests.post(url, json=data, headers=headers)
        st.write(response.json())  # Print the full API response for debugging

        if response.status_code == 200:
            video_url = response.json().get("result_url")
            st.write(f"Avatar video generated: {video_url}")

            if video_url:
                st.video(video_url)  # Display the video in Streamlit
        else:
            st.write(f"Error generating avatar video: {response.text}")

    def display_past_questions_and_answers(self) -> None:
        """Displays the conversation so far."""
        for i in range(self.session_state['interview_step']):
            question_text, question_key = self.session_state['questions'][i]
            message(question_text, key=f'message_{question_key}')

            if i < len(self.session_state['answers']):
                answer_text, answer_key = self.session_state['answers'][i]
                message(answer_text, is_user=True, key=f'message_{answer_key}')
                st.write(f"You: {answer_text}")

    def execute_interview(self) -> None:
        """Run the interview by displaying past questions, asking the next one, and getting audio input."""
        self.display_past_questions_and_answers()
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            self.ask_question()
            self.get_audio_answer()
        else:
            st.write("Interview complete!")

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
        message(intro_text, key="greeting")
        st.write(intro_text)
        asyncio.run(bot.prepare_questions())

    bot.execute_interview()

# Streamlit UI
show_live_camera_feed()
create_bot()
