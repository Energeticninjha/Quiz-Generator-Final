import streamlit as st
import json
import os
from dotenv import load_dotenv
from utils.auth import check_auth, logout
from utils.document import extract_text
from utils.ai_generation import generate_quiz
from utils.database import save_quiz, save_score, get_user_categories, create_category

# Load environment variables explicitly
load_dotenv()

st.set_page_config(page_title="Quiz Generator", page_icon="📝", layout="centered")

check_auth()

with st.sidebar:
    st.header(f"👤 Welcome, {st.session_state.username}!")
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()

st.title("📚 Intelligent Quiz Generator")
st.markdown("**Upload your notes, textbook, or document and get a smart quiz instantly**")

# Initialize Session State for Quiz if not exists
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'interactive' not in st.session_state:
    st.session_state.interactive = False
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'current_quiz_id' not in st.session_state:
    st.session_state.current_quiz_id = None
if 'score_saved' not in st.session_state:
    st.session_state.score_saved = False
if 'weak_topics' not in st.session_state:
    st.session_state.weak_topics = []
if 'strong_topics' not in st.session_state:
    st.session_state.strong_topics = []

api_key = os.getenv("GEMINI_API_KEY")

# File Upload
uploaded_file = st.file_uploader(
    "Upload your document", 
    type=['pdf', 'docx', 'txt', 'md', 'py', 'java', 'js', 'cpp']
)

if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    document_text = extract_text(uploaded_file)
    
    # Category Selection
    st.markdown("### 🏷️ Category")
    categories = get_user_categories(st.session_state.user_id)
    cat_options = ["None"] + [c['name'] for c in categories] + ["+ Create New Category"]
    selected_cat = st.selectbox("Select or Create a Category", cat_options)
    
    new_cat_name = ""
    if selected_cat == "+ Create New Category":
        new_cat_name = st.text_input("New Category Name")
        
    st.markdown("### ⚙️ Quiz Settings")
    col1, col2 = st.columns(2)
    with col1:
        num_q = st.slider("Number of Questions", 5, 20, 10)
        difficulty = st.selectbox("Difficulty", ["Mixed", "Easy", "Medium", "Hard"])
    with col2:
        q_types = st.multiselect("Question Types", 
                               ["Multiple Choice", "True/False", "Short Answer", "Coding"],
                               default=["Multiple Choice", "Short Answer"])
    
    if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
        if not api_key:
            st.error("API Key is missing. Please configure it in your .env file.")
        elif not document_text.strip():
            st.error("Could not extract text from the uploaded document. Please try another file.")
        elif selected_cat == "+ Create New Category" and not new_cat_name.strip():
            st.error("Please provide a name for the new category.")
        else:
            with st.spinner("Generating intelligent quiz using Gemini AI..."):
                try:
                    quiz_json = generate_quiz(api_key, document_text, num_q, difficulty, q_types)
                    
                    # Resolve Category ID
                    cat_id = None
                    if selected_cat == "+ Create New Category":
                        cat_id = create_category(st.session_state.user_id, new_cat_name.strip())
                    elif selected_cat != "None":
                        cat_id = next(c['id'] for c in categories if c['name'] == selected_cat)
                    
                    # Save to DB for the user
                    topic = uploaded_file.name
                    quiz_id = save_quiz(topic, num_q, difficulty, quiz_json, st.session_state.user_id, cat_id)
                    
                    # Reset state for new quiz
                    st.session_state.quiz_data = quiz_json
                    st.session_state.current_question_index = 0
                    st.session_state.score = 0
                    st.session_state.interactive = False
                    st.session_state.feedback = None
                    st.session_state.current_quiz_id = quiz_id
                    st.session_state.score_saved = False
                    st.session_state.weak_topics = []
                    st.session_state.strong_topics = []
                    
                    st.success("Quiz Generated Successfully!")
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse the quiz format. Please try generating again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Display the Quiz if it exists
if st.session_state.quiz_data:
    st.markdown("---")
    if not st.session_state.interactive:
        st.markdown("### 📝 Generated Quiz Preview")
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            if q.get('options'):
                for opt in q['options']:
                    st.markdown(f"- {opt}")
            st.markdown(f"*Answer: {q['answer']}*")
            st.markdown("---")
            
        if st.button("Start Interactive Quiz", type="primary"):
            st.session_state.interactive = True
            st.rerun()

    else:
        st.markdown("### 🎯 Interactive Mode")
        
        quiz = st.session_state.quiz_data
        idx = st.session_state.current_question_index
        
        if idx < len(quiz):
            q = quiz[idx]
            st.progress((idx) / len(quiz))
            st.write(f"**Question {idx + 1} of {len(quiz)}**")
            st.subheader(q['question'])
            
            with st.form(key=f"question_form_{idx}"):
                user_answer = ""
                if q.get('options'):
                    user_answer = st.radio("Choose your answer:", q['options'], index=None)
                else:
                    user_answer = st.text_input("Your Answer:")
                    
                submit = st.form_submit_button("Submit Answer")
                
                if submit:
                    if not user_answer:
                        st.warning("Please provide an answer before submitting.")
                    else:
                        is_correct = False
                        if q.get('options'):
                            is_correct = (user_answer == q['answer'])
                        else:
                            is_correct = (q['answer'].lower() in user_answer.lower() or user_answer.lower() in q['answer'].lower())
                        
                        # Generate a short topic label from the question (first 50 chars)
                        short_topic = q['question'][:50] + "..." if len(q['question']) > 50 else q['question']
                        
                        if is_correct:
                            st.session_state.score += 1
                            st.session_state.feedback = ("success", f"Correct! {q.get('explanation', '')}")
                            st.session_state.strong_topics.append(short_topic)
                        else:
                            st.session_state.feedback = ("error", f"Incorrect. The right answer is: {q['answer']}. {q.get('explanation', '')}")
                            st.session_state.weak_topics.append(short_topic)
                        
            if st.session_state.feedback:
                f_type, f_msg = st.session_state.feedback
                if f_type == "success":
                    st.success(f_msg)
                else:
                    st.error(f_msg)
                    
                if st.button("Next Question"):
                    st.session_state.current_question_index += 1
                    st.session_state.feedback = None
                    st.rerun()
                    
        else:
            st.success("🎉 Quiz Completed!")
            st.balloons()
            st.markdown(f"### Your Score: {st.session_state.score} / {len(quiz)}")
            
            if st.session_state.current_quiz_id and not st.session_state.score_saved:
                save_score(st.session_state.current_quiz_id, 
                           st.session_state.score, 
                           len(quiz), 
                           st.session_state.user_id,
                           st.session_state.weak_topics,
                           st.session_state.strong_topics)
                st.session_state.score_saved = True
                
            if st.button("Retake Quiz"):
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.feedback = None
                st.session_state.score_saved = False
                st.session_state.weak_topics = []
                st.session_state.strong_topics = []
                st.rerun()
