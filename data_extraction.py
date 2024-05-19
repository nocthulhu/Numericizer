import cv2
import numpy as np

class DataExtraction:
    """Data point selection and interpolation."""

    def __init__(self, main_window, calibration):
        self.main_window = main_window
        self.calibration = calibration
        self.data_points = []

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

    def extract_data(self):
        """Asks the user to select data points on the image."""
        image_copy = self.main_window.image_processor.image.copy()
        self.data_points = self.get_mouse_points(image_copy, "Data Extraction", -1)
        if self.calibration.calibration_done:
            self.scale_data_points()
        self.main_window.update_image_view()

    def scale_data_points(self):
        """Scales data points using calibration parameters."""
        if self.calibration.calibration_done and self.calibration.real_distance is not None:
            x1, y1 = self.calibration.calibration_points[0]
            x2, y2 = self.calibration.calibration_points[1]
            pixel_distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            scale_factor = self.calibration.real_distance / pixel_distance

            scaled_data = []
            for x, y in self.data_points:
                scaled_x = x * scale_factor
                scaled_y = y * scale_factor
                scaled_data.append((scaled_x, scaled_y))

            self.data_points = scaled_data
        else:
            print("Calibrate axes first.")

    def interpolate_data(self):
        """Performs linear interpolation between extracted data points."""
        if len(self.data_points) > 1:
            x, y = zip(*self.data_points)
            x_interp = np.linspace(x[0], x[-1], num=100)
            y_interp = np.interp(x_interp, x, y)
            self.data_points = list(zip(x_interp, y_interp))
        else:
            print("Not enough data points for interpolation. Extract at least two points.")