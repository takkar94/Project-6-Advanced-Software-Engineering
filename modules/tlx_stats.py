from PySide6 import QtWidgets
import sqlite3
from modules.database.db import get_db_path

class TLXStatsWidget(QtWidgets.QWidget):
    def __init__(self, user_id, user_role):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.setMinimumHeight(300)

        self.layout = QtWidgets.QHBoxLayout(self)

        # Two separate group boxes
        self.avg_group = QtWidgets.QGroupBox("Average Scores")
        self.latest_group = QtWidgets.QGroupBox("Latest Scores")

        self.avg_layout = QtWidgets.QVBoxLayout()
        self.latest_layout = QtWidgets.QVBoxLayout()

        self.avg_labels = {}
        self.latest_labels = {}

        for dimension in ["Mental", "Physical", "Temporal", "Performance", "Effort", "Frustration"]:
            avg_label = QtWidgets.QLabel(f"{dimension}: --")
            latest_label = QtWidgets.QLabel(f"{dimension}: --")

            self.avg_layout.addWidget(avg_label)
            self.latest_layout.addWidget(latest_label)

            self.avg_labels[dimension] = avg_label
            self.latest_labels[dimension] = latest_label

        self.avg_group.setLayout(self.avg_layout)
        self.latest_group.setLayout(self.latest_layout)

        self.layout.addWidget(self.avg_group)
        self.layout.addWidget(self.latest_group)

        self.refresh_stats()

    def refresh_stats(self):
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT mental, physical, temporal, performance, effort, frustration
            FROM tlx_entries
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (self.user_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            for dimension in self.avg_labels.keys():
                self.avg_labels[dimension].setText(f"{dimension}: No data")
                self.latest_labels[dimension].setText(f"{dimension}: No data")
            return

        mentals = [row[0] for row in rows]
        physicals = [row[1] for row in rows]
        temporals = [row[2] for row in rows]
        performances = [row[3] for row in rows]
        efforts = [row[4] for row in rows]
        frustrations = [row[5] for row in rows]

        metrics = {
            "Mental": mentals,
            "Physical": physicals,
            "Temporal": temporals,
            "Performance": performances,
            "Effort": efforts,
            "Frustration": frustrations
        }

        for dimension, values in metrics.items():
            avg = sum(values) / len(values)
            latest = values[-1]
            self.avg_labels[dimension].setText(f"{dimension}: {avg:.2f}")
            self.latest_labels[dimension].setText(f"{dimension}: {latest:.2f}")