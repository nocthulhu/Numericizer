from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class CalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Real Distance")
        self.real_distance = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel("Enter the real distance between the calibration points:")
        layout.addWidget(label)

        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def accept(self):
        try:
            self.real_distance = float(self.line_edit.text())
            super().accept()
        except ValueError:
            print("Invalid input. Please enter a number.")