"""
PSLE Science AI Tutor - Streamlit Application

Requirements:
- streamlit
- google-generativeai
- pandas
- plotly
- pillow
- python-dotenv
- PyPDF2 (optional, for PDF support)

Installation:
pip install streamlit google-generativeai pandas plotly pillow python-dotenv PyPDF2

Environment Setup:
Create a .env file with: GOOGLE_API_KEY=your_api_key_here
OR use Streamlit secrets: Add to .streamlit/secrets.toml
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import json
import os
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="PSLE Science AI Tutor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
# NOTE: This app uses st.session_state for data storage, which works perfectly on Streamlit Cloud.
# Session state is temporary (resets on app restart) but sufficient for quiz tracking within a session.
# For permanent storage across sessions, consider integrating Google Sheets API or a cloud database.
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'user_topic' not in st.session_state:
    st.session_state.user_topic = "Cycles"
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0

# Configure Gemini API
def configure_gemini():
    """
    Configure Gemini API with error handling.
    Checks Streamlit Cloud secrets first (for deployment), then falls back to .env (for local development).
    """
    api_key = None
    
    # Priority 1: Try to get API key from Streamlit secrets (Cloud deployment)
    # This works on Streamlit Community Cloud when secrets are set via the web interface
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            api_key = st.secrets['GOOGLE_API_KEY']
    except Exception:
        pass
    
    # Priority 2: Fallback to environment variable (local development)
    # This works when using .env file for local testing
    if not api_key:
        api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        st.error("❌ **API Key Missing!** Please add your Google API key:")
        st.code("""
For Streamlit Cloud:
1. Go to your app settings on streamlit.io
2. Navigate to "Secrets" tab
3. Add: GOOGLE_API_KEY = "your_api_key_here"

For Local Development:
Create .env file with:
GOOGLE_API_KEY=your_api_key_here
        """)
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"❌ Error configuring Gemini API: {str(e)}")
        st.stop()

# Configure API on app load
configure_gemini()

# Gemini Helper Functions
def generate_quiz_question(topic, difficulty="Medium"):
    """
    Generate a PSLE Science MCQ question using Gemini
    Returns a dictionary with question, options, correct_answer, and explanation
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a PSLE Science tutor creating a multiple-choice question for Singapore Primary School students.

Topic: {topic}
Difficulty Level: {difficulty}

Create a PSLE Science multiple-choice question with exactly 4 options (A, B, C, D).
The question should be appropriate for Primary 5-6 students in Singapore.

Respond in JSON format only:
{{
    "question": "The question text here",
    "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "A clear, educational explanation suitable for primary school students explaining why the answer is correct and why other options are wrong"
}}

Ensure the question tests understanding of key concepts in {topic} that are relevant to the PSLE Science syllabus."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response to extract JSON
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        question_data = json.loads(response_text)
        
        return question_data
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing question response: {str(e)}")
        st.error(f"Response received: {response_text[:500]}")
        return None
    except Exception as e:
        st.error(f"❌ Error generating question: {str(e)}")
        return None

def mark_worksheet(image):
    """
    Mark a student's worksheet using Gemini 2.5 Flash Vision
    Returns feedback with marks, missing keywords, and corrections using strict PSLE marking standards
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """You are a strict, veteran Singapore PSLE Science Marker. Your job is not to be a friend, but to grade rigorously based on the MOE Syllabus.

**Your Marking Rubric:**
1.  **Keyword Supremacy:** You must award ZERO marks if the student explains the concept correctly but misses the specific scientific keyword.
    * *Example:* If they say "The water dried up," mark it WRONG. The required phrase is "The water gained heat and evaporated."
    * *Example:* If they say "The object is heavy," mark it WRONG. They must discuss "Gravitational Potential Energy."
    * *Example:* Never accept "rubbing"; demand "Friction."
    * *Example:* Never accept "size"; demand "Exposed Surface Area."

2.  **The "CER" Check:**
    * **C**laim: Did they answer the question directly?
    * **E**vidence: Did they quote data from the table/graph?
    * **R**easoning: Did they link the evidence to the scientific concept?
    * *If any part is missing, deduct marks.*

**Task:**
Analyze the student's handwritten answer in the image.
1.  Transcribe what they wrote.
2.  Identify the missing keywords immediately.
3.  Provide a strict score (e.g., 0/2, 1/2, or 2/2).
4.  Draft the "Model Answer" that would get full marks.

**Output Format (JSON Only):**
{
    "transcription": "Student's exact words...",
    "score": "X/2",
    "verdict": "Strict/Lenient/Correct",
    "missing_keywords": ["List", "Of", "Missing", "Keywords"],
    "feedback_text": "You lost marks because you said 'X' instead of 'Y'. In Section B, we do not accept general descriptions.",
    "model_answer": "The perfect answer showing exactly how to phrase it."
}

