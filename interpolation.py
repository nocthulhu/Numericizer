from PyQt5.QtCore import QPointF
import numpy as np

class Interpolation:
    def __init__(self):
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        if len(data_points) > 1:
            self.interpolated_points.clear()
            sorted_points = sorted(data_points, key=lambda point: point.x())
            x, y = zip(*[(p.x(), p.y()) for p in sorted_points])
            x_interp = np.linspace(x[0], x[-1], num=100)
            y_interp = np.interp(x_interp, x, y)
            self.interpolated_points = [QPointF(x, y) for x, y in zip(x_interp, y_interp)]
        else:
            print("Not enough data points for interpolation. Extract at least two points.")