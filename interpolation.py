# interpolation.py

from PyQt5.QtCore import QPointF
import numpy as np
from point import Point

class Interpolation:
    def __init__(self, calibration):
        self.calibration = calibration
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        if len(data_points) > 1:
            self.interpolated_points.clear()

            # Ensure real-world coordinates are set for each point
            self.calibration.transform_points(data_points)
            real_coordinates = [p.get_real_coordinates() for p in data_points]

            if real_coordinates is not None:
                sorted_points = sorted(real_coordinates, key=lambda point: point[0])
                x, y = zip(*sorted_points)
                print("Sorted real coordinates:", sorted_points)
                x_interp = np.linspace(x[0], x[-1], num=100)
                y_interp = np.interp(x_interp, x, y)

                self.interpolated_points = [
                    Point(QPointF(*self.calibration.inverse_transform_point(x, y)), point_type='interpolated')
                    for x, y in zip(x_interp, y_interp)
                ]
                print("Interpolated points:", self.interpolated_points)
            else:
                print("Calibration is required before interpolation.")
        else:
            print("Not enough data points for interpolation. Extract at least two points.")