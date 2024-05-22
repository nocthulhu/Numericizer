from PyQt5.QtCore import QPointF
from calibration_dialog import CalibrationDialog
import numpy as np
import cv2
class Calibration:
    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []  # List of QPointF for image coordinates
        self.real_world_coordinates = []  # List of tuples for real coordinates
        self.transformation_matrix = None
        self.calibration_done = False

    def add_calibration_point(self, point: QPointF):
        if len(self.calibration_points) < 3:
            self.calibration_points.append(point)

            dialog = CalibrationDialog(self.main_window)
            if dialog.exec() == CalibrationDialog.Accepted:
                self.real_world_coordinates.append(dialog.real_coordinates)
                if len(self.calibration_points) == 3:
                    self.calculate_transformation_matrix()
            else:
                # If user cancels, remove the last added point
                self.calibration_points.pop()

    def calculate_transformation_matrix(self):
        image_points = np.array([[p.x(), p.y()] for p in self.calibration_points])
        real_coords = np.array(self.real_world_coordinates)
        self.transformation_matrix = cv2.getAffineTransform(
            image_points.astype(np.float32), real_coords.astype(np.float32)
        )
        self.calibration_done = True

    def transform_points(self, points):
        """Transforms a list of points from image to real coordinates."""
        if self.transformation_matrix is not None:
            homogeneous_points = np.array([[p.x(), p.y(), 1] for p in points])
            transformed_points = np.dot(self.transformation_matrix, homogeneous_points.T).T
            return [(p[0], p[1]) for p in transformed_points]
        else:
            return None

    def reset_calibration(self):
        self.calibration_points.clear()
        self.real_world_coordinates.clear()
        self.transformation_matrix = None


    def inverse_transform_point(self, x, y):
        if self.transformation_matrix is not None:
            inverse_matrix = cv2.invertAffineTransform(self.transformation_matrix)
            point = np.array([x, y, 1])
            transformed_point = np.dot(inverse_matrix, point)
            return transformed_point[0], transformed_point[1]  # x, y döndür
        else:
            return None