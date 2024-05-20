import cv2
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QPointF


class Calibration:
    """Axis calibration and scaling."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False

    def add_calibration_point(self, point):
        """Adds a calibration point to the list."""
        if len(self.calibration_points) < 2:
            self.calibration_points.append(QPointF(point.x(), point.y()))
            self.draw_calibration_points()
            if len(self.calibration_points) == 2:
                self.get_real_distance()

    def draw_calibration_points(self):
        """Draws calibration points on the image view."""
        if self.main_window.image_processor.image is not None:
            image_copy = self.main_window.image_processor.image.copy()
            for point in self.calibration_points:
                x, y = point.x(), point.y()
                cv2.circle(image_copy, (int(x), int(y)), 5, (0, 0, 255), -1)
            self.main_window.image_processor.image = image_copy
            self.main_window.update_image_view()

    def get_real_distance(self):
        """Gets the real distance between the calibration points from the user."""
        distance, ok = QInputDialog.getDouble(self.main_window, "Enter Real Distance", "Real distance:", 1.0)
        if ok:
            self.real_distance = distance
            self.calibration_done = True

    def reset_calibration(self):
        """Resets calibration parameters."""
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False
