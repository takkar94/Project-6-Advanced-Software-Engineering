import sqlite3
import os

# Define database path
DB_FOLDER = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_FOLDER, "tlx_app.db")

def get_db_path():
    return DB_PATH

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('employee', 'manager')) NOT NULL
        )
    """)

    # TLX Entries table
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

    # App Usage table
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

    # Manager Interruption table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_interruptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Usability Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usability_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def save_manager_interruption(user_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO manager_interruptions (user_id)
        VALUES (?)
    ''', (user_id,))

    conn.commit()
    conn.close()

def fetch_manager_interruptions(user_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT timestamp FROM manager_interruptions
        WHERE user_id = ?
    ''', (user_id,))

    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

def save_tlx_result_to_db(result, user_id):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tlx_entries (user_id, mental, physical, temporal, performance, effort, frustration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, result['Mental'], result['Physical'], result['Temporal'], result['Performance'], result['Effort'], result['Frustration']))

    conn.commit()
    conn.close()

def save_usability_feedback(user_id, score):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO usability_feedback (user_id, score)
        VALUES (?, ?)
    ''', (user_id, score))

    conn.commit()
    conn.close()

def save_task(user_id, title, description):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tasks (user_id, title, description)
        VALUES (?, ?, ?)
    ''', (user_id, title, description))

    conn.commit()
    conn.close()

def fetch_tasks_summary():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id, u.name, COUNT(t.id)
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        GROUP BY u.id
    ''')

    results = cursor.fetchall()
    conn.close()
    return results

def fetch_tasks_by_user(user_id):
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
