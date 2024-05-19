from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QFileDialog, QSlider, QHBoxLayout, QVBoxLayout, \
    QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QPointF
from PyQt5 import QtGui
from image_processor import ImageProcessor
from calibration import Calibration
from data_extraction import DataExtraction
from data_exporter import DataExporter
import cv2
import numpy as np


class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.pixmap_item = None
        self.zoom_factor = 1

    def set_image(self, image):
        """Sets the image for the view."""
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.pixmap = QPixmap.fromImage(q_image)
        if self.pixmap_item is None:
            self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.pixmap_item)
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        else:
            self.pixmap_item.setPixmap(self.pixmap)

    def wheelEvent(self, event):
        """Zoom with mouse wheel."""
        if self.pixmap_item:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            self.zoom_factor *= 1.1 ** steps
            self.scale(1.1 ** steps, 1.1 ** steps)

    def mousePressEvent(self, event):
        """Start panning."""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.start_pos = event.pos()
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """End panning."""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            super().mouseReleaseEvent(event)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.data_extraction = DataExtraction(self, self.calibration)
        self.data_exporter = DataExporter()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Engauge Digitizer')
        self.setGeometry(100, 100, 800, 600)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(800, 600)

        # Add tabs
        self.tabs.addTab(self.tab1, "Load & Edit")
        self.tabs.addTab(self.tab2, "Calibration")
        self.tabs.addTab(self.tab3, "Data Extraction")

        # Tab 1: Load & Edit
        self.image_view = ImageView(self.tab1)
        self.image_view.setGeometry(50, 50, 700, 500)

        self.load_button = QPushButton('Load Image', self.tab1)
        self.load_button.clicked.connect(self.open_image)
        self.load_button.move(50, 560)

        # Tab 2: Calibration
        self.calibrate_button = QPushButton('Calibrate Axes', self.tab2)
        self.calibrate_button.clicked.connect(self.calibrate_axes)
        self.calibrate_button.move(50, 50)

        # Tab 3: Data Extraction
        self.extract_button = QPushButton('Extract Data', self.tab3)
        self.extract_button.clicked.connect(self.extract_data)
        self.extract_button.move(50, 50)

        self.interpolate_button = QPushButton('Interpolate Data', self.tab3)
        self.interpolate_button.clicked.connect(self.interpolate_data)
        self.interpolate_button.move(50, 100)

        self.export_button = QPushButton('Export Data', self.tab3)
        self.export_button.clicked.connect(self.export_data)
        self.export_button.move(50, 150)

        # Brightness and Contrast Sliders
        self.brightness_label = QLabel("Brightness:", self.tab1)
        self.brightness_slider = QSlider(Qt.Horizontal, self.tab1)
        self.brightness_slider.setRange(-255, 255)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)

        self.contrast_label = QLabel("Contrast:", self.tab1)
        self.contrast_slider = QSlider(Qt.Horizontal, self.tab1)
        self.contrast_slider.setRange(-255, 255)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)

        # Layout for sliders
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.brightness_label)
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.contrast_label)
        slider_layout.addWidget(self.contrast_slider)

        # Adjust margins and spacing for slider_layout
        slider_layout.setContentsMargins(10, 10, 10, 10)
        slider_layout.setSpacing(10)

        # Main layout for Tab 1
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.image_view)
        tab1_layout.addWidget(self.load_button)
        tab1_layout.addLayout(slider_layout)

        # Set the layout of the main window to the tab widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

    def open_image(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                  "Image Files (*.jpg *.jpeg *.png);;All Files (*)", options=options)
        if filepath:
            self.image_processor.load_image(filepath)
            self.calibration.reset_calibration()
            self.original_image = self.image_processor.image.copy()
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(0)
            self.update_image_view()

    def adjust_brightness(self, value):
        if self.original_image is not None:
            self.apply_brightness_contrast(value, self.contrast_slider.value())
        else:
            print("Load an image first.")

    def adjust_contrast(self, value):
        if self.original_image is not None:
            self.apply_brightness_contrast(self.brightness_slider.value(), value)
        else:
            print("Load an image first.")

    def apply_brightness_contrast(self, brightness, contrast):
        """Applies both brightness and contrast adjustments to the image."""
        img = self.original_image.copy()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, brightness)
        v = np.clip(v, 0, 255).astype(np.uint8)
        final_hsv = cv2.merge((h, s, v))
        processed_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

        contrast = contrast / 255.0
        processed_image = cv2.addWeighted(processed_image, 1 + contrast,
                                          np.zeros(img.shape, img.dtype),
                                          0, -contrast * 128)
        self.image_processor.image = processed_image
        self.update_image_view()

    def update_image_view(self):
        """Updates the image view with the processed image."""
        if self.image_processor.image is not None:
            self.image_view.set_image(self.image_processor.image)

    def calibrate_axes(self):
        if self.image_processor.image is not None:
            self.calibration.calibrate_axes()
        else:
            print("Load an image first.")

    def extract_data(self):
        if self.image_processor.image is not None:
            self.data_extraction.extract_data()
        else:
            print("Load an image first.")
    def export_data(self):
        if self.data_extraction.data_points:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "",
                                                    "CSV Files (*.csv);;All Files (*)", options=options)
            if filepath:
                self.data_exporter.export_to_csv(self.data_extraction.data_points, filepath)
        else:
            print("No data to export. Extract data points first.")
    def interpolate_data(self):
        self.data_extraction.interpolate_data()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()