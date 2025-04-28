from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sqlite3
from modules.database.db import get_db_path, fetch_manager_interruptions
import datetime

class TLXStatsWidget(QtWidgets.QWidget):
    def __init__(self, user_id, user_role):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.setMinimumHeight(300)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.canvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.layout.addWidget(self.canvas)

        self.refresh_stats()

    def refresh_stats(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT frustration, timestamp FROM tlx_entries
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (self.user_id,))
        rows = cursor.fetchall()

        conn.close()

        if not rows:
            ax.set_title("No TLX data yet.")
            self.canvas.draw()
            return

        frustrations = [row[0] for row in rows]
        timestamps = [datetime.datetime.fromisoformat(row[1]) for row in rows]

        ax.plot(timestamps, frustrations, label="Frustration Level", marker='o')

        # --- Fetch and plot Manager Interruptions ---
        interruption_times = fetch_manager_interruptions(self.user_id)
        if interruption_times:
            interruptions = [datetime.datetime.fromisoformat(ts) for ts in interruption_times]
            ax.scatter(interruptions, [100]*len(interruptions), color='green', marker='X', label='Manager Interruptions')

        ax.set_ylabel("Frustration (0–100)")
        ax.set_xlabel("Time")
        ax.set_title("Frustration Levels Over Time")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()
