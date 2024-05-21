from PyQt5.QtCore import QPointF
import numpy as np

class Interpolation:
    """
    Handles linear interpolation between extracted data points
    using image coordinates.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.interpolated_points = []  # Stores QPointF of interpolated image points

    def interpolate_data(self, data_points):
        """Performs linear interpolation on image coordinates."""
        if len(data_points) > 1:
            sorted_points = sorted(data_points, key=lambda point: point.x())
            x, y = zip(*[(p.x(), p.y()) for p in sorted_points])
            x_interp = np.linspace(x[0], x[-1], num=100)
            y_interp = np.interp(x_interp, x, y)
            self.interpolated_points = [QPointF(x, y) for x, y in zip(x_interp, y_interp)]
            self.main_window.image_view.draw_data_points(self.interpolated_points)
        else:
            print("Not enough data points for interpolation. Extract at least two points.")