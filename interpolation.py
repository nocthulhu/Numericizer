from PyQt5.QtCore import QPointF
import numpy as np
from point import Point

class Interpolation:
    """Class to handle interpolation of data points based on calibration."""

    def __init__(self, calibration):
        self.calibration = calibration
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        """Interpolates data points if there are more than one point."""
        if len(data_points) > 1:
            self.interpolated_points.clear()

            # Transform data points using calibration matrix
            transformed_points = self.calibration.transform_points(data_points)
            real_coordinates = [p.get_real_coordinates() for p in transformed_points]

            if real_coordinates:
                sorted_points = sorted(real_coordinates, key=lambda point: point[0])
                x, y = zip(*sorted_points)
                print("Sorted real coordinates:", sorted_points)
                x_interp = np.linspace(x[0], x[-1], num=100)
                y_interp = np.interp(x_interp, x, y)

                self.interpolated_points = [
                    Point(QPointF(*self.calibration.inverse_transform_point(x_val, y_val)),
                          real_coordinates=(x_val, y_val), point_type='interpolated')
                    for x_val, y_val in zip(x_interp, y_interp)
                ]
                print("Interpolated points:", self.interpolated_points)
            else:
                print("Calibration is required before interpolation.")
        else:
            print("Not enough data points for interpolation. Extract at least two points.")

    def get_interpolated_points(self):
        """Returns the list of interpolated points."""
        return self.interpolated_points
