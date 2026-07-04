import streamlit as st
from utils.auth import check_auth, logout
from utils.database import get_all_scores_for_user, get_all_quizzes

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

check_auth()

with st.sidebar:
    st.header(f"👤 Welcome, {st.session_state.username}!")
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()

st.title("📚 Dashboard")
st.markdown("Welcome to your Intelligent Quiz Generator hub!")

scores = get_all_scores_for_user(st.session_state.user_id)
all_quizzes = get_all_quizzes(st.session_state.user_id)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Quizzes Generated", len(all_quizzes))
with col2:
    total_quizzes_taken = len(scores)
    st.metric("Quizzes Attempted", total_quizzes_taken)
with col3:
    if scores:
        avg_score = sum(s['score']/s['total'] for s in scores) / len(scores) * 100
        st.metric("Average Score", f"{avg_score:.1f}%")
    else:
        st.metric("Average Score", "N/A")

st.markdown("---")
st.subheader("🗂️ Quizzes by Category")

if not all_quizzes:
    st.info("You haven't generated any quizzes yet.")
else:
    # Group quizzes by category
    grouped_quizzes = {}
    for q in all_quizzes:
        cat = q['category_name']
        if cat not in grouped_quizzes:
            grouped_quizzes[cat] = []
        grouped_quizzes[cat].append(q)
        
    for cat, quizzes in grouped_quizzes.items():
        with st.expander(f"📁 Category: {cat} ({len(quizzes)} quizzes)", expanded=True):
            for q in quizzes:
                st.markdown(f"- **{q['topic']}** | {q['difficulty']} difficulty | {q['num_q']} Qs | *{q['created_at']}*")

st.markdown("---")
if st.button("🚀 Generate New Quiz", type="primary", use_container_width=True):
    st.switch_page("pages/02_Quiz_Generator.py")
