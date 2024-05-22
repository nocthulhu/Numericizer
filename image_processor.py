import cv2

class ImageProcessor:
    def __init__(self):
        self.image = None
        self.filepath = None

    def load_image(self, filepath):
        self.filepath = filepath
        if filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.image = cv2.imread(filepath)
        else:
            raise ValueError("Unsupported file format.")

    def display_image(self):
        if self.image is not None:
            cv2.imshow("Image", self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Load an image first.")