import cv2
import numpy as np

class ImageProcessor:
    """Image loading, processing, and visualization."""

    def __init__(self):
        self.image = None
        self.filepath = None

    def load_image(self, filepath):
        """Loads JPG or PNG image."""
        self.filepath = filepath
        if filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.image = cv2.imread(filepath)
        else:
            raise ValueError("Unsupported file format.")

    def display_image(self):
        """Displays the image on the screen."""
        if self.image is not None:
            cv2.imshow("Image", self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Load an image first.")