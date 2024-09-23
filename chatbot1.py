import requests
import asyncio
import streamlit as st
from streamlit_chat import message
import uuid
import speech_recognition as sr
import json

class InterviewBot:
    def __init__(self, assistant_api_key: str, tts_api_key: str, assistant_url: str, tts_url: str) -> None:
        self.assistant_api_key = assistant_api_key
        self.tts_api_key = tts_api_key
        self.assistant_url = assistant_url
        self.tts_url = tts_url
        
        if 'questions' not in st.session_state:
            st.session_state['questions'] = []
        if 'answers' not in st.session_state:
            st.session_state['answers'] = []
        if 'interview_step' not in st.session_state:
            st.session_state['interview_step'] = 0

        self.session_state = st.session_state

    def ask_question(self) -> None:
        """Ask the current interview question."""
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            text, key = self.session_state['questions'][self.session_state['interview_step']]
            self._text_to_speech(text)  # Play question as audio
            message(text, key=f'message_{key}')
            st.write(f"Bot: {text}")  # Display question on screen

    def _text_to_speech(self, text: str) -> None:
        """Convert text to speech using IBM Watson Text to Speech."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.tts_api_key}',
        }
        data = json.dumps({
            "text": text,
            "voice": "en-US_AllisonV3Voice",
            "accept": "audio/wav"
        })
        response = requests.post(self.tts_url, headers=headers, data=data)

        if response.status_code == 200:
            audio_content = response.content
            st.audio(audio_content, format='audio/wav')
        else:
            st.write("Error in TTS response:", response.text)

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
            asyncio.run(self.ask_dynamic_question(answer))  # Get dynamic question based on answer
            self.session_state['interview_step'] += 1
            st.experimental_rerun()

        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio. Please try again.")
            self.get_audio_answer()  # Restart the listening process
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")

    async def ask_dynamic_question(self, user_answer: str) -> None:
        """Ask a dynamic question based on the user's answer using Watson Assistant."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.assistant_api_key}',
        }
        data = json.dumps({
            "input": {
                "text": user_answer
            }
        })
        response = requests.post(self.assistant_url, headers=headers, data=data)

        if response.status_code == 200:
            follow_up = response.json().get('output', {}).get('generic', [{}])[0].get('text', 'No response received')
            self.session_state['questions'].append((follow_up, self._generate_uuid()))  # Append the new question
            st.write(f"Bot: {follow_up}")  # Display the new AI-generated question
            self._text_to_speech(follow_up)  # Speak the question
        else:
            st.write(f"Error in Watson Assistant response: {response.status_code} - {response.text}")

    def display_past_questions_and_answers(self) -> None:
        """Displays the conversation so far."""
        for i in range(self.session_state['interview_step']):
            question_text, question_key = self.session_state['questions'][i]
            message(question_text, key=f'message_{question_key}')

            if i < len(self.session_state['answers']):
                answer_text, answer_key = self.session_state['answers'][i]
                message(answer_text, is_user=True, key=f'message_{answer_key}')
                st.write(f"You: {answer_text}")  # Display user's answer

    def execute_interview(self) -> None:
        """Run the interview by displaying past questions, asking the next one, and getting audio input."""
        self.display_past_questions_and_answers()
        if self.session_state['interview_step'] < len(self.session_state['questions']):
            self.ask_question()
            self.get_audio_answer()  # Get audio answer after asking the question
        else:
            st.write("Interview complete!")

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a UUID for unique identification."""
        return str(uuid.uuid4())

def create_bot() -> None:
    """Create and initialize the InterviewBot."""
    assistant_api_key = '3V1Ku-mLiEZpk4gcvw4JDdnGobSnJVhOIulAjX1RllSh'  # IBM Watson Assistant API key
    tts_api_key = 'YOUR_TTS_API_KEY'  # Replace with your Watson TTS API key
    assistant_url = 'YOUR_ASSISTANT_URL'  # Replace with your Watson Assistant URL
    tts_url = 'YOUR_TTS_URL'  # Replace with your Watson TTS URL

    bot = InterviewBot(assistant_api_key, tts_api_key, assistant_url, tts_url)
    if len(bot.session_state['questions']) == 0:
        intro_text = "Hey there! I'm your friendly interviewer bot. Let’s get started!"
        bot._text_to_speech(intro_text)
        message(intro_text, key="greeting")
        st.write(intro_text)  # Display intro on screen
        # Prepare initial questions here if needed

    bot.execute_interview()

# Streamlit UI
st.title("InterviewBot - AI Interview Chatbot")
create_bot()
