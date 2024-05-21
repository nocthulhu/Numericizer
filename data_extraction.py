from PyQt5.QtCore import QPointF

class Extraction:
    """
    Handles data point extraction from the image.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.data_points = []

    def add_data_point(self, point):
        """Adds a data point to the list and draws it on the image view."""
        self.data_points.append(point)
        self.main_window.image_view.draw_data_points(self.data_points)