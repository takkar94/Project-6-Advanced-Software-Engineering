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

    conn.commit()
    conn.close()

# Save a manager interruption event
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

# Fetch all manager interruptions for a user
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
