from PySide6 import QtWidgets
import csv
import os

class TLXStatsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.setStyleSheet("font-size: 14px; padding: 10px;")
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("📊 TLX stats will show here.")
        self.layout.addWidget(self.label)

        self.refresh_stats()

    def refresh_stats(self):
        if not os.path.exists("tlx_results.csv"):
            self.label.setText("📊 No TLX data yet.")
            return

        with open("tlx_results.csv", newline='') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                self.label.setText("📊 TLX file is empty.")
                return

            rows = list(reader)

        if not rows:
            self.label.setText("📊 No TLX entries.")
            return

        try:
            totals = [0] * len(headers)
            counts = [0] * len(headers)

            for row in rows:
                for i, val in enumerate(row):
                    try:
                        value = int(val)
                        totals[i] += value
                        counts[i] += 1
                    except (ValueError, TypeError):
                        continue  # Skip empty or invalid values

            averages = [
                round(totals[i] / counts[i], 2) if counts[i] > 0 else 0
                for i in range(len(headers))
            ]

            display = "\n".join(f"{headers[i]}: {averages[i]}" for i in range(len(headers)))
            self.label.setText(f"📈 TLX Averages:\n{display}")
        except Exception as e:
            self.label.setText(f"❌ Error reading TLX: {e}")
