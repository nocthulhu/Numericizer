import cv2
import numpy as np
from calibration_dialog import CalibrationDialog
from PyQt5.QtWidgets import QDialog

class Calibration:
    """Axis calibration and scaling."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False

    def get_mouse_points(self, image, window_name, point_count=2):
        points = []

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(points) < point_count or point_count == -1:
                    points.append((x, y))
                    cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
                    cv2.imshow(window_name, image)
                    if len(points) == point_count:
                        cv2.destroyAllWindows()

        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        return points

    def calibrate_axes(self):
        """Asks the user to select two points for axis calibration."""
        if self.main_window.image_processor.image is not None:
            self.calibration_points = self.get_mouse_points(self.main_window.image_processor.image.copy(),
                                                            "Calibration", 2)
            if len(self.calibration_points) == 2:
                dialog = CalibrationDialog()
                if dialog.exec_() == QDialog.Accepted:
                    self.real_distance = dialog.real_distance
                    self.calibration_done = True
                    self.main_window.update_image_view()
        else:
            print("Load an image first.")

    def reset_calibration(self):
        """Resets calibration parameters."""
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False