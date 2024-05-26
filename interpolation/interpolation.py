import numpy as np
from scipy.interpolate import interp1d
from PyQt5.QtCore import QPointF
from point import Point


class Interpolation:
    """Class to handle interpolation of data points."""

    def __init__(self, calibration, main_window):
        self.calibration = calibration
        self.main_window = main_window
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        """Interpolates data points using the calibration matrix."""
        if len(data_points) < 2:
            raise ValueError("At least two data points are required for interpolation.")

        # Sort data points by their real x-coordinates to ensure proper interpolation
        valid_points = [point for point in data_points if point.get_real_coordinates() is not None]
        valid_points = sorted(valid_points, key=lambda point: point.get_real_coordinates().x())

        if len(valid_points) < 2:
            raise ValueError("Not enough valid real coordinates for interpolation.")

        x = [point.get_real_coordinates().x() for point in valid_points]
        y = [point.get_real_coordinates().y() for point in valid_points]

        x_min, x_max = min(x), max(x)
        num_points = max(len(data_points) * 40, 30)  # Ensure at least 30 points
        x_new = np.linspace(x_min, x_max, num_points)
        y_new = np.interp(x_new, x, y)

        self.interpolated_points = []
        for x_val, y_val in zip(x_new, y_new):
            image_coords = self.calibration.inverse_transform_point(x_val, y_val)
            self.interpolated_points.append(Point(image_coords, QPointF(x_val, y_val), point_type='interpolated'))

        self.main_window.image_view.draw_interpolated_points(self.interpolated_points)

    def clear_interpolated_points(self):
        """Clears the interpolated points."""
        self.interpolated_points = []
        self.main_window.image_view.clear_interpolated_points()
