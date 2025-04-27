from PySide6 import QtWidgets

class SystemUsabilityDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Usability Feedback")
        self.setMinimumSize(300, 200)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("On a scale of 1 to 10,\nhow easy was the system to use?")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self.value_label = QtWidgets.QLabel("5")
        self.slider.valueChanged.connect(lambda val: self.value_label.setText(str(val)))

        submit_button = QtWidgets.QPushButton("Submit")
        submit_button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        layout.addWidget(submit_button)

    def get_score(self):
        return self.slider.value()
