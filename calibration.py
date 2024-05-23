from PyQt5.QtCore import QPointF
from calibration_dialog import CalibrationDialog
from point import Point
import numpy as np
import cv2

class Calibration:
    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []  # List of Point objects
        self.transformation_matrix = None
        self.calibration_done = False

    def add_calibration_point(self, point: QPointF):
        if len(self.calibration_points) < 3:
            point_obj = Point(point, point_type='calibration')
            self.calibration_points.append(point_obj)

            self.main_window.image_view.highlight_point(point_obj)

            dialog = CalibrationDialog(self.main_window)
            dialog.setWindowTitle(f"Enter Real Coordinates for Point {len(self.calibration_points)}")
            if dialog.exec() == CalibrationDialog.Accepted:
                point_obj.set_real_coordinates(dialog.real_coordinates)
                self.main_window.image_view.clear_highlight()
                if len(self.calibration_points) == 3:
                    self.calculate_transformation_matrix()
            else:
                self.calibration_points.pop()
                self.main_window.image_view.clear_highlight()

    def calculate_transformation_matrix(self):
        image_points = np.array([[p.get_image_coordinates().x(), p.get_image_coordinates().y()] for p in self.calibration_points])
        real_coords = np.array([p.get_real_coordinates() for p in self.calibration_points])
        self.transformation_matrix = cv2.getAffineTransform(
            image_points.astype(np.float32), real_coords.astype(np.float32)
        )
        self.calibration_done = True
        self.main_window.interpolationAction.setEnabled(True)

    def transform_points(self, points):
        if self.transformation_matrix is not None:
            image_points = np.array([[p.get_image_coordinates().x(), p.get_image_coordinates().y(), 1] for p in points])
            transformed_points = np.dot(self.transformation_matrix, image_points.T).T
            for i, point in enumerate(points):
                point.set_real_coordinates((transformed_points[i][0], transformed_points[i][1]))
            return points
        else:
            return None

    def reset_calibration(self):
        self.calibration_points.clear()
        self.transformation_matrix = None
        self.calibration_done = False

    def inverse_transform_point(self, x, y):
        if self.transformation_matrix is not None:
            inverse_matrix = cv2.invertAffineTransform(self.transformation_matrix)
            point = np.array([x, y, 1])
            transformed_point = np.dot(inverse_matrix, point)
            return transformed_point[0], transformed_point[1]
        else:
            return None

    def automatic_calibration(self, image):
        print("Starting automatic calibration...")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Harris Corner Detection
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray, 2, 3, 0.04)
        dst = cv2.dilate(dst, None)

        # Threshold to find the corners
        corners = np.argwhere(dst > 0.01 * dst.max())
        print("Detected corners:", corners)

        if len(corners) >= 3:
            corners = corners[:3]  # Take the first 3 corners
            self.calibration_points = []
            for corner in corners:
                y, x = corner  # Note the (y, x) order in the corners array
                point = QPointF(x, y)
                self.add_calibration_point(point)
            self.calculate_transformation_matrix()
            self.main_window.update_image()
            print("Calibration points set:", self.calibration_points)
        else:
            print("Not enough corners detected for calibration.")

        # Draw detected corners on the image for visual feedback
        for corner in corners:
            y, x = corner
            cv2.circle(image, (x, y), 5, (0, 255, 0), 2)

        # Update the image view to show the detected corners
        self.main_window.image_view.set_image(image)
        self.main_window.update_image()