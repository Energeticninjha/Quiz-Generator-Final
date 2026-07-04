import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import check_auth, logout
from utils.database import get_all_scores_for_user

st.set_page_config(page_title="Progress Report", page_icon="📈", layout="wide")

check_auth()

with st.sidebar:
    st.header(f"👤 Welcome, {st.session_state.username}!")
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()

st.title("📈 Progress Report")
st.markdown("Track your learning progress and analyze your quiz performance over time.")

scores = get_all_scores_for_user(st.session_state.user_id)

if not scores:
    st.info("You haven't completed any quizzes yet. Complete a quiz to see your progress here!")
else:
    # Prepare DataFrame
    df = pd.DataFrame(scores)
    # Calculate accuracy percentage
    df['accuracy'] = (df['score'] / df['total']) * 100
    df['completed_at'] = pd.to_datetime(df['completed_at'])
    df['date'] = df['completed_at'].dt.date

    # Row 1: Overall Stats
    overall_accuracy = df['score'].sum() / df['total'].sum() * 100
    total_quizzes = len(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Quizzes Attempted", total_quizzes)
    with col2:
        st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
        
    st.markdown("---")
    
    # Row 2: Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Score Trend Over Time")
        # Line chart for accuracy over time
        trend_df = df.groupby('date')['accuracy'].mean().reset_index()
        fig1 = px.line(trend_df, x='date', y='accuracy', markers=True, 
                       labels={'accuracy': 'Accuracy (%)', 'date': 'Date'})
        fig1.update_traces(line_color='#0068c9', line_width=3, marker=dict(size=8))
        fig1.update_layout(yaxis_range=[0, 105], margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.subheader("Performance by Difficulty")
        # Bar chart for difficulty
        diff_df = df.groupby('difficulty')['accuracy'].mean().reset_index()
        fig2 = px.bar(diff_df, x='difficulty', y='accuracy', color='difficulty',
                      labels={'accuracy': 'Accuracy (%)', 'difficulty': 'Difficulty Level'},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(yaxis_range=[0, 105], showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Quiz Log")
    st.dataframe(
        df[['completed_at', 'topic', 'difficulty', 'score', 'total', 'accuracy']].sort_values('completed_at', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "completed_at": "Date & Time",
            "topic": "Topic",
            "difficulty": "Difficulty",
            "score": "Score",
            "total": "Total Questions",
            "accuracy": st.column_config.NumberColumn("Accuracy (%)", format="%.1f%%")
        }
    )
