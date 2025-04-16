from PySide6 import QtWidgets, QtCore
import sqlite3
import os
import bcrypt
from modules.database.db import get_db_path

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setMinimumSize(350, 200)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_btn = QtWidgets.QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)

        self.status_label = QtWidgets.QLabel("")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("👤 Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QtWidgets.QLabel("🔒 Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.status_label)

        self.user_info = None

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.status_label.setText("❌ Enter both email and password.")
            return

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, password_hash, role FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, name, password_hash, role = user
            if bcrypt.checkpw(password.encode(), password_hash.encode()):
                self.user_info = {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "role": role
                }
                self.accept()  # ✅ Login success
                return

        self.status_label.setText("❌ Invalid email or password.")

    def get_user_info(self):
        return self.user_info
