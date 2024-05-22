from PyQt5.QtCore import QPointF

class Extraction:
    def __init__(self):
        self.data_points = []  # Stores QPointF points clicked by the user

    def add_data_point(self, point: QPointF):
        self.data_points.append(point)
