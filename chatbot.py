import asyncio
import pyttsx3
import speech_recognition as sr
import uuid
import streamlit as st
from streamlit_chat import message
from characterai import aiocai
import time

st.title("InterviewBot - AI Interviewer")

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
        """Prepares a list of predefined questions, including technical questions."""
        questions = [
            # General and behavioral questions
            "Hi! It's nice to meet you. What's your name?",
            "Why are you interested in this job?",
            "Can you tell me a bit about yourself?",
            "What do you consider your greatest strength?",
            "What is one of your weaknesses, and how do you manage it?",
            "What is your preferred working style?",
            "Tell me about a time you overcame a significant challenge.",
            "How do you handle tight deadlines and pressure?",
            "What motivates you to perform well in a job?",
            "How do you prioritize your tasks?",
            "Where do you see yourself in five years?",
            "Describe a successful project you've worked on.",
            "Tell me about a time you faced a conflict at work.",
            "How do you handle constructive criticism?",
            "What do you like to do outside of work?",
            "How do you keep yourself updated with industry trends?",
            "Tell me about a time when you had to learn a new skill quickly.",
            "How would your previous coworkers describe you?",
            "What would you consider your ideal work environment?",
            "Why do you think you'd be a good fit for our company?",
            
            # Technical questions - Python
            "Can you explain the concept of Python decorators?",
            "What are Python list comprehensions, and why are they useful?",
            "How does error handling work in Python, and when would you use try-except?",
            "What is the difference between a list and a tuple in Python?",
            "How do you use lambda functions in Python?",
            "Explain the difference between '==' and 'is' in Python.",
            "What are Python generators, and how do they work?",
            "How does memory management work in Python?",
            "What is the purpose of Python's `with` statement?",
            "How would you use `map`, `filter`, and `reduce` functions in Python?",

            # Technical questions - JavaScript
            "What is the difference between `var`, `let`, and `const` in JavaScript?",
            "How does JavaScript handle asynchronous operations?",
            "What is the concept of closures in JavaScript?",
            "Can you explain the JavaScript `this` keyword?",
            "What is the difference between `==` and `===` in JavaScript?",
            "How do promises work in JavaScript, and what are async/await functions?",
            "What is event delegation in JavaScript?",
            "Explain JavaScript's `call`, `apply`, and `bind` methods.",
            "How would you prevent an event from bubbling up in JavaScript?",
            "What are JavaScript arrow functions, and how do they differ from regular functions?",

            # Technical questions - SQL
            "What is the difference between `INNER JOIN` and `OUTER JOIN` in SQL?",
            "How would you write a query to find duplicate records in a table?",
            "What are indexes in SQL, and why are they important?",
            "Explain the difference between `HAVING` and `WHERE` clauses in SQL.",
            "How do you perform a left join in SQL?",
            "What are stored procedures, and when would you use them?",
            "How would you retrieve the top N records from a table?",
            "Explain SQL transactions and their purpose.",
            "What is a primary key, and how does it differ from a unique key?",
            "How would you update records in SQL based on another table?",
            
            # Additional questions to reach 50
            "What do you consider the most important factor in teamwork?",
            "Describe your process for troubleshooting technical issues.",
            "How do you approach learning new programming languages or technologies?",
            "What tools or practices do you use to improve code quality?",
            "Explain a time when you went above and beyond in a project.",
            "What are your strategies for managing and organizing code?",
            "How would you go about refactoring legacy code?",
            "What methods do you use to ensure your work is efficient and effective?",
            "Have you contributed to open-source projects? If so, tell me about it.",
            "What projects are you currently working on in your spare time?",
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