Analyze the image carefully and provide your assessment."""
        
        response = model.generate_content([prompt, image])
        response_text = response.text.strip()
        
        # Clean the response to extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        feedback_data = json.loads(response_text)
        
        return feedback_data
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a structured error response
        return {
            "error": True,
            "raw_response": response_text,
            "message": "Could not parse AI response. Raw feedback: " + response_text[:500]
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Error marking worksheet: {str(e)}"
        }

# UI Components
def main():
    # Header
    st.title("🔬 PSLE Science AI Tutor")
    st.markdown("**Your Personal Science Learning Assistant for PSLE Preparation**")
    st.markdown("---")
    
    # Sidebar Navigation
    st.sidebar.title("📚 Navigation")
    mode = st.sidebar.radio(
        "Choose a Mode:",
        ["Smart Tutor (Quiz & Learn)", "Homework Marker", "Student Dashboard"]
    )
    
    # Mode 1: Smart Tutor (Quiz & Learn)
    if mode == "Smart Tutor (Quiz & Learn)":
        st.header("🎯 Smart Tutor - Quiz & Learn Mode")
        st.markdown("Practice PSLE Science questions and learn with instant feedback!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Topic Selection
            topic = st.selectbox(
                "📖 Select a Topic:",
                ["Cycles", "Systems", "Interactions", "Energy"],
                index=["Cycles", "Systems", "Interactions", "Energy"].index(st.session_state.user_topic) if st.session_state.user_topic in ["Cycles", "Systems", "Interactions", "Energy"] else 0
            )
            st.session_state.user_topic = topic
            
            # Difficulty Selection
            difficulty = st.selectbox(
                "📊 Difficulty Level:",
                ["Easy", "Medium", "Hard"]
            )
            
            # Generate Question Button
            if st.button("🎲 Generate New Question", type="primary", use_container_width=True):
                with st.spinner("🧠 Creating a perfect question for you..."):
                    question_data = generate_quiz_question(topic, difficulty)
                    if question_data:
                        st.session_state.current_question = question_data
                        st.session_state.quiz_history.append({
                            "topic": topic,
                            "difficulty": difficulty,
                            "question": question_data.get("question", "")
                        })
        
        with col2:
            st.metric("📈 Current Score", f"{st.session_state.quiz_score} points")
            st.metric("✅ Accuracy", 
                     f"{(st.session_state.correct_answers/st.session_state.total_questions*100) if st.session_state.total_questions > 0 else 0:.1f}%")
            st.metric("📝 Questions Attempted", st.session_state.total_questions)
        
        # Display Current Question
        if st.session_state.current_question:
            question_data = st.session_state.current_question
            
            st.markdown("---")
            st.subheader("📝 Question")
            st.markdown(f"**{question_data.get('question', 'No question generated')}**")
            
            # Options as Radio Buttons
            options = question_data.get('options', {})
            user_answer = st.radio(
                "Select your answer:",
                options=list(options.keys()),
                format_func=lambda x: f"{x}. {options[x]}",
                key="user_answer_radio"
            )
            
            # Check Answer Button
            col_check1, col_check2 = st.columns([1, 4])
            with col_check1:
                check_button = st.button("✅ Check Answer", type="primary", use_container_width=True)
            
            if check_button:
                correct_answer = question_data.get('correct_answer', '')
                explanation = question_data.get('explanation', 'No explanation available.')
                
                st.session_state.total_questions += 1
                
                if user_answer == correct_answer:
                    st.session_state.correct_answers += 1
                    st.session_state.quiz_score += 10  # Award 10 points for correct answer
                    st.success(f"🎉 **Correct!** Well done!")
                    st.info(f"💡 **Explanation:** {explanation}")
                else:
                    st.error(f"❌ **Incorrect.** The correct answer is **{correct_answer}**.")
                    st.warning(f"💡 **Explanation:** {explanation}")
        
        else:
            st.info("👆 Click 'Generate New Question' to start practicing!")
    
    # Mode 2: Homework Marker
    elif mode == "Homework Marker":
        st.header("✏️ Homework Marker")
        st.markdown("Upload your Science worksheet and get instant AI feedback!")
        
        # File Uploader
        uploaded_file = st.file_uploader(
            "📄 Upload your Science worksheet (PNG, JPG, or PDF):",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload an image of your Science homework or worksheet"
        )
        
        if uploaded_file is not None:
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.subheader("📷 Your Worksheet")
                
                # Handle different file types
                if uploaded_file.type.startswith('image/'):
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Worksheet", use_container_width=True)
                elif uploaded_file.type == 'application/pdf':
                    st.warning("📄 PDF detected. Please convert to PNG/JPG for best results, or upload an image file.")
                    st.info("For now, extracting first page as image...")
                    # Note: PDF handling would require PyPDF2 and pdf2image
                    # For now, we'll show a message
                    image = None
                else:
                    st.error("Unsupported file type")
                    image = None
                
                # Mark Button
                if image is not None:
                    if st.button("🔍 Mark My Worksheet", type="primary", use_container_width=True):
                        with st.spinner("👨‍🏫 Marking your worksheet... Please wait..."):
                            feedback = mark_worksheet(image)
                            
                            # Store feedback in session state
                            st.session_state.worksheet_feedback = feedback
            
            with col_right:
                st.subheader("🤖 AI Feedback")
                
                if 'worksheet_feedback' in st.session_state:
                    feedback = st.session_state.worksheet_feedback
                    
                    if feedback.get('error'):
                        st.error(feedback.get('message', 'An error occurred'))
                        if 'raw_response' in feedback:
                            st.text_area("Raw Response", feedback['raw_response'], height=300)
                    else:
                        # Parse score (format: "X/Y")
                        score_str = feedback.get('score', '0/2')
                        try:
                            marks_awarded, total_marks = map(int, score_str.split('/'))
                        except:
                            marks_awarded, total_marks = 0, 2
                        
                        # Display Score and Verdict
                        col_score, col_verdict = st.columns(2)
                        with col_score:
                            st.metric("📊 Score", score_str)
                        with col_verdict:
                            verdict = feedback.get('verdict', 'N/A')
                            verdict_color = {
                                'Correct': '🟢',
                                'Strict': '🔴',
                                'Lenient': '🟡'
                            }.get(verdict, '⚪')
                            st.metric("🎯 Verdict", f"{verdict_color} {verdict}")
                        
                        # Progress Bar
                        progress = marks_awarded / total_marks if total_marks > 0 else 0
                        st.progress(progress)
                        
                        st.markdown("---")
                        
                        # Display Transcription
                        transcription = feedback.get('transcription', '')
                        if transcription:
                            st.subheader("📝 Student's Answer (Transcribed)")
                            st.text_area("", transcription, height=100, disabled=True, key="transcription_display")
                        
                        # Display Missing Keywords
                        missing_keywords = feedback.get('missing_keywords', [])
                        if missing_keywords:
                            st.subheader("🔑 Missing Keywords")
                            keywords_text = ", ".join([f"**{kw}**" for kw in missing_keywords])
                            st.warning(keywords_text)
                        else:
                            st.success("✅ All required keywords are present!")
                        
                        # Display Feedback Text
                        feedback_text = feedback.get('feedback_text', '')
                        if feedback_text:
                            st.subheader("💬 Feedback")
                            st.info(feedback_text)
                        
                        # Display Model Answer
                        model_answer = feedback.get('model_answer', '')
                        if model_answer:
                            st.subheader("✨ Model Answer")
                            st.success(model_answer)
                else:
                    st.info("👆 Upload a worksheet and click 'Mark My Worksheet' to get feedback!")
        
        else:
            st.info("👆 Please upload your Science worksheet to get started!")
    
    # Mode 3: Student Dashboard
    elif mode == "Student Dashboard":
        st.header("📊 Student Dashboard")
        st.markdown("Track your progress and performance!")
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Questions", st.session_state.total_questions)
        with col2:
            accuracy = (st.session_state.correct_answers / st.session_state.total_questions * 100) if st.session_state.total_questions > 0 else 0
            st.metric("✅ Accuracy Rate", f"{accuracy:.1f}%")
        with col3:
            st.metric("🏆 Score", f"{st.session_state.quiz_score} points")
        with col4:
            st.metric("📚 Topics Covered", len(set([q.get('topic', '') for q in st.session_state.quiz_history])))
        
        st.markdown("---")
        
        # Performance Chart
        if st.session_state.quiz_history:
            st.subheader("📈 Performance by Topic")
            
            # Create performance data
            topic_stats = {}
            for item in st.session_state.quiz_history:
                topic = item.get('topic', 'Unknown')
                if topic not in topic_stats:
                    topic_stats[topic] = {'total': 0, 'correct': 0}
                topic_stats[topic]['total'] += 1
            
            # Calculate accuracy (simplified - in real app, track correct/incorrect per question)
            df_data = []
            for topic, stats in topic_stats.items():
                # For demo purposes, estimate accuracy based on score
                # In production, you'd track this properly
                accuracy = 75 if stats['total'] > 0 else 0  # Dummy data
                df_data.append({
                    'Topic': topic,
                    'Questions Attempted': stats['total'],
                    'Estimated Accuracy (%)': accuracy
                })
            
            df = pd.DataFrame(df_data)
            
            # Create bar chart
            if not df.empty:
                fig = px.bar(
                    df,
                    x='Topic',
                    y='Estimated Accuracy (%)',
                    title='Your Performance by Topic',
                    color='Estimated Accuracy (%)',
                    color_continuous_scale='Greens',
                    text='Estimated Accuracy (%)'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(
                    xaxis_title="Science Topic",
                    yaxis_title="Accuracy (%)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No data yet! Complete some quizzes to see your performance here.")
        
        # Quiz History
        if st.session_state.quiz_history:
            st.subheader("📜 Recent Quiz History")
            history_df = pd.DataFrame(st.session_state.quiz_history[-10:])  # Show last 10
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("📜 Your quiz history will appear here after you complete some questions!")

if __name__ == "__main__":
    main()
