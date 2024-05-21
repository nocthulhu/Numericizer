from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

class CalibrationDialog(QDialog):
    """
    Dialog to get real coordinates for a calibration point.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Real Coordinates")
        self.real_coordinates = (None, None)  # Initialize as (None, None)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel("Enter the real X and Y coordinates for this point:")
        layout.addWidget(label)

        # Use QHBoxLayout for inputting X and Y coordinates side-by-side
        input_layout = QHBoxLayout()

        self.x_line_edit = QLineEdit(self)
        self.x_line_edit.setPlaceholderText("X")
        input_layout.addWidget(self.x_line_edit)

        self.y_line_edit = QLineEdit(self)
        self.y_line_edit.setPlaceholderText("Y")
        input_layout.addWidget(self.y_line_edit)

        layout.addLayout(input_layout)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def accept(self):
        try:
            x = float(self.x_line_edit.text())
            y = float(self.y_line_edit.text())
            self.real_coordinates = (x, y)
            super().accept()
        except ValueError:
            print("Invalid input. Please enter numbers for X and Y.")