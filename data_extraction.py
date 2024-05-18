import cv2
import numpy as np

class DataExtraction:
    """Data point selection and interpolation."""

    def __init__(self, calibration):
        self.calibration = calibration
        self.data_points = []

    def extract_data(self, image):
        """Asks the user to select data points on the image."""
        self.data_points = []

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.data_points.append((x, y))
                cv2.circle(image, (x, y), 3, (255, 0, 0), -1)
                cv2.imshow("Data Extraction", image) # Change window name to "Data Extraction"

        cv2.namedWindow("Data Extraction") # Change window name to "Data Extraction"
        cv2.setMouseCallback("Data Extraction", mouse_callback) # Change window name to "Data Extraction"
        cv2.imshow("Data Extraction", image) # Change window name to "Data Extraction"
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if self.calibration.calibration_done:
            scaled_data = []
            for point in self.data_points:
                scaled_point = self.calibration.scale_data(point)
                if scaled_point is not None:
                    scaled_data.append(scaled_point)
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