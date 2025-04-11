from PySide6 import QtWidgets
import csv
import os

class TLXStatsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.setStyleSheet("font-size: 14px; padding: 10px;")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("📊 TLX Averages will appear here.")
        self.layout.addWidget(self.label)
        self.refresh_stats()

    def refresh_stats(self):
        if not os.path.exists("tlx_results.csv"):
            self.label.setText("📊 No TLX data found yet.")
            return

        with open("tlx_results.csv", newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)

        if not rows:
            self.label.setText("📊 No TLX entries recorded.")
            return

        # Calculate averages
        num_entries = len(rows)
        num_factors = len(headers)
        totals = [0] * num_factors

        for row in rows:
            for i in range(num_factors):
                totals[i] += int(row[i])

        averages = [round(tot / num_entries, 2) for tot in totals]

        display = "\n".join(f"{headers[i]}: {averages[i]}" for i in range(num_factors))
        self.label.setText(f"📈 Average NASA TLX Scores:\n{display}")
