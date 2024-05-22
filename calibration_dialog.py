from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class CalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.real_coordinates = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Enter Real Coordinates")

        layout = QVBoxLayout()

        self.x_label = QLabel("X Coordinate:")
        self.x_input = QLineEdit()
        self.y_label = QLabel("Y Coordinate:")
        self.y_input = QLineEdit()

        layout.addWidget(self.x_label)
        layout.addWidget(self.x_input)
        layout.addWidget(self.y_label)
        layout.addWidget(self.y_input)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def accept(self):
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            self.real_coordinates = (x, y)
            super().accept()
        except ValueError:
            self.x_input.setText("")
            self.y_input.setText("")
            self.x_input.setPlaceholderText("Please enter valid numbers")
            self.y_input.setPlaceholderText("Please enter valid numbers")