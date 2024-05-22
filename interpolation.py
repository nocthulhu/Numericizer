from PyQt5.QtCore import QPointF
import numpy as np

class Interpolation:
    def __init__(self, calibration):
        self.calibration = calibration
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        if len(data_points) > 1:
            self.interpolated_points.clear()

            real_coordinates = self.calibration.transform_points(data_points)

            if real_coordinates is not None:
                sorted_points = sorted(real_coordinates, key=lambda point: point[0])
                x, y = zip(*sorted_points)
                x_interp = np.linspace(x[0], x[-1], num=100)
                y_interp = np.interp(x_interp, x, y)

                self.interpolated_points = [
                    QPointF(*self.calibration.inverse_transform_point(x, y))
                    for x, y in zip(x_interp, y_interp)
                ]
            else:
                print("Calibration is required before interpolation.")
        else:
            print("Not enough data points for interpolation. Extract at least two points.")