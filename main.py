from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QFileDialog, QSlider, QHBoxLayout, QVBoxLayout, \
    QTabWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from image_processor import ImageProcessor
from calibration import Calibration
from data_extraction import DataExtraction
from data_exporter import DataExporter
import cv2
import numpy as np


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration()  # Initialize calibration here
        self.calibration_done = False
        self.data_extraction = DataExtraction(self.calibration)
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
        self.image_label = QLabel(self.tab1)
        self.image_label.setGeometry(50, 50, 700, 500)

        self.load_button = QPushButton('Load Image', self.tab1)
        self.load_button.clicked.connect(self.open_image)
        self.load_button.move(50, 560)

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
        tab1_layout.addWidget(self.image_label)
        tab1_layout.addWidget(self.load_button)
        tab1_layout.addLayout(slider_layout)

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

        # Set the layout of the main window to the tab widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
    def open_image(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                "Image Files (*.jpg *.jpeg *.png);;All Files (*)", options=options)
        if filepath:
            self.image_processor.load_image(filepath)
            pixmap = QPixmap(filepath)
            self.image_label.setPixmap(pixmap)
            self.calibration_done = False
            self.original_image = self.image_processor.image.copy()
    def calibrate_axes(self):
        print("Calibrate Axes function called!")  # Add this line
        self.calibration_done = False
        if not self.calibration_done:
            if self.image_processor.image is not None:
                self.calibration.calibrate_axes(self.image_processor.image.copy())
                self.calibration_done = True  # Set to True after calibration
            else:
                print("Load an image first.")
    def extract_data(self):
        if self.image_processor.image is not None:
            self.data_extraction.extract_data(self.image_processor.image.copy())
        else:
            print("Load an image first.")

    def interpolate_data(self):
        self.data_extraction.interpolate_data()

    def export_data(self):
        if self.data_extraction.data_points:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "",
                                                    "CSV Files (*.csv);;All Files (*)", options=options)
            if filepath:
                self.data_exporter.export_to_csv(self.data_extraction.data_points, filepath)
        else:
            print("No data to export. Extract data points first.")

    def adjust_brightness(self, value):
        if self.original_image is not None:
            brightness = value

            # Work on a copy of the image
            img = self.original_image.copy()

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v = cv2.add(v, brightness)
            v = np.clip(v, 0, 255).astype(np.uint8)
            final_hsv = cv2.merge((h, s, v))
            processed_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

            self.image_processor.image = processed_image
            self.update_image_label()
        else:
            print("Load an image first.")

    def adjust_contrast(self, value):
        if self.original_image is not None:
            contrast = value / 255.0

            # Work on a copy of the image
            img = self.original_image.copy()

            processed_image = cv2.addWeighted(img, 1 + contrast,
                                              np.zeros(img.shape, img.dtype),
                                              0, -contrast * 128)

            self.image_processor.image = processed_image
            self.update_image_label()
        else:
            print("Load an image first.")
    def update_image_label(self):
        """Updates the image label with the processed image."""
        if self.image_processor.image is not None:
            height, width, channel = self.image_processor.image.shape
            bytes_per_line = 3 * width
            q_image = QPixmap(QtGui.QImage(self.image_processor.image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888).rgbSwapped())
            self.image_label.setPixmap(q_image)
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()