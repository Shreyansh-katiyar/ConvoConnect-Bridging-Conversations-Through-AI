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
            "What skills do you bring to the table? and how would you rate yourself in the following areas:",
            "What do you think is your greatest strength?",
            "Can you describe a time when you faced a challenge at work and how you overcame it?",
            "How do you handle stress and pressure?",
            "Where do you see yourself in five years?",
            "Why should we hire you?",
            "What motivates you to perform your best at work?",
            "Describe a project or task that you worked on that required creativity.",
            "What is your approach to team collaboration?",
            "How do you stay organized when managing multiple tasks?",
            "Have you ever had to deal with difficult coworkers? How did you handle it?",
            "What is your greatest professional achievement?",
            "How do you keep up with industry trends?",
            "What kind of work environment do you thrive in?",
            "What is the most important thing for a manager to do to be effective?",
            "How do you prioritize tasks when dealing with multiple deadlines?",
            "Tell me about a time when you had to learn a new skill or tool quickly.",
            "What are your expectations from this role?",
            "How do you handle criticism?",
            "What are your salary expectations?",
            "What do you consider to be the key to effective leadership?",
            "How do you approach problem-solving?",
            "Can you provide an example of how you worked effectively under pressure?",
            "How do you stay motivated when performing repetitive tasks?",
            "How would you describe your work style?",
            "What would your colleagues say about you?",
            "Have you ever worked on a project that didn't go as planned? How did you handle it?",
            "What skills do you want to develop in the next year?",
            "What was the most challenging part of your previous job?",
            "Can you describe a time when you worked with a cross-functional team?",
            "What was the biggest challenge in your last job, and how did you overcome it?",
            "What type of work culture do you prefer?",
            "Can you give an example of a time when you had to adapt to a significant change?",
            "How do you ensure the quality of your work?",
            "What do you think is the most important factor for success in this role?",
            "Describe a time when you took the initiative on a project.",
            "How do you handle multiple projects at the same time?",
            "What was the most difficult decision you've had to make at work?",
            "What makes you a good fit for this company?",
            "What are your strengths and weaknesses?",
            "What do you hope to achieve in this role?",
            "What makes you excited about this job?",
            "Tell me about a time when you worked with a team to accomplish a goal.",
            "How do you approach learning new things?",
            "What excites you most about working here?",
            "Tell me about a time when you worked under tight deadlines.",
            "How do you handle a situation where you disagree with a colleague?",
            "What are the key qualities you think are necessary for success in this industry?",
            "What can you bring to the team that others cannot?",
            "What role do you typically play in a team?",
            "Can you describe a time when you made a mistake at work and how you corrected it?",
            "What do you know about our company and the role you're applying for?"
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

            # Wait for the user's audio answer and only move to the next question if it's valid
            while not self.get_audio_answer():
                st.write("Please provide a valid answer.")
            time.sleep(5)  # Pause for 5 seconds after each question
            st.rerun()  # Rerun the app to move to the next question
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
