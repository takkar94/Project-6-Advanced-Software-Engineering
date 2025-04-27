import sqlite3
import os

# Define proper database folder and path
DB_FOLDER = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_FOLDER, "tlx_app.db")

def get_db_path():
    return DB_PATH

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Users table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('employee', 'manager')) NOT NULL
        )
    """)

    # --- TLX Entries table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tlx_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mental INTEGER,
            physical INTEGER,
            temporal INTEGER,
            performance INTEGER,
            effort INTEGER,
            frustration INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # --- App Usage table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            app TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # --- Usability Feedback table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usability_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            usability_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # --- Tasks table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# --- Save TLX result ---
def save_tlx_result_to_db(result: dict, user_id: int):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tlx_entries (user_id, mental, physical, temporal, performance, effort, frustration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            result.get("Mental", 0),
            result.get("Physical", 0),
            result.get("Temporal", 0),
            result.get("Performance", 0),
            result.get("Effort", 0),
            result.get("Frustration", 0)
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save TLX result: {e}")

# --- Save usability feedback ---
def save_usability_feedback(user_id: int, score: int):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO usability_feedback (user_id, usability_score)
            VALUES (?, ?)
        ''', (user_id, score))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save usability feedback: {e}")

# --- Save Task Completion ---
def save_task(user_id: int, title: str, description: str):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tasks (user_id, title, description)
            VALUES (?, ?, ?)
        ''', (user_id, title, description))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save task: {e}")

# --- Fetch Task Summary for Admin ---
def fetch_tasks_summary():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.name, COUNT(t.id) as task_count
            FROM users u
            LEFT JOIN tasks t ON u.id = t.user_id
            GROUP BY u.id, u.name
        ''')

        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Failed to fetch task summary: {e}")
        return []

# --- Fetch Task Details for Specific Employee ---
def fetch_tasks_by_user(user_id):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT title, description, timestamp
            FROM tasks
            WHERE user_id = ?
        ''', (user_id,))

        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Failed to fetch tasks for user: {e}")
        return []
