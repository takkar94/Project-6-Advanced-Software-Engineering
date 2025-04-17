import sqlite3
import bcrypt
import os

db_path = os.path.join("modules", "database", "tlx_app.db")

users = [
    {"name": "Aaditya Sharma", "email": "aaditya@example.com", "password": "securepass", "role": "employee"},
    {"name": "Admin Manager", "email": "admin@example.com", "password": "adminpass", "role": "manager"}
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for user in users:
    password_hash = bcrypt.hashpw(user["password"].encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (user["name"], user["email"], password_hash, user["role"]))
        print(f"Added user: {user['name']} ({user['role']})")
    except sqlite3.IntegrityError:
        print(f"⚠️ User already exists: {user['email']}")

conn.commit()
conn.close()
