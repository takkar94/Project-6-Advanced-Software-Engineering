from PySide6 import QtWidgets, QtCore


class TLXForm(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NASA TLX - Workload Assessment")
        self.setModal(True)
        self.setMinimumSize(400, 300)

        self.fields = {}
        layout = QtWidgets.QFormLayout(self)

        categories = [
            "Mental Demand",
            "Physical Demand",
            "Temporal Demand",
            "Performance",
            "Effort",
            "Frustration"
        ]

        for category in categories:
            # Create slider
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(50)
            slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            slider.setTickInterval(10)

            # Label to show current value
            value_label = QtWidgets.QLabel("50")
            slider.valueChanged.connect(lambda val, lbl=value_label: lbl.setText(str(val)))

            # Pack into a row
            row_layout = QtWidgets.QHBoxLayout()
            row_layout.addWidget(slider)
            row_layout.addWidget(value_label)

            container = QtWidgets.QWidget()
            container.setLayout(row_layout)

            layout.addRow(f"{category}:", container)
            self.fields[category] = slider

        # Submit Button
        self.submit_btn = QtWidgets.QPushButton("Submit")
        self.submit_btn.clicked.connect(self.accept)
        layout.addWidget(self.submit_btn)

    # def get_results(self):
    #     return {key: slider.value() for key, slider in self.fields.items()}

    def get_results(self):
        raw_results = {key: slider.value() for key, slider in self.fields.items()}
        mapped_results = {
            "Mental": raw_results.get("Mental Demand", 0),
            "Physical": raw_results.get("Physical Demand", 0),
            "Temporal": raw_results.get("Temporal Demand", 0),
            "Performance": raw_results.get("Performance", 0),
            "Effort": raw_results.get("Effort", 0),
            "Frustration": raw_results.get("Frustration", 0)
        }
        return mapped_results