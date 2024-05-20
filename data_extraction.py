import cv2
import numpy as np
from PyQt5.QtCore import QPointF


class DataExtraction:
    """Data point selection and interpolation."""

    def __init__(self, main_window, calibration):
        self.main_window = main_window
        self.calibration = calibration
        self.data_points = []

    def add_data_point(self, point):
        """Adds a data point to the list."""
        self.data_points.append(QPointF(point.x(), point.y()))
        self.draw_data_points()
        if self.calibration.calibration_done:
            self.scale_data_points()

    def draw_data_points(self):
        """Draws data points on the image view."""
        if self.main_window.image_processor.image is not None:
            image_copy = self.main_window.image_processor.image.copy()
            for point in self.data_points:
                x, y = point.x(), point.y()
                cv2.circle(image_copy, (int(x), int(y)), 5, (255, 0, 0), -1)
            self.main_window.image_processor.image = image_copy
            self.main_window.update_image_view()

    def scale_data_points(self):
        """Scales data points using calibration parameters."""
        if self.calibration.calibration_done and self.calibration.real_distance is not None:
            x1, y1 = self.calibration.calibration_points[0].x(), self.calibration.calibration_points[0].y()
            x2, y2 = self.calibration.calibration_points[1].x(), self.calibration.calibration_points[1].y()
            pixel_distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            scale_factor = self.calibration.real_distance / pixel_distance

            scaled_data = []
            for point in self.data_points:
                x, y = point.x(), point.y()
                scaled_x = x * scale_factor
                scaled_y = y * scale_factor
                scaled_data.append(QPointF(scaled_x, scaled_y))

            self.data_points = scaled_data
        else:
            print("Calibrate axes first.")

    def interpolate_data(self):
        """Performs linear interpolation between extracted data points."""
        if len(self.data_points) > 1:
            x, y = zip(*[(p.x(), p.y()) for p in self.data_points])
            x_interp = np.linspace(x[0], x[-1], num=100)
            y_interp = np.interp(x_interp, x, y)
            self.data_points = [QPointF(x, y) for x, y in zip(x_interp, y_interp)]
            self.draw_data_points()
        else:
            print("Not enough data points for interpolation. Extract at least two points.")
