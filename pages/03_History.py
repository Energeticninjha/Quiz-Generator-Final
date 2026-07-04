import streamlit as st
from collections import Counter
from utils.auth import check_auth, logout
from utils.database import get_all_quizzes, get_scores_for_quiz, get_all_scores_for_user

st.set_page_config(page_title="Quiz History", page_icon="🗂️", layout="wide")

check_auth()

with st.sidebar:
    st.header(f"👤 Welcome, {st.session_state.username}!")
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()

st.title("🗂️ Quiz History & Analysis")
st.markdown("Review your past quizzes and see your strongest and weakest areas.")

# Top 3 Weak and Strong Topics Overall
all_scores = get_all_scores_for_user(st.session_state.user_id)
all_weak = []
all_strong = []
for s in all_scores:
    all_weak.extend(s.get('weak_topics', []))
    all_strong.extend(s.get('strong_topics', []))

if all_weak or all_strong:
    st.markdown("### 🏆 Your Overall Topic Performance")
    colA, colB = st.columns(2)
    
    with colA:
        st.success("💪 **Top 3 Strongest Topics**")
        if all_strong:
            top_strong = Counter(all_strong).most_common(3)
            for topic, count in top_strong:
                st.write(f"- {topic} *(Got right {count} times)*")
        else:
            st.write("No strong topics recorded yet.")
            
    with colB:
        st.error("⚠️ **Top 3 Weakest Topics**")
        if all_weak:
            top_weak = Counter(all_weak).most_common(3)
            for topic, count in top_weak:
                st.write(f"- {topic} *(Got wrong {count} times)*")
        else:
            st.write("No weak topics recorded yet.")
    st.markdown("---")

# Quiz History List
st.markdown("### 📜 Past Quizzes")
history = get_all_quizzes(st.session_state.user_id)

if not history:
    st.info("You haven't generated any quizzes yet. Head over to the Quiz Generator to get started!")
else:
    for q in history:
        with st.expander(f"📝 {q['topic']} [{q['category_name']}] - {q['difficulty']} ({q['created_at']})"):
            st.write(f"**Category:** {q['category_name']}")
            st.write(f"**Difficulty:** {q['difficulty']}")
            st.write(f"**Questions:** {q['num_q']}")
            
            scores = get_scores_for_quiz(q['id'], st.session_state.user_id)
            if scores:
                st.markdown("#### Past Attempts")
                for i, s in enumerate(scores):
                    st.markdown(f"**Attempt {len(scores)-i}:** Score {s['score']}/{s['total']} on {s['completed_at']}")
                    
                    if s.get('weak_topics'):
                        st.markdown("<span style='color:red'>**Weak Areas (Wrong Answers):**</span>", unsafe_allow_html=True)
                        for wt in s['weak_topics']:
                            st.write(f"- {wt}")
                            
                    if s.get('strong_topics'):
                        st.markdown("<span style='color:green'>**Strong Areas (Correct Answers):**</span>", unsafe_allow_html=True)
                        for stp in s['strong_topics']:
                            st.write(f"- {stp}")
                    
                    st.divider()
            else:
                st.write("*No completed attempts yet.*")
            
            if st.button("Retake Quiz", key=f"retake_{q['id']}"):
                st.session_state.quiz_data = q['quiz_data']
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.interactive = False
                st.session_state.feedback = None
                st.session_state.current_quiz_id = q['id']
                st.session_state.score_saved = False
                st.session_state.weak_topics = []
                st.session_state.strong_topics = []
                st.switch_page("pages/02_Quiz_Generator.py")
