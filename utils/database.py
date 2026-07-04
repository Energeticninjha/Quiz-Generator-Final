import psycopg2
from psycopg2 import pool
import json
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Use Streamlit caching to keep the pool alive across page reloads!
@st.cache_resource
def get_connection_pool():
    try:
        # Try to get from environment first
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Fallback to Streamlit secrets for Cloud deployment
        if not DATABASE_URL:
            try:
                DATABASE_URL = st.secrets["DATABASE_URL"]
            except FileNotFoundError:
                pass # Secrets file missing

        if not DATABASE_URL:
            st.error("DATABASE_URL is completely missing! Check your Streamlit Secrets.")
            st.stop()

        # Creates a pool of connections so we don't have to reconnect every time
        return pool.ThreadedConnectionPool(1, 10, DATABASE_URL, sslmode='require')
    except Exception as e:
        st.error(f"FATAL DATABASE ERROR: {str(e)}")
        st.stop()

def get_connection():
    return get_connection_pool().getconn()

def release_connection(conn):
    try:
        get_connection_pool().putconn(conn)
    except Exception:
        pass

def format_ist(utc_datetime):
    """Convert UTC datetime object or string to IST."""
    try:
        if isinstance(utc_datetime, str):
            utc_dt = datetime.strptime(utc_datetime, "%Y-%m-%d %H:%M:%S")
            utc_dt = pytz.utc.localize(utc_dt)
        else:
            if utc_datetime.tzinfo is None:
                utc_dt = pytz.utc.localize(utc_datetime)
            else:
                utc_dt = utc_datetime
        
        ist_dt = utc_dt.astimezone(pytz.timezone('Asia/Kolkata'))
        return ist_dt.strftime("%Y-%m-%d %I:%M %p IST")
    except Exception as e:
        return str(utc_datetime)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            hashed_password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Create quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id SERIAL PRIMARY KEY,
            topic TEXT,
            num_q INTEGER,
            difficulty TEXT,
            quiz_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    
    # Create scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id SERIAL PRIMARY KEY,
            quiz_id INTEGER,
            score INTEGER,
            total INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            weak_topics TEXT,
            strong_topics TEXT,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    release_connection(conn)

# --- User Functions ---

def create_user(username, email, hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (username, email, hashed_password))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError:
        conn.rollback()
        return None
    finally:
        cursor.close()
        release_connection(conn)

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, hashed_password, created_at FROM users WHERE username = %s', (username,))
    row = cursor.fetchone()
    cursor.close()
    release_connection(conn)
    if row:
        return {'id': row[0], 'username': row[1], 'email': row[2], 'hashed_password': row[3], 'created_at': row[4]}
    return None

# --- Category Functions ---

def create_category(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO categories (user_id, name)
        VALUES (%s, %s)
        RETURNING id
    ''', (user_id, name))
    cat_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    release_connection(conn)
    return cat_id

def get_user_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM categories WHERE user_id = %s ORDER BY name ASC', (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    return [{'id': r[0], 'name': r[1]} for r in rows]

# --- Quiz Functions ---

def save_quiz(topic, num_q, difficulty, quiz_data, user_id, category_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quizzes (topic, num_q, difficulty, quiz_data, user_id, category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (topic, num_q, difficulty, json.dumps(quiz_data), user_id, category_id))
    quiz_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    release_connection(conn)
    return quiz_id

def get_all_quizzes(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.id, q.topic, q.num_q, q.difficulty, q.created_at, q.quiz_data, c.name 
        FROM quizzes q
        LEFT JOIN categories c ON q.category_id = c.id
        WHERE q.user_id = %s 
        ORDER BY q.created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    quizzes = []
    for row in rows:
        quizzes.append({
            'id': row[0],
            'topic': row[1],
            'num_q': row[2],
            'difficulty': row[3],
            'created_at': format_ist(row[4]),
            'quiz_data': json.loads(row[5]),
            'category_name': row[6] if row[6] else "Uncategorized"
        })
    return quizzes

def get_recent_quizzes(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.id, q.topic, q.num_q, q.difficulty, q.created_at, c.name 
        FROM quizzes q
        LEFT JOIN categories c ON q.category_id = c.id
        WHERE q.user_id = %s 
        ORDER BY q.created_at DESC LIMIT %s
    ''', (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    quizzes = []
    for row in rows:
        quizzes.append({
            'id': row[0],
            'topic': row[1],
            'num_q': row[2],
            'difficulty': row[3],
            'created_at': format_ist(row[4]),
            'category_name': row[5] if row[5] else "Uncategorized"
        })
    return quizzes

# --- Score Functions ---

def save_score(quiz_id, score, total, user_id, weak_topics, strong_topics):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scores (quiz_id, score, total, user_id, weak_topics, strong_topics)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (quiz_id, score, total, user_id, json.dumps(weak_topics), json.dumps(strong_topics)))
    conn.commit()
    cursor.close()
    release_connection(conn)

def get_scores_for_quiz(quiz_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT score, total, completed_at, weak_topics, strong_topics FROM scores WHERE quiz_id = %s AND user_id = %s ORDER BY completed_at DESC', (quiz_id, user_id))
    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    scores = []
    for row in rows:
        scores.append({
            'score': row[0],
            'total': row[1],
            'completed_at': format_ist(row[2]),
            'weak_topics': json.loads(row[3]) if row[3] else [],
            'strong_topics': json.loads(row[4]) if row[4] else []
        })
    return scores

def get_all_scores_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.score, s.total, s.completed_at, q.topic, q.difficulty, s.weak_topics, s.strong_topics 
        FROM scores s
        JOIN quizzes q ON s.quiz_id = q.id
        WHERE s.user_id = %s 
        ORDER BY s.completed_at ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    scores = []
    for row in rows:
        scores.append({
            'score': row[0],
            'total': row[1],
            'completed_at': format_ist(row[2]),
            'topic': row[3],
            'difficulty': row[4],
            'weak_topics': json.loads(row[5]) if row[5] else [],
            'strong_topics': json.loads(row[6]) if row[6] else []
        })
    return scores
