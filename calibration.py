from PyQt5.QtCore import QPointF
from calibration_dialog import CalibrationDialog

class Calibration:
    """
    Handles axis calibration and scaling for accurate data extraction.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False

    def add_calibration_point(self, point):
        """Adds a calibration point to the list and prompts for real distance if two points are selected."""
        if len(self.calibration_points) < 2:
            self.calibration_points.append(point)
            self.main_window.image_view.draw_calibration_points(self.calibration_points)
            if len(self.calibration_points) == 2:
                self.get_real_distance()

    def get_real_distance(self):
        """Gets the real distance between the calibration points from the user."""
        dialog = CalibrationDialog(self.main_window)
        if dialog.exec() == CalibrationDialog.Accepted:
            self.real_distance = dialog.real_distance
            self.calibration_done = True

    def reset_calibration(self):
        """Resets calibration parameters and clears any drawn calibration points."""
        self.calibration_points = []
        self.real_distance = None
        self.calibration_done = False
        self.main_window.image_view.draw_calibration_points(self.calibration_points)