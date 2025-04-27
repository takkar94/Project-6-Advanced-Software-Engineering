from PySide6 import QtWidgets
import sqlite3
import os
from modules.database.db import get_db_path
import matplotlib.pyplot as plt

class TLXStatsWidget(QtWidgets.QWidget):
    def __init__(self, user_id, user_role, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.user_role = user_role

        self.setMinimumHeight(150)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.latest_label = QtWidgets.QLabel("Latest TLX Entry: N/A")
        self.average_label = QtWidgets.QLabel("Average TLX: N/A")

        self.layout.addWidget(self.latest_label)
        self.layout.addWidget(self.average_label)

        # Only managers get the "View All Employees" button
        if self.user_role == "manager":
            self.view_all_button = QtWidgets.QPushButton("📊 View All Employees' TLX Data")
            self.view_all_button.clicked.connect(self.show_all_employees_chart)
            self.layout.addWidget(self.view_all_button)

        self.refresh_stats()

    def refresh_stats(self):
        try:
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Fetch latest TLX entry for this user
            cursor.execute('''
                SELECT mental, physical, temporal, performance, effort, frustration
                FROM tlx_entries
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (self.user_id,))
            latest = cursor.fetchone()

            if latest:
                latest_text = f"Mental: {latest[0]}, Physical: {latest[1]}, Temporal: {latest[2]}, " \
                              f"Performance: {latest[3]}, Effort: {latest[4]}, Frustration: {latest[5]}"
            else:
                latest_text = "No entries yet."

            self.latest_label.setText(f"Latest TLX Entry:\n{latest_text}")

            # Fetch averages for this user
            cursor.execute('''
                SELECT 
                    AVG(mental), AVG(physical), AVG(temporal),
                    AVG(performance), AVG(effort), AVG(frustration)
                FROM tlx_entries
                WHERE user_id = ?
            ''', (self.user_id,))
            averages = cursor.fetchone()

            if averages and all(a is not None for a in averages):
                avg_text = f"Mental: {averages[0]:.1f}, Physical: {averages[1]:.1f}, Temporal: {averages[2]:.1f}, " \
                           f"Performance: {averages[3]:.1f}, Effort: {averages[4]:.1f}, Frustration: {averages[5]:.1f}"
            else:
                avg_text = "No data yet."

            self.average_label.setText(f"Average TLX:\n{avg_text}")

            conn.close()
        except Exception as e:
            print(f"❌ Failed to fetch TLX stats: {e}")
            self.latest_label.setText("Latest TLX Entry: Error")
            self.average_label.setText("Average TLX: Error")

    def show_all_employees_chart(self):
        try:
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Fetch average frustration per employee
            cursor.execute('''
                SELECT users.name, 
                       AVG(tlx_entries.mental),
                       AVG(tlx_entries.physical),
                       AVG(tlx_entries.temporal),
                       AVG(tlx_entries.performance),
                       AVG(tlx_entries.effort),
                       AVG(tlx_entries.frustration)
                FROM tlx_entries
                JOIN users ON tlx_entries.user_id = users.id
                GROUP BY users.id
            ''')
            data = cursor.fetchall()
            conn.close()

            if not data:
                QtWidgets.QMessageBox.information(self, "No Data", "No TLX data available yet.")
                return

            names = [row[0] for row in data]
            frustrations = [row[6] for row in data]

            # Plot the graph
            plt.figure(figsize=(10, 6))
            plt.bar(names, frustrations, color="skyblue")
            plt.xlabel("Employees")
            plt.ylabel("Average Frustration Level")
            plt.title("Average Frustration Level of Employees")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"❌ Failed to plot all employees' TLX: {e}")
