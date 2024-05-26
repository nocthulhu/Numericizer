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

        x = [point.get_real_coordinates().x() for point in data_points if point.get_real_coordinates() is not None]
        y = [point.get_real_coordinates().y() for point in data_points if point.get_real_coordinates() is not None]

        if len(x) < 2 or len(y) < 2:
            raise ValueError("Not enough valid real coordinates for interpolation.")

        x_min, x_max = min(x), max(x)
        y_min, y_max = min(y), max(y)

        num_points = len(data_points) * 40
        x_new = np.linspace(x_min, x_max, num_points)
        y_new = np.interp(x_new, x, y)

        self.interpolated_points = [Point(self.calibration.inverse_transform_point(x, y), point_type='interpolated') for
                                    x, y in zip(x_new, y_new)]
        self.main_window.image_view.draw_interpolated_points(self.interpolated_points)
