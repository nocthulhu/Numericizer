from scipy.interpolate import CubicSpline
import numpy as np
from PyQt5.QtCore import QPointF
from point import Point

class Interpolation:
    """Class to handle interpolation of data points."""

    def __init__(self, calibration, main_window):
        self.calibration = calibration
        self.main_window = main_window
        self.interpolated_points = []
        self.method = 'linear'  # Default interpolation method

    def set_method(self, method):
        """Sets the interpolation method."""
        if method in ['linear', 'spline']:
            self.method = method
        else:
            raise ValueError("Invalid interpolation method. Choose 'linear' or 'spline'.")

    def interpolate_data(self, data_points):
        """Interpolates data points using the selected method."""
        if len(data_points) < 2:
            raise ValueError("At least two data points are required for interpolation.")

        valid_points = [point for point in data_points if point.get_real_coordinates() is not None]
        valid_points = sorted(valid_points, key=lambda point: point.get_real_coordinates().x())

        if len(valid_points) < 2:
            raise ValueError("Not enough valid real coordinates for interpolation.")

        x = [point.get_real_coordinates().x() for point in valid_points]
        y = [point.get_real_coordinates().y() for point in valid_points]

        if self.method == 'linear':
            y_new = np.interp(x, x, y)
        elif self.method == 'spline':
            cs = CubicSpline(x, y)
            x_new = np.linspace(min(x), max(x), num=100)
            y_new = cs(x_new)

        lower_bound, upper_bound = self.calculate_confidence_intervals(y_new)

        self.interpolated_points = []
        for x_val, y_val in zip(x, y_new):
            image_coords = self.calibration.inverse_transform_point(x_val, y_val)
            self.interpolated_points.append(Point(image_coords, QPointF(x_val, y_val), point_type='interpolated'))

        self.main_window.image_view.draw_interpolated_points(self.interpolated_points)
        self.main_window.draw_confidence_intervals(x, lower_bound, upper_bound)

        rmse = self.calculate_rmse(valid_points, self.interpolated_points)
        self.main_window.show_error_metric(rmse)

    def calculate_confidence_intervals(self, y_new):
        """Calculates confidence intervals for the interpolated points."""
        y_std = np.std(y_new) / np.sqrt(len(y_new))  # Simplified estimation, adjust as needed
        confidence_interval = 1.96 * y_std  # 95% confidence interval

        lower_bound = y_new - confidence_interval
        upper_bound = y_new + confidence_interval

        return lower_bound, upper_bound

    def calculate_rmse(self, original_points, interpolated_points):
        """Calculates the Root Mean Squared Error (RMSE) for the interpolated points."""
        errors = [(op.get_real_coordinates().y() - ip.get_real_coordinates().y()) ** 2 for op, ip in zip(original_points, interpolated_points)]
        mse = np.mean(errors)
        rmse = np.sqrt(mse)
        return rmse

    def clear_interpolated_points(self):
        """Clears the interpolated points."""
        self.interpolated_points = []
        self.main_window.image_view.clear_interpolated_points()
    def clear_interpolated_points(self):
        """Clears the interpolated points."""
        self.interpolated_points = []
        self.main_window.image_view.clear_interpolated_points()