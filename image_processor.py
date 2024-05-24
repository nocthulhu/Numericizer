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

    def equalize_histogram(self):
        if self.image is not None:
            if len(self.image.shape) == 3:  # Mixed Color
                img_yuv = cv2.cvtColor(self.image, cv2.COLOR_BGR2YUV)
                img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
                self.image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
            elif len(self.image.shape) == 2:  # Grayscale
                self.image = cv2.equalizeHist(self.image)
            else:
                print("Unsupported image format for histogram equalization.")
        else:
            print("Load an image first.")

    def edge_detection(self):
        if self.image is not None:
            self.image = cv2.Canny(self.image, 100, 200)
        else:
            print("Load an image first.")

    def denoise_image(self):
        if self.image is not None:
            if len(self.image.shape) == 3:
                self.image = cv2.fastNlMeansDenoisingColored(self.image, None, 10, 10, 7, 21)
            elif len(self.image.shape) == 2:
                self.image = cv2.fastNlMeansDenoising(self.image, None, 10, 7, 21)
            else:
                print("Unsupported image format for denoising.")
        else:
            print("Load an image first.")

    def correct_perspective(self, pts1, pts2):
        if self.image is not None:
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            width, height = self.image.shape[1], self.image.shape[0]
            self.image = cv2.warpPerspective(self.image, matrix, (width, height))

    def rotate_image(self, angle):
        if self.image is not None:
            (h, w) = self.image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            self.image = cv2.warpAffine(self.image, matrix, (w, h))
