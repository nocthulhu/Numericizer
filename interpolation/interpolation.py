import numpy as np
from scipy.interpolate import interp1d
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
        data_points = sorted(data_points, key=lambda point: point.get_real_coordinates().x())
        x = [point.get_real_coordinates().x() for point in data_points if point.get_real_coordinates() is not None]
        y = [point.get_real_coordinates().y() for point in data_points if point.get_real_coordinates() is not None]

        if len(x) < 2 or len(y) < 2:
            raise ValueError("Not enough valid real coordinates for interpolation.")

        self.interpolated_points = []

        # Interpolate between each pair of points
        for i in range(len(data_points) - 1):
            x1, y1 = x[i], y[i]
            x2, y2 = x[i + 1], y[i + 1]

            # Calculate the number of interpolated points between each pair
            num_points_between = max(30, int(np.hypot(x2 - x1, y2 - y1)))  # At least 10 points between each pair

            x_new = np.linspace(x1, x2, num_points_between)
            y_new = np.interp(x_new, [x1, x2], [y1, y2])

            # Append interpolated points
            for xi, yi in zip(x_new, y_new):
                interpolated_point = Point(self.calibration.inverse_transform_point(xi, yi), point_type='interpolated')
                self.interpolated_points.append(interpolated_point)

        self.main_window.image_view.draw_interpolated_points(self.interpolated_points)

    def clear_interpolated_points(self):
        """Clears the interpolated points."""
        self.interpolated_points = []
        self.main_window.image_view.clear_interpolated_points()
