import cv2
import numpy as np
from PyQt5.QtCore import QPointF
from point import Point

class Extraction:
    """Class to manage the extraction of data points from an image."""

    def __init__(self):
        self.data_points = []  # List of Point objects

    def add_data_point(self, point: QPointF):
        """Adds a data point."""
        point_obj = Point(point, point_type='data')
        self.data_points.append(point_obj)

    def delete_data_point(self, index):
        """Deletes a data point at the given index."""
        if 0 <= index < len(self.data_points):
            del self.data_points[index]

    def edit_data_point(self, index, new_point: QPointF):
        """Edits the data point at the given index with a new point."""
        if 0 <= index < len(self.data_points):
            self.data_points[index].set_image_coordinates(new_point)

    def get_data_points(self):
        """Returns the list of data points."""
        return self.data_points

    def automatic_extraction(self, image):
        """Automatically extracts data points from the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Enhanced contrast and adaptive thresholding
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect circles using Hough Transform
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                   param1=50, param2=30, minRadius=1, maxRadius=30)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                point = QPointF(x, y)
                self.add_data_point(point)
                cv2.circle(image, (x, y), r, (0, 255, 0), 4)

        return image