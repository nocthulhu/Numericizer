import numpy as np
from point import Point
from PyQt5.QtCore import QPointF


class Interpolation:
    """Class for handling data interpolation."""

    def __init__(self, calibration):
        self.calibration = calibration
        self.interpolated_points = []

    def interpolate_data(self, data_points):
        """Interpolates data points linearly between each pair of points."""

        if len(data_points) < 2:
            raise ValueError("At least 2 data points are required for interpolation.")

        num_points = len(data_points) * 40  # Interpolation points count as 40 times data points count

        # Data points should be sorted by real x coordinates
        sorted_points = sorted(data_points, key=lambda p: p.get_real_coordinates().x())

        self.interpolated_points = []

        for i in range(len(sorted_points) - 1):
            p1 = sorted_points[i]
            p2 = sorted_points[i + 1]
            real_coords1 = np.array([p1.get_real_coordinates().x(), p1.get_real_coordinates().y()])
            real_coords2 = np.array([p2.get_real_coordinates().x(), p2.get_real_coordinates().y()])
            image_coords1 = np.array([p1.get_image_coordinates().x(), p1.get_image_coordinates().y()])
            image_coords2 = np.array([p2.get_image_coordinates().x(), p2.get_image_coordinates().y()])

            for t in np.linspace(0, 1, num_points // (len(sorted_points) - 1), endpoint=False):
                real_coords = (1 - t) * real_coords1 + t * real_coords2
                image_coords = (1 - t) * image_coords1 + t * image_coords2
                point = Point(QPointF(image_coords[0], image_coords[1]), QPointF(real_coords[0], real_coords[1]))
                self.interpolated_points.append(point)

        # Add the last point explicitly
        last_point = sorted_points[-1]
        self.interpolated_points.append(Point(last_point.get_image_coordinates(), last_point.get_real_coordinates()))

        return self.interpolated_points
