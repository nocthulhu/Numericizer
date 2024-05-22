from PyQt5.QtCore import QPointF


class Point:
    def __init__(self, qpoint: QPointF, real_coordinates=None, point_type='data'):
        self.qpoint = qpoint
        self.real_coordinates = real_coordinates
        self.point_type = point_type

    def set_real_coordinates(self, real_coordinates):
        self.real_coordinates = real_coordinates

    def get_image_coordinates(self):
        return self.qpoint.x(), self.qpoint.y()

    def get_real_coordinates(self):
        return self.real_coordinates

    def is_calibration_point(self):
        return self.point_type == 'calibration'

    def is_data_point(self):
        return self.point_type == 'data'
