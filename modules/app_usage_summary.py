from PySide6 import QtWidgets
import sqlite3
from collections import defaultdict
from modules.database.db import get_db_path

class AppUsageSummary(QtWidgets.QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setMinimumHeight(200)
        self.setStyleSheet("font-size: 14px; padding: 10px;")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("📋 App usage summary will appear here.")
        self.layout.addWidget(self.label)

        self.refresh_summary()

    def refresh_summary(self):
        usage_data = defaultdict(int)

        try:
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT app, SUM(duration)
                FROM app_usage
                WHERE user_id = ?
                GROUP BY app
                ORDER BY SUM(duration) DESC
            ''', (self.user_id,))
            rows = cursor.fetchall()

            for app, total_duration in rows:
                usage_data[app] += total_duration

            conn.close()

        except Exception as e:
            print(f"❌ Failed to load app usage summary: {e}")
            self.label.setText("❌ Failed to load app usage summary.")
            return

        if not usage_data:
            self.label.setText("📋 No usage recorded.")
            return

        summary_lines = [
            f"{app} — {round(seconds / 60, 1)} min"
            for app, seconds in usage_data.items()
        ]

        self.label.setText("📋 App Usage Summary:\n" + "\n".join(summary_lines))
