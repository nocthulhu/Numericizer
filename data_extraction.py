from PyQt5.QtCore import QPointF


class Extraction:
    """
    Handles data point extraction from the image.
    Calculates and stores real coordinates of extracted points using the calibration.
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.data_points = []  # Stores QPointF points clicked by the user
        self.real_coordinates = []  # Stores tuples of (x, y) real coordinates

    def add_data_point(self, point: QPointF):
        """
        Adds a data point to the list, transforming the point
        to real coordinates using the calibration.
        """
        self.data_points.append(point)
        self.main_window.image_view.draw_data_points(self.data_points)

        if self.main_window.calibration.calibration_done:
            real_coords = self.main_window.calibration.transform_point(point)
            if real_coords is not None:
                self.real_coordinates.append(real_coords)
                print(f"Extracted point (Real Coordinates): {real_coords}")
        else:
            print("Calibration is required before extracting data points.")