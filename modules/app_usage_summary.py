from PySide6 import QtWidgets
import csv
import os
from collections import defaultdict

class AppUsageSummary(QtWidgets.QWidget):
    def __init__(self, log_file="app_usage_log.csv"):
        super().__init__()
        self.log_file = log_file
        self.setMinimumHeight(200)
        self.setStyleSheet("font-size: 14px; padding: 10px;")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("📋 App usage summary will appear here.")
        self.layout.addWidget(self.label)

        self.refresh_summary()

    def refresh_summary(self):
        if not os.path.exists(self.log_file):
            self.label.setText("📋 No app usage data found.")
            return

        usage_data = defaultdict(int)

        with open(self.log_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                app = row["App"]
                try:
                    duration = int(row["Duration (s)"])
                    usage_data[app] += duration
                except:
                    continue

        if not usage_data:
            self.label.setText("📋 No usage recorded.")
            return

        summary_lines = [
            f"{app} — {round(seconds / 60, 1)} min"
            for app, seconds in sorted(usage_data.items(), key=lambda x: -x[1])
        ]

        self.label.setText("📋 App Usage Summary:\n" + "\n".join(summary_lines))
