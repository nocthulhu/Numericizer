import cv2
import numpy as np
from calibration_dialog import CalibrationDialog
from PyQt5.QtWidgets import QDialog

class Calibration:
    """Axis calibration and scaling."""

    def __init__(self):
        self.calibration_points = []
        self.calibration_done = False
        self.real_distance = None

    def calibrate_axes(self, image):
        """Asks the user to select two points for axis calibration."""
        self.calibration_points = []

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(self.calibration_points) < 2:
                    self.calibration_points.append((x, y))
                    cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
                    cv2.imshow("Calibration", image) # Change window name to "Calibration"
                    if len(self.calibration_points) == 2:
                        self.calibration_done = True
                        cv2.destroyAllWindows()

        cv2.namedWindow("Calibration") # Change window name to "Calibration"
        cv2.setMouseCallback("Calibration", mouse_callback) # Change window name to "Calibration"
        cv2.imshow("Calibration", image) # Change window name to "Calibration"
        cv2.waitKey(0)

        if self.calibration_done:
            dialog = CalibrationDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.real_distance = dialog.real_distance

    def scale_data(self, data_point):
        """Scales data points using calibration parameters."""
        if self.calibration_done and self.real_distance is not None:
            x1, y1 = self.calibration_points[0]
            x2, y2 = self.calibration_points[1]

            pixel_distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            scale_factor = self.real_distance / pixel_distance

            x, y = data_point
            scaled_x = x * scale_factor
            scaled_y = y * scale_factor
            return scaled_x, scaled_y
        else:
            print("Calibrate axes first.")
            return None