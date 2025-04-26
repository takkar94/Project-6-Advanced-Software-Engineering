from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import sqlite3
from modules.database.db import get_db_path

class TLXStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.refresh_stats()

    def refresh_stats(self):
        # Clear old widgets
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()

            # Get latest 5 entries
            cursor.execute("""
                SELECT mental, physical, temporal, performance, effort, frustration, timestamp
                FROM tlx_entries
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            rows = cursor.fetchall()
            conn.close()

            if rows:
                for row in rows:
                    mental, physical, temporal, performance, effort, frustration, timestamp = row
                    summary = (
                        f"🧠 Mental: {mental} | 💪 Physical: {physical} | ⏱ Temporal: {temporal} | "
                        f"🎯 Performance: {performance} | 🔧 Effort: {effort} | 😖 Frustration: {frustration} | 🕒 {timestamp}"
                    )
                    label = QLabel(summary)
                    self.layout.addWidget(label)
            else:
                self.layout.addWidget(QLabel("No TLX data yet."))

        except Exception as e:
            self.layout.addWidget(QLabel(f"Error loading TLX data: {e}"))
