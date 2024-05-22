from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QFileDialog, QSlider, QHBoxLayout, \
    QVBoxLayout, QAction, QMenu, QMenuBar
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from image_view import ImageView
from image_processor import ImageProcessor
from calibration import Calibration
from data_extraction import Extraction
from interpolation import Interpolation
from data_exporter import DataExporter
import cv2
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.extraction = Extraction()
        self.interpolation = Interpolation(self.calibration)
        self.data_exporter = DataExporter()
        self.initUI()

        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False

        self.original_image = None

    def initUI(self):
        self.setWindowTitle('Engauge Digitizer')
        self.setGeometry(100, 100, 800, 600)

        self.image_view = ImageView(self)
        self.setCentralWidget(self.image_view)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        openAction = QAction('&Open Image', self)
        openAction.triggered.connect(self.open_image)
        fileMenu.addAction(openAction)

        toolsMenu = menubar.addMenu('&Tools')
        calibrationAction = QAction('&Calibrate Axes', self)
        calibrationAction.triggered.connect(self.toggle_calibration_mode)
        toolsMenu.addAction(calibrationAction)

        extractionAction = QAction('&Extract Data', self)
        extractionAction.triggered.connect(self.toggle_extraction_mode)
        toolsMenu.addAction(extractionAction)

        interpolationAction = QAction('&Interpolate Data', self)
        interpolationAction.triggered.connect(self.toggle_interpolation_mode)
        toolsMenu.addAction(interpolationAction)

        exportAction = QAction('&Export Data', self)
        exportAction.triggered.connect(self.export_data)
        toolsMenu.addAction(exportAction)

        toolbar = self.addToolBar('Tools')
        toolbar.addAction(calibrationAction)
        toolbar.addAction(extractionAction)
        toolbar.addAction(interpolationAction)
        toolbar.addAction(exportAction)

        self.brightness_label = QLabel("Brightness:", self)
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setRange(-255, 255)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_image)

        self.contrast_label = QLabel("Contrast:", self)
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setRange(-255, 255)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.update_image)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.brightness_label)
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.contrast_label)
        slider_layout.addWidget(self.contrast_slider)

        main_layout = QVBoxLayout()
        main_layout.addLayout(slider_layout)
        main_layout.addWidget(self.image_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

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
            self.update_image()

    def update_image(self):
        if self.original_image is not None:
            brightness = self.brightness_slider.value()
            contrast = self.contrast_slider.value()
            self.apply_brightness_contrast(brightness, contrast)

            # Update image view with processed image and points
            self.image_view.set_image(self.image_processor.image)
            self.image_view.draw_calibration_points(self.calibration.calibration_points)
            self.image_view.draw_data_points(self.extraction.data_points)
            if self.interpolation_mode:
                self.image_view.draw_data_points(
                    self.interpolation.interpolated_points
                )

    def apply_brightness_contrast(self, brightness, contrast):
        """Applies brightness and contrast adjustments to the image."""
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

    def toggle_calibration_mode(self):
        self.calibration_mode = not self.calibration_mode
        self.extraction_mode = False
        self.interpolation_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.calibration_mode else Qt.ArrowCursor))

    def toggle_extraction_mode(self):
        self.extraction_mode = not self.extraction_mode
        self.calibration_mode = False
        self.interpolation_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.extraction_mode else Qt.ArrowCursor))

    def toggle_interpolation_mode(self):
        self.interpolation_mode = not self.interpolation_mode
        self.calibration_mode = False
        self.extraction_mode = False

        if self.interpolation_mode:
            self.interpolation.calibration = self.calibration
            self.interpolation.interpolate_data(self.extraction.data_points)
            self.update_image()

    def export_data(self):
        if self.calibration.calibration_done:
            if self.interpolation_mode:
                real_coordinates = self.calibration.transform_points(
                    self.interpolation.interpolated_points
                )
            else:
                real_coordinates = self.calibration.transform_points(
                    self.extraction.data_points
                )
            if real_coordinates:
                options = QFileDialog.Options()
                filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "",
                                                          "CSV Files (*.csv);;All Files (*)", options=options)
                if filepath:
                    self.data_exporter.export_to_csv(real_coordinates, filepath)
        else:
            print("Calibration is required before exporting data points.")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()