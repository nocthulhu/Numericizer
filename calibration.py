from PyQt5.QtCore import QPointF
from calibration_dialog import CalibrationDialog
import numpy as np
import cv2
class Calibration:
    """
    Handles axis calibration and scaling for accurate data extraction.
    Uses three points to define the coordinate plane.
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []  # Stores QPointF points clicked by the user
        self.real_coordinates = []  # Stores tuples of (x, y) real coordinates entered by the user
        self.transformation_matrix = None  # 2x3 matrix for transforming image points to real coordinates
        self.calibration_done = False

    def add_calibration_point(self, point: QPointF):
        """
        Adds a calibration point to the list and prompts for real coordinates.
        Calculates the transformation matrix when three points are defined.
        """
        if len(self.calibration_points) < 3:
            self.calibration_points.append(point)
            self.main_window.image_view.draw_calibration_points(self.calibration_points)

            # Prompt for real coordinates
            dialog = CalibrationDialog(self.main_window)
            if dialog.exec() == CalibrationDialog.Accepted:
                self.real_coordinates.append(dialog.real_coordinates)
            else:
                # If user cancels, remove the last added point
                self.calibration_points.pop()
                self.main_window.image_view.draw_calibration_points(self.calibration_points)
                return

            if len(self.calibration_points) == 3:
                self.calculate_transformation_matrix()
                self.calibration_done = True

    def calculate_transformation_matrix(self):
        """
        Calculates the transformation matrix based on the three calibration points
        and their corresponding real coordinates.
        """
        # Convert to numpy arrays for easier calculations
        image_points = np.array([[p.x(), p.y()] for p in self.calibration_points])
        real_coords = np.array(self.real_coordinates)

        # Calculate the transformation matrix using OpenCV's getAffineTransform
        self.transformation_matrix = cv2.getAffineTransform(
            image_points.astype(np.float32), real_coords.astype(np.float32)
        )

    def transform_point(self, point: QPointF) -> tuple:
        """
        Transforms a point from image coordinates to real coordinates using
        the calculated transformation matrix.
        """
        if self.transformation_matrix is not None:
            # Create a homogeneous coordinate (x, y, 1)
            homogeneous_point = np.array([point.x(), point.y(), 1])
            # Apply the transformation matrix
            transformed_point = np.dot(self.transformation_matrix, homogeneous_point)
            return tuple(transformed_point[:2]) # Return (x, y)
        else:
            return None

    def reset_calibration(self):
        """Resets calibration parameters and clears any drawn calibration points."""
        self.calibration_points = []
        self.real_coordinates = []
        self.transformation_matrix = None
        self.calibration_done = False
        self.main_window.image_view.draw_calibration_points(self.calibration_points)