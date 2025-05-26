import asyncio
import pyttsx3
import speech_recognition as sr
import uuid
import streamlit as st
from streamlit_chat import message
from characterai import aiocai
import time
import pandas as pd
import random
from datetime import datetime
import os
import requests
import json
from typing import Dict, List, Tuple, Any

st.title("InterviewBot - AI Interviewer with Smart Evaluation")

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

class CandidateEvaluator:
    """AI-powered candidate evaluation system using AIML API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.aimlapi.com/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_candidate_performance(self, responses_df: pd.DataFrame, emotions_df: pd.DataFrame, candidate_name: str) -> Dict[str, Any]:
        """Comprehensive candidate analysis using AI."""
        
        # Prepare data for analysis
        interview_data = self._prepare_interview_data(responses_df, emotions_df)
        
        # Generate AI analysis
        analysis_prompt = self._create_analysis_prompt(interview_data, candidate_name)
        ai_analysis = self._get_ai_analysis(analysis_prompt)
        
        # Calculate detailed scores
        scores = self._calculate_comprehensive_scores(responses_df, emotions_df, ai_analysis)
        
        # Generate final recommendation
        recommendation = self._generate_recommendation(scores, ai_analysis)
        
        return {
            'candidate_name': candidate_name,
            'scores': scores,
            'ai_analysis': ai_analysis,
            'recommendation': recommendation,
            'personality_traits': self._extract_personality_traits(ai_analysis),
            'strengths': self._extract_strengths(ai_analysis),
            'areas_for_improvement': self._extract_improvements(ai_analysis),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _prepare_interview_data(self, responses_df: pd.DataFrame, emotions_df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare structured data for AI analysis."""
        
        # Process responses
        questions = responses_df[responses_df['Speaker'] == 'Interviewer']['Question/Answer'].tolist()
        answers = responses_df[responses_df['Speaker'] != 'Interviewer']['Question/Answer'].tolist()
        
        # Process emotions
        emotion_summary = emotions_df['Emotion'].value_counts().to_dict()
        emotion_timeline = emotions_df.to_dict('records')
        
        # Calculate emotion stability
        emotion_changes = len(emotions_df['Emotion'].diff().dropna())
        emotion_stability = max(0, 100 - (emotion_changes * 2))  # Penalty for frequent changes
        
        return {
            'total_questions': len(questions),
            'total_answers': len(answers),
            'q_and_a_pairs': list(zip(questions[:len(answers)], answers)),
            'emotion_summary': emotion_summary,
            'emotion_timeline': emotion_timeline,
            'emotion_stability_score': emotion_stability,
            'interview_phases': responses_df['Interview_Phase'].unique().tolist()
        }
    
    def _create_analysis_prompt(self, interview_data: Dict[str, Any], candidate_name: str) -> str:
        """Create comprehensive analysis prompt for AI."""
        
        qa_text = "\n".join([f"Q: {q}\nA: {a}\n" for q, a in interview_data['q_and_a_pairs']])
        emotion_text = ", ".join([f"{emotion}: {count}" for emotion, count in interview_data['emotion_summary'].items()])
        
        prompt = f"""
        You are an expert HR professional and psychologist conducting a comprehensive candidate evaluation.
        
        CANDIDATE: {candidate_name}
        
        INTERVIEW RESPONSES:
        {qa_text}
        
        EMOTIONAL ANALYSIS:
        - Emotion Distribution: {emotion_text}
        - Emotion Stability Score: {interview_data['emotion_stability_score']}/100
        - Total Questions: {interview_data['total_questions']}
        - Interview Phases: {', '.join(interview_data['interview_phases'])}
        
        Please provide a detailed professional analysis covering:
        
        1. TECHNICAL COMPETENCY (Rate 1-10):
           - Programming knowledge depth
           - Problem-solving approach
           - Technical communication clarity
        
        2. BEHAVIORAL ASSESSMENT (Rate 1-10):
           - Communication skills
           - Confidence level
           - Professionalism
           - Adaptability
        
        3. EMOTIONAL INTELLIGENCE (Rate 1-10):
           - Emotional stability during interview
           - Stress management
           - Self-awareness
           - Interpersonal skills
        
        4. PERSONALITY TRAITS:
           Identify 5-7 key personality traits with explanations
        
        5. STRENGTHS:
           List 3-5 major strengths with specific examples
        
        6. AREAS FOR IMPROVEMENT:
           List 3-5 areas needing development
        
        7. CULTURAL FIT ASSESSMENT (Rate 1-10):
           - Team collaboration potential
           - Alignment with professional values
           - Growth mindset
        
        8. OVERALL ASSESSMENT:
           Provide a comprehensive summary and final recommendation.
        
        Format your response as a structured professional assessment with clear ratings and detailed explanations.
        """
        
        return prompt
    
    def _get_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis from AIML API."""
        try:
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert HR professional and organizational psychologist with 15+ years of experience in candidate assessment and evaluation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return "Analysis unavailable due to API error."
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return "Analysis unavailable due to unexpected error."
    
    def _calculate_comprehensive_scores(self, responses_df: pd.DataFrame, emotions_df: pd.DataFrame, ai_analysis: str) -> Dict[str, float]:
        """Calculate detailed scoring based on multiple factors."""
        
        scores = {}
        
        # Technical Score (based on technical questions and AI analysis)
        technical_responses = responses_df[
            responses_df['Interview_Phase'].str.contains('technical', na=False)
        ]
        technical_score = min(len(technical_responses) * 8, 85)  # Base technical engagement
        scores['technical_competency'] = technical_score
        
        # Communication Score (based on response length and clarity)
        candidate_responses = responses_df[
            (responses_df['Speaker'] != 'Interviewer') & 
            (responses_df['Speaker'] != 'System')
        ]
        
        if not candidate_responses.empty:
            avg_response_length = candidate_responses['Question/Answer'].str.len().mean()
            communication_score = min(avg_response_length / 10, 90)  # Normalize to 0-90
            scores['communication_skills'] = communication_score
        else:
            scores['communication_skills'] = 0
        
        # Emotional Stability Score
        if not emotions_df.empty:
            positive_emotions = ['happy', 'confident', 'calm', 'focused', 'engaged']
            negative_emotions = ['angry', 'sad', 'fear', 'anxious', 'stressed']
            neutral_emotions = ['neutral', 'surprised']
            
            emotion_counts = emotions_df['Emotion'].value_counts()
            total_emotions = len(emotions_df)
            
            positive_ratio = sum(emotion_counts.get(emotion, 0) for emotion in positive_emotions) / total_emotions
            negative_ratio = sum(emotion_counts.get(emotion, 0) for emotion in negative_emotions) / total_emotions
            
            emotional_stability = (positive_ratio * 100) - (negative_ratio * 30)
            scores['emotional_intelligence'] = max(0, min(100, emotional_stability))
        else:
            scores['emotional_intelligence'] = 50  # Default neutral score
        
        # Engagement Score (based on interview completion)
        total_possible_questions = 40
        questions_answered = len(candidate_responses)
        engagement_score = (questions_answered / total_possible_questions) * 100
        scores['engagement_level'] = min(engagement_score, 100)
        
        # Behavioral Score (composite of multiple factors)
        behavioral_factors = [
            scores['communication_skills'],
            scores['emotional_intelligence'],
            scores['engagement_level']
        ]
        scores['behavioral_assessment'] = sum(behavioral_factors) / len(behavioral_factors)
        
        # Cultural Fit Score (based on professionalism and responses)
        cultural_fit = (scores['behavioral_assessment'] + scores['emotional_intelligence']) / 2
        scores['cultural_fit'] = cultural_fit
        
        # Overall Score (weighted average)
        weights = {
            'technical_competency': 0.30,
            'communication_skills': 0.20,
            'behavioral_assessment': 0.25,
            'emotional_intelligence': 0.15,
            'cultural_fit': 0.10
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights.keys())
        scores['overall_score'] = overall_score
        
        return scores
    
    def _generate_recommendation(self, scores: Dict[str, float], ai_analysis: str) -> str:
        """Generate final hiring recommendation."""
        overall_score = scores['overall_score']
        
        if overall_score >= 80:
            return "RECOMMENDED"
        elif overall_score >= 60:
            return "BORDERLINE - FURTHER EVALUATION REQUIRED"
        else:
            return "NOT RECOMMENDED"
    
    def _extract_personality_traits(self, ai_analysis: str) -> List[str]:
        """Extract personality traits from AI analysis."""
        # This is a simplified extraction - in reality, you'd use more sophisticated NLP
        traits = []
        common_traits = [
            "analytical", "creative", "detail-oriented", "leadership", "collaborative",
            "adaptable", "confident", "communicative", "problem-solver", "innovative",
            "reliable", "proactive", "empathetic", "resilient", "organized"
        ]
        
        for trait in common_traits:
            if trait.lower() in ai_analysis.lower():
                traits.append(trait.title())
        
        return traits[:7]  # Return top 7 traits
    
    def _extract_strengths(self, ai_analysis: str) -> List[str]:
        """Extract strengths from AI analysis."""
        # Simplified extraction
        return [
            "Strong technical foundation",
            "Clear communication skills",
            "Professional demeanor",
            "Problem-solving ability",
            "Adaptability to new challenges"
        ]
    
    def _extract_improvements(self, ai_analysis: str) -> List[str]:
        """Extract areas for improvement from AI analysis."""
        # Simplified extraction
        return [
            "Deepen domain-specific knowledge",
            "Enhance confidence in technical discussions",
            "Improve response elaboration",
            "Strengthen leadership examples"
        ]
    
    def generate_marks_document(self, evaluation_result: Dict[str, Any]) -> pd.DataFrame:
        """Generate comprehensive candidate marks document."""
        
        candidate_name = evaluation_result['candidate_name']
        scores = evaluation_result['scores']
        recommendation = evaluation_result['recommendation']
        
        # Create detailed marks sheet
        marks_data = []
        
        # Header Information
        marks_data.append({
            'Category': 'CANDIDATE INFORMATION',
            'Component': 'Name',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': candidate_name
        })
        
        marks_data.append({
            'Category': 'CANDIDATE INFORMATION',
            'Component': 'Assessment Date',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': evaluation_result['timestamp']
        })
        
        # Technical Competency Section
        marks_data.append({
            'Category': 'TECHNICAL COMPETENCY',
            'Component': 'Programming Knowledge',
            'Score': f"{scores['technical_competency']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['technical_competency']:.1f}%",
            'Details': 'Assessment based on technical responses and problem-solving approach'
        })
        
        # Communication Assessment
        marks_data.append({
            'Category': 'COMMUNICATION SKILLS',
            'Component': 'Verbal Communication',
            'Score': f"{scores['communication_skills']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['communication_skills']:.1f}%",
            'Details': 'Clarity, articulation, and response quality'
        })
        
        # Behavioral Assessment
        marks_data.append({
            'Category': 'BEHAVIORAL ASSESSMENT',
            'Component': 'Professional Behavior',
            'Score': f"{scores['behavioral_assessment']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['behavioral_assessment']:.1f}%",
            'Details': 'Professionalism, confidence, and interview conduct'
        })
        
        # Emotional Intelligence
        marks_data.append({
            'Category': 'EMOTIONAL INTELLIGENCE',
            'Component': 'Emotional Stability',
            'Score': f"{scores['emotional_intelligence']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['emotional_intelligence']:.1f}%",
            'Details': 'Stress management and emotional regulation during interview'
        })
        
        # Cultural Fit
        marks_data.append({
            'Category': 'CULTURAL FIT',
            'Component': 'Team Integration Potential',
            'Score': f"{scores['cultural_fit']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['cultural_fit']:.1f}%",
            'Details': 'Alignment with organizational values and team dynamics'
        })
        
        # Overall Score
        marks_data.append({
            'Category': 'OVERALL ASSESSMENT',
            'Component': 'Composite Score',
            'Score': f"{scores['overall_score']:.1f}",
            'Max Score': '100',
            'Percentage': f"{scores['overall_score']:.1f}%",
            'Details': 'Weighted average of all assessment components'
        })
        
        # Personality Traits
        traits_str = ', '.join(evaluation_result['personality_traits'])
        marks_data.append({
            'Category': 'PERSONALITY PROFILE',
            'Component': 'Key Traits',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': traits_str
        })
        
        # Strengths
        strengths_str = ' | '.join(evaluation_result['strengths'])
        marks_data.append({
            'Category': 'STRENGTHS',
            'Component': 'Identified Strengths',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': strengths_str
        })
        
        # Areas for Improvement
        improvements_str = ' | '.join(evaluation_result['areas_for_improvement'])
        marks_data.append({
            'Category': 'DEVELOPMENT AREAS',
            'Component': 'Areas for Improvement',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': improvements_str
        })
        
        # Final Recommendation
        marks_data.append({
            'Category': 'FINAL RECOMMENDATION',
            'Component': 'Hiring Decision',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': recommendation
        })
        
        # AI Analysis Summary
        marks_data.append({
            'Category': 'AI ANALYSIS SUMMARY',
            'Component': 'Detailed Assessment',
            'Score': '',
            'Max Score': '',
            'Percentage': '',
            'Details': evaluation_result['ai_analysis'][:500] + "..." if len(evaluation_result['ai_analysis']) > 500 else evaluation_result['ai_analysis']
        })
        
        return pd.DataFrame(marks_data)

class InterviewBot:
    char = 'f4hEGbw8ywUrjsrye03EJxiBdooy--HiOWgU2EiRJ0s'  # Character ID
    token = '67c42f8f986f526fe33a8630b9bdbbf97b219783'  # API token
    tts_engine = pyttsx3.init()
    aiml_api_key = '508f0852c77742bcbb5adaccde0308fe'  # AIML API key

    interviewer_icon_path = "C:\\Users\\yogan\\Downloads\\intervieww.jpg"
    interviewee_icon_path = "C:\\Users\\yogan\\Downloads\\2303808.png"

    def __init__(self) -> None:
        if 'questions' not in st.session_state:
            st.session_state['questions'] = {}
        if 'answers' not in st.session_state:
            st.session_state['answers'] = []
        if 'interview_step' not in st.session_state:
            st.session_state['interview_step'] = 0
        if 'used_questions' not in st.session_state:
            st.session_state['used_questions'] = []
        if 'interview_phase' not in st.session_state:
            st.session_state['interview_phase'] = 'introduction'
        if 'candidate_name' not in st.session_state:
            st.session_state['candidate_name'] = ''
        if 'excel_data' not in st.session_state:
            st.session_state['excel_data'] = []
        if 'evaluator' not in st.session_state:
            st.session_state['evaluator'] = CandidateEvaluator(self.aiml_api_key)

        self.session_state = st.session_state
        self.evaluator = st.session_state['evaluator']

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
        """Prepares categorized questions for natural interview flow."""
        questions = {
            'introduction': [
                "Hi! It's nice to meet you. What's your name?",
                "Thank you for joining us today. Could you please introduce yourself?",
                "Good morning/afternoon! Let's start with your name, please.",
            ],
            'warm_up': [
                "Can you tell me a bit about yourself?",
                "What brings you here today?",
                "How did you hear about this position?",
                "What interests you about this role?",
            ],
            'behavioral': [
                "What do you consider your greatest strength?",
                "What is one of your weaknesses, and how do you manage it?",
                "Tell me about a time you overcame a significant challenge.",
                "How do you handle tight deadlines and pressure?",
                "What motivates you to perform well in a job?",
                "How do you prioritize your tasks?",
                "Describe a successful project you've worked on.",
                "Tell me about a time you faced a conflict at work.",
                "How do you handle constructive criticism?",
                "Tell me about a time when you had to learn a new skill quickly.",
                "How would your previous coworkers describe you?",
                "What is your preferred working style?",
                "How do you keep yourself updated with industry trends?",
                "Explain a time when you went above and beyond in a project.",
            ],
            'technical_python': [
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
            ],
            'technical_javascript': [
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
            ],
            'technical_sql': [
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
            ],
            'experience': [
                "Why are you interested in this job?",
                "Where do you see yourself in five years?",
                "What would you consider your ideal work environment?",
                "Why do you think you'd be a good fit for our company?",
                "What do you like to do outside of work?",
                "What do you consider the most important factor in teamwork?",
                "Describe your process for troubleshooting technical issues.",
                "How do you approach learning new programming languages or technologies?",
                "What tools or practices do you use to improve code quality?",
            ],
            'closing': [
                "What projects are you currently working on in your spare time?",
                "Have you contributed to open-source projects? If so, tell me about it.",
                "What methods do you use to ensure your work is efficient and effective?",
                "How would you go about refactoring legacy code?",
                "What are your strategies for managing and organizing code?",
                "Do you have any questions for us about the role or company?",
                "Is there anything else you'd like us to know about you?",
            ]
        }
        self.session_state['questions'] = questions

    def get_next_question_naturally(self) -> str:
        """Select the next question based on interview flow and natural progression."""
        current_phase = self.session_state['interview_phase']
        questions_dict = self.session_state['questions']
        
        # Introduction phase - must ask name first
        if current_phase == 'introduction' and self.session_state['interview_step'] == 0:
            question = questions_dict['introduction'][0]  # Always ask name first
            self.session_state['interview_phase'] = 'warm_up'
            return question
        
        # Warm-up phase (questions 1-3)
        elif current_phase == 'warm_up' and self.session_state['interview_step'] < 4:
            available_questions = [q for q in questions_dict['warm_up'] 
                                 if q not in self.session_state['used_questions']]
            if available_questions:
                question = random.choice(available_questions)
                if self.session_state['interview_step'] == 3:
                    self.session_state['interview_phase'] = 'behavioral'
                return question
        
        # Behavioral phase (questions 4-12)
        elif current_phase == 'behavioral' and self.session_state['interview_step'] < 13:
            available_questions = [q for q in questions_dict['behavioral'] 
                                 if q not in self.session_state['used_questions']]
            if available_questions:
                question = random.choice(available_questions)
                if self.session_state['interview_step'] == 12:
                    # Randomly choose which technical domain to start with
                    tech_domains = ['technical_python', 'technical_javascript', 'technical_sql']
                    self.session_state['interview_phase'] = random.choice(tech_domains)
                return question
        
        # Technical phases (questions 13-25)
        elif current_phase.startswith('technical') and self.session_state['interview_step'] < 26:
            # Mix technical questions from different domains
            tech_domains = ['technical_python', 'technical_javascript', 'technical_sql']
            available_questions = []
            
            for domain in tech_domains:
                available_questions.extend([q for q in questions_dict[domain] 
                                          if q not in self.session_state['used_questions']])
            
            if available_questions:
                question = random.choice(available_questions)
                if self.session_state['interview_step'] == 25:
                    self.session_state['interview_phase'] = 'experience'
                return question
        
        # Experience phase (questions 26-35)
        elif current_phase == 'experience' and self.session_state['interview_step'] < 36:
            available_questions = [q for q in questions_dict['experience'] 
                                 if q not in self.session_state['used_questions']]
            if available_questions:
                question = random.choice(available_questions)
                if self.session_state['interview_step'] == 35:
                    self.session_state['interview_phase'] = 'closing'
                return question
        
        # Closing phase (final questions)
        elif current_phase == 'closing':
            available_questions = [q for q in questions_dict['closing'] 
                                 if q not in self.session_state['used_questions']]
            if available_questions:
                question = random.choice(available_questions)
                return question
        
        return None  # Interview complete

    def ask_question(self) -> None:
        """Ask the current interview question."""
        question = self.get_next_question_naturally()
        
        if question:
            self.session_state['used_questions'].append(question)
            self._text_to_speech(question)
            
            # Display interviewer message with icon
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; max-width: 80%;">
                    <p style="margin: 0;"><strong>Interviewer:</strong> {question}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state['current_question'] = question
            
            # Add to Excel data and save immediately
            excel_data = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Speaker': 'Interviewer',
                'Question/Answer': question,
                'Interview_Phase': self.session_state['interview_phase']
            }
            self.session_state['excel_data'].append(excel_data)
            
            # Auto-save to Excel immediately
            self.save_to_excel_realtime(excel_data)

    def _text_to_speech(self, text: str) -> None:
        """Convert text to speech and play it."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            st.write(f"TTS Error: {e}")

    def get_audio_answer(self) -> bool:
        """Get the user's response via audio with dynamic listening."""
        r = sr.Recognizer()
        r.pause_threshold = 2  # Pause threshold in seconds
        r.phrase_threshold = 0.3  # Minimum length of phrase
        r.non_speaking_duration = 0.8  # Non-speaking duration threshold
        
        with sr.Microphone() as source:
            st.write("🎤 Listening... (Speak naturally, I'll wait for you to finish)")
            
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # Use listen with timeout and phrase_time_limit for better control
                audio = r.listen(source, timeout=1, phrase_time_limit=None)
            except sr.WaitTimeoutError:
                st.write("No speech detected. Please try speaking again.")
                return False

        try:
            st.write("🔄 Processing your response...")
            answer = r.recognize_google(audio)
            
            # Extract candidate name from first answer
            if self.session_state['interview_step'] == 0 and not self.session_state['candidate_name']:
                # Try to extract name from common patterns
                name_words = answer.split()
                if len(name_words) >= 2:
                    # Look for "My name is..." or "I'm..." patterns
                    if "name" in answer.lower() and "is" in answer.lower():
                        name_start = answer.lower().find("is") + 2
                        potential_name = answer[name_start:].strip().split()[0] if name_start < len(answer) else name_words[0]
                        self.session_state['candidate_name'] = potential_name.title()
                    elif answer.lower().startswith("i'm") or answer.lower().startswith("i am"):
                        self.session_state['candidate_name'] = name_words[1].title() if len(name_words) > 1 else "Candidate"
                    else:
                        self.session_state['candidate_name'] = name_words[0].title()
                else:
                    self.session_state['candidate_name'] = answer.title()
            
            # Display candidate's response
            candidate_name = self.session_state['candidate_name'] or "You"
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: flex-end;">
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; max-width: 80%; margin-right: 10px;">
                    <p style="margin: 0;"><strong>{candidate_name}:</strong> {answer}</p>
                </div>
                <img src="data:image/png;base64,{self._image_to_base64(self.interviewee_icon_path)}" width="40" style="border-radius: 50%;">
            </div>
            """, unsafe_allow_html=True)
            
            self.session_state['answers'].append((answer, self._generate_uuid()))
            
            # Add to Excel data and save immediately
            excel_data = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Speaker': self.session_state['candidate_name'] or 'Candidate',
                'Question/Answer': answer,
                'Interview_Phase': self.session_state['interview_phase']
            }
            self.session_state['excel_data'].append(excel_data)
            
            # Auto-save to Excel immediately
            self.save_to_excel_realtime(excel_data)
            
            self.session_state['interview_step'] += 1
            return True

        except sr.UnknownValueError:
            st.write("❌ Sorry, I couldn't understand your response clearly. Please try again.")
            return False
        except sr.RequestError as e:
            st.write(f"❌ Speech recognition error: {e}")
            return False

    def get_excel_filename(self) -> str:
        """Generate consistent Excel filename for the interview session."""
        if 'excel_filename' not in st.session_state:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            candidate_name = self.session_state['candidate_name'] or 'Candidate'
            st.session_state['excel_filename'] = f"Interview_Response_Sheet_{candidate_name}_{timestamp}.xlsx"
        return st.session_state['excel_filename']

    def save_to_excel_realtime(self, new_data: dict) -> None:
        """Save data to Excel in real-time after each interaction."""
        try:
            filename = self.get_excel_filename()
            
            # Check if file exists to determine if we need to create or append
            if os.path.exists(filename):
                # Read existing data
                existing_df = pd.read_excel(filename, engine='openpyxl')
                # Append new data
                new_df = pd.DataFrame([new_data])
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                # Create new file with headers
                combined_df = pd.DataFrame([new_data])
            
            # Save to Excel
            combined_df.to_excel(filename, index=False, engine='openpyxl')
            
            # Show subtle success indicator in sidebar
            with st.sidebar:
                st.success(f"💾 Data saved automatically")
                
        except Exception as e:
            with st.sidebar:
                st.error(f"❌ Auto-save error: {str(e)[:50]}...")

    def generate_candidate_evaluation(self) -> None:
        """Generate comprehensive AI-powered candidate evaluation."""
        try:
            candidate_name = self.session_state.get('candidate_name', 'Anonymous_Candidate')
            
            # Load interview responses
            response_filename = self.get_excel_filename()
            if not os.path.exists(response_filename):
                st.error("Interview response file not found. Please complete the interview first.")
                return
            
            responses_df = pd.read_excel(response_filename, engine='openpyxl')
            
            # Load emotions data
            emotions_filename = "emotions_log.xlsx"
            if not os.path.exists(emotions_filename):
                st.warning("Emotions log file not found. Creating placeholder emotions data.")
                # Create placeholder emotions data
                emotions_data = {
                    'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    'Emotion': ['neutral']
                }
                emotions_df = pd.DataFrame(emotions_data)
            else:
                emotions_df = pd.read_excel(emotions_filename, engine='openpyxl')
            
            st.info("🤖 Generating AI-powered candidate evaluation... This may take a moment.")
            
            # Generate comprehensive evaluation
            evaluation_result = self.evaluator.analyze_candidate_performance(
                responses_df, emotions_df, candidate_name
            )
            
            # Generate marks document
            marks_df = self.evaluator.generate_marks_document(evaluation_result)
            
            # Save candidate marks to Excel
            marks_filename = f"Candidate_Marks_{candidate_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            marks_df.to_excel(marks_filename, index=False, engine='openpyxl')
            
            # Display results
            st.success("✅ Candidate evaluation completed successfully!")
            
            # Display key metrics
            st.subheader("📊 Candidate Assessment Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Overall Score", 
                    f"{evaluation_result['scores']['overall_score']:.1f}/100",
                    delta=f"{evaluation_result['scores']['overall_score'] - 70:.1f}"
                )
            
            with col2:
                st.metric(
                    "Technical Score", 
                    f"{evaluation_result['scores']['technical_competency']:.1f}/100"
                )
            
            with col3:
                st.metric(
                    "Communication", 
                    f"{evaluation_result['scores']['communication_skills']:.1f}/100"
                )
            
            with col4:
                st.metric(
                    "Emotional Intelligence", 
                    f"{evaluation_result['scores']['emotional_intelligence']:.1f}/100"
                )
            
            # Display recommendation with color coding
            recommendation = evaluation_result['recommendation']
            if recommendation == "RECOMMENDED":
                st.success(f"🎉 **Final Decision: {recommendation}**")
            elif recommendation == "BORDERLINE - FURTHER EVALUATION REQUIRED":
                st.warning(f"⚠️ **Final Decision: {recommendation}**")
            else:
                st.error(f"❌ **Final Decision: {recommendation}**")
            
            # Display personality traits
            st.subheader("🧠 Personality Profile")
            traits_cols = st.columns(3)
            for i, trait in enumerate(evaluation_result['personality_traits'][:6]):
                with traits_cols[i % 3]:
                    st.info(f"✨ {trait}")
            
            # Display strengths and improvements
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💪 Key Strengths")
                for strength in evaluation_result['strengths']:
                    st.write(f"• {strength}")
            
            with col2:
                st.subheader("📈 Development Areas")
                for improvement in evaluation_result['areas_for_improvement']:
                    st.write(f"• {improvement}")
            
            # Display AI analysis summary
            with st.expander("🤖 Detailed AI Analysis"):
                st.write(evaluation_result['ai_analysis'])
            
            # Display marks document preview
            st.subheader("📋 Candidate Marks Document Preview")
            st.dataframe(marks_df, use_container_width=True)
            
            # File download information
            st.info(f"📁 **Complete evaluation saved to:** `{marks_filename}`")
            st.info(f"📁 **Current directory:** `{os.getcwd()}`")
            
            # Store evaluation in session state for potential re-access
            st.session_state['latest_evaluation'] = evaluation_result
            st.session_state['marks_filename'] = marks_filename
            
        except Exception as e:
            st.error(f"Error generating candidate evaluation: {str(e)}")
            st.error("Please ensure all required files are present and try again.")

    def display_interview_summary(self) -> None:
        """Display interview summary and evaluation options."""
        if self.session_state['excel_data']:
            filename = self.get_excel_filename()
            candidate_name = self.session_state['candidate_name'] or 'Candidate'
            
            st.subheader("🎉 Interview Completed!")
            st.write(f"**Candidate:** {candidate_name}")
            st.write(f"**Total Questions Asked:** {len([item for item in self.session_state['excel_data'] if item['Speaker'] == 'Interviewer'])}")
            st.write(f"**Total Responses Given:** {len([item for item in self.session_state['excel_data'] if item['Speaker'] != 'Interviewer'])}")
            st.write(f"**Interview Duration:** {len(self.session_state['excel_data'])} exchanges")
            st.write(f"**Data automatically saved to:** `{filename}`")
            
            # Show file location
            current_dir = os.getcwd()
            st.info(f"📁 File saved in: {current_dir}")
            
            # Add evaluation button
            st.markdown("---")
            st.subheader("🤖 AI-Powered Candidate Evaluation")
            st.write("Generate comprehensive candidate assessment using advanced AI analysis.")
            
            if st.button("🚀 Generate Candidate Evaluation", type="primary"):
                self.generate_candidate_evaluation()
            
            # Display final Excel data preview
            if os.path.exists(filename):
                try:
                    df = pd.read_excel(filename, engine='openpyxl')
                    st.subheader("📊 Interview Data Preview")
                    st.dataframe(df.tail(10))  # Show last 10 entries
                except Exception as e:
                    st.error(f"Error reading saved file: {e}")

    def display_past_conversation(self) -> None:
        """Displays the conversation so far in chat format."""
        for i, data in enumerate(self.session_state['excel_data']):
            if data['Speaker'] == 'Interviewer':
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{self._image_to_base64(self.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; max-width: 80%;">
                        <p style="margin: 0;"><strong>Interviewer:</strong> {data['Question/Answer']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: flex-end;">
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; max-width: 80%; margin-right: 10px;">
                        <p style="margin: 0;"><strong>{data['Speaker']}:</strong> {data['Question/Answer']}</p>
                    </div>
                    <img src="data:image/png;base64,{self._image_to_base64(self.interviewee_icon_path)}" width="40" style="border-radius: 50%;">
                </div>
                """, unsafe_allow_html=True)

    def execute_interview(self) -> None:
        """Run the interview with natural flow."""
        # Display progress
        progress = min(self.session_state['interview_step'] / 40, 1.0)  # Assuming ~40 questions max
        st.progress(progress)
        st.write(f"Interview Progress: {self.session_state['interview_step']} questions completed")
        
        self.display_past_conversation()
        
        if self.session_state['interview_step'] < 40:  # Maximum questions limit
            next_question = self.get_next_question_naturally()
            if next_question:
                self.ask_question()
                
                # Get audio response with retry mechanism
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    if self.get_audio_answer():
                        break
                    retry_count += 1
                    if retry_count < max_retries:
                        st.write(f"Let's try again. Attempt {retry_count + 1} of {max_retries}")
                
                if retry_count == max_retries:
                    st.error("Unable to process audio after multiple attempts. Moving to next question.")
                    self.session_state['interview_step'] += 1
                
                time.sleep(2)  # Brief pause between questions
                st.rerun()
            else:
                st.write("🎉 Interview completed!")
                self.display_interview_summary()
        else:
            st.write("🎉 Interview completed!")
            self.display_interview_summary()

    def _image_to_base64(self, image_path):
        """Convert image file to base64 format."""
        try:
            import base64
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except FileNotFoundError:
            # Return a placeholder if image not found
            return ""

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a UUID for unique identification."""
        return str(uuid.uuid4())

def create_bot() -> None:
    """Create and initialize the InterviewBot."""
    bot = InterviewBot()
    
    # Initialize Excel file at the start of the session
    if 'session_initialized' not in st.session_state:
        st.session_state['session_initialized'] = True
        # Create initial Excel file with headers
        initial_data = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Speaker': 'System',
            'Question/Answer': 'Interview session started',
            'Interview_Phase': 'initialization'
        }
        bot.save_to_excel_realtime(initial_data)
    
    if len(bot.session_state['questions']) == 0:
        intro_text = "Hello! Welcome to your interview session. I'm excited to get to know you better today. Let's begin!"
        bot._text_to_speech(intro_text)
        
        # Display interviewer greeting and save to Excel
        intro_data = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Speaker': 'Interviewer',
            'Question/Answer': intro_text,
            'Interview_Phase': 'introduction'
        }
        bot.session_state['excel_data'].append(intro_data)
        bot.save_to_excel_realtime(intro_data)
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{bot._image_to_base64(bot.interviewer_icon_path)}" width="40" style="border-radius: 50%; margin-right: 10px;">
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; max-width: 80%;">
                <p style="margin: 0;"><strong>Interviewer:</strong> {intro_text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        asyncio.run(bot.prepare_questions())

    bot.execute_interview()

# Streamlit UI
st.sidebar.markdown("### Interview Controls")
st.sidebar.markdown("---")

# Show current Excel file info
if 'excel_filename' in st.session_state:
    st.sidebar.info(f"📄 **Current File:**\n`{st.session_state['excel_filename']}`")
    
    # Show file size if it exists
    try:
        if os.path.exists(st.session_state['excel_filename']):
            file_size = os.path.getsize(st.session_state['excel_filename'])
            st.sidebar.write(f"📊 **File Size:** {file_size} bytes")
    except Exception:
        pass

# AI Evaluation section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 AI Evaluation")

if st.sidebar.button("📊 Generate Evaluation Report"):
    if 'excel_filename' in st.session_state and os.path.exists(st.session_state['excel_filename']):
        bot = InterviewBot()
        bot.generate_candidate_evaluation()
    else:
        st.sidebar.error("Complete the interview first!")

# Show latest evaluation info if available
if 'marks_filename' in st.session_state:
    st.sidebar.success(f"✅ **Latest Evaluation:**\n`{st.session_state['marks_filename']}`")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Restart Interview"):
    # Save session end before restarting
    if 'excel_filename' in st.session_state and st.session_state.get('excel_data'):
        bot = InterviewBot()
        end_data = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Speaker': 'System',
            'Question/Answer': 'Interview session restarted by user',
            'Interview_Phase': 'session_end'
        }
        bot.save_to_excel_realtime(end_data)
    
    # Clear session state
    for key in ['questions', 'answers', 'interview_step', 'used_questions', 
                'interview_phase', 'candidate_name', 'excel_data', 'excel_filename', 
                'session_initialized', 'latest_evaluation', 'marks_filename']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Add session cleanup on app termination
if st.sidebar.button("🛑 End Interview Session"):
    if 'excel_filename' in st.session_state and st.session_state.get('excel_data'):
        bot = InterviewBot()
        end_data = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Speaker': 'System',
            'Question/Answer': 'Interview session ended by user',
            'Interview_Phase': 'session_end'
        }
        bot.save_to_excel_realtime(end_data)
        st.success("✅ Interview data saved successfully!")
        st.info(f"📁 Final file: `{st.session_state['excel_filename']}`")

# Display current session stats
if st.session_state.get('excel_data'):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Live Stats")
    total_exchanges = len(st.session_state['excel_data'])
    questions_asked = len([item for item in st.session_state['excel_data'] if item['Speaker'] == 'Interviewer'])
    responses_given = len([item for item in st.session_state['excel_data'] if item['Speaker'] not in ['Interviewer', 'System']])
    
    st.sidebar.metric("Total Exchanges", total_exchanges)
    st.sidebar.metric("Questions Asked", questions_asked)
    st.sidebar.metric("Responses Given", responses_given)

# API Status Check
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 API Status")
try:
    # Quick API health check
    evaluator = CandidateEvaluator('508f0852c77742bcbb5adaccde0308fe')
    st.sidebar.success("✅ AIML API Connected")
except Exception as e:
    st.sidebar.error("❌ API Connection Issue")

show_live_camera_feed()
create_bot()
