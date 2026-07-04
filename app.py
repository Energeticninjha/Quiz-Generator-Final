import streamlit as st
import json
from utils.document import extract_text
from utils.ai_generation import generate_quiz

st.set_page_config(page_title="Quiz Generator", page_icon="📝", layout="centered")
st.title("📚 Intelligent Quiz Generator")
st.markdown("**Upload your notes, textbook, or document and get a smart quiz instantly**")

# Initialize Session State
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

import os
api_key = os.getenv("GEMINI_API_KEY")

# File Upload
uploaded_file = st.file_uploader(
    "Upload your document", 
    type=['pdf', 'docx', 'txt', 'md', 'py', 'java', 'js', 'cpp']
)

if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    document_text = extract_text(uploaded_file)
    
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
            st.error("API Key is missing. Please configure it in your environment.")
        elif not document_text.strip():
            st.error("Could not extract text from the uploaded document. Please try another file.")
        else:
            with st.spinner("Generating intelligent quiz using Gemini AI..."):
                try:
                    quiz_json = generate_quiz(api_key, document_text, num_q, difficulty, q_types)
                    
                    # Reset state for new quiz
                    st.session_state.quiz_data = quiz_json
                    st.session_state.current_question_index = 0
                    st.session_state.score = 0
                    st.session_state.interactive = False
                    st.session_state.feedback = None
                    
                    st.success("Quiz Generated Successfully!")
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse the quiz format. Please try generating again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Display the Quiz if it exists
if st.session_state.quiz_data:
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
                        
                        if is_correct:
                            st.session_state.score += 1
                            st.session_state.feedback = ("success", f"Correct! {q.get('explanation', '')}")
                        else:
                            st.session_state.feedback = ("error", f"Incorrect. The right answer is: {q['answer']}. {q.get('explanation', '')}")
                        
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
            if st.button("Retake Quiz"):
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.feedback = None
                st.rerun()

st.caption("Built by D M Dharshini Sree")
