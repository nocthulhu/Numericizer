from PyQt5.QtCore import QPointF
from point import Point

class Extraction:
    def __init__(self):
        self.data_points = []  # List of Point objects

    def add_data_point(self, point: QPointF):
        point_obj = Point(point, point_type='data')
        self.data_points.append(point_obj)
