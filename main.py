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
    """
    Handles user interface, image processing, calibration, data extraction, interpolation, data expor etc.
    """
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.extraction = Extraction(self)
        self.interpolation = Interpolation(self)
        self.data_exporter = DataExporter()
        self.initUI()

        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False

        self.original_image = None

    def initUI(self):
        """Initializes the user interface, including menus, toolbar, and sliders."""
        self.setWindowTitle('Engauge Digitizer')
        self.setGeometry(100, 100, 800, 600)

        # Image View
        self.image_view = ImageView(self)
        self.setCentralWidget(self.image_view)

        # Menu Bar
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

        # Toolbar
        toolbar = self.addToolBar('Tools')
        toolbar.addAction(calibrationAction)
        toolbar.addAction(extractionAction)
        toolbar.addAction(interpolationAction)
        toolbar.addAction(exportAction)

        # Brightness and Contrast Sliders
        self.brightness_label = QLabel("Brightness:", self)
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setRange(-255, 255)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)

        self.contrast_label = QLabel("Contrast:", self)
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setRange(-255, 255)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)

        # Layout for sliders
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.brightness_label)
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.contrast_label)
        slider_layout.addWidget(self.contrast_slider)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(slider_layout)
        main_layout.addWidget(self.image_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_image(self):
        """Opens an image file using a file dialog."""
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
        """Adjusts the brightness of the image."""
        if self.original_image is not None:
            self.apply_brightness_contrast(value, self.contrast_slider.value())

    def adjust_contrast(self, value):
        """Adjusts the contrast of the image."""
        if self.original_image is not None:
            self.apply_brightness_contrast(self.brightness_slider.value(), value)

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
        self.update_image_view()

    def update_image_view(self):
        """Updates the image view with the processed image and any drawn points."""
        if self.image_processor.image is not None:
            self.image_view.set_image(self.image_processor.image)

            if self.calibration_mode:
                self.image_view.draw_calibration_points(self.calibration.calibration_points)
            elif self.extraction_mode:
                self.image_view.draw_data_points(self.extraction.data_points)
            elif self.interpolation_mode:
                self.image_view.draw_data_points(self.interpolation.interpolated_points)

    def toggle_calibration_mode(self):
        """Toggles calibration mode on or off."""
        self.calibration_mode = not self.calibration_mode
        self.extraction_mode = False
        self.interpolation_mode = False
        if self.calibration_mode:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_extraction_mode(self):
        """Toggles data extraction mode on or off."""
        self.extraction_mode = not self.extraction_mode
        self.calibration_mode = False
        self.interpolation_mode = False
        if self.extraction_mode:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_interpolation_mode(self):
        """
        Toggles interpolation mode.
        Calculates real-world coordinates for interpolated points if calibration is done.
        """
        self.interpolation_mode = not self.interpolation_mode
        self.calibration_mode = False
        self.extraction_mode = False

        if self.interpolation_mode:
            self.interpolation.interpolate_data(self.extraction.data_points)
            if self.calibration.calibration_done:
                self.interpolation.interpolated_real_coordinates = [
                    self.calibration.transform_point(p) for p in self.interpolation.interpolated_points
                ]
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def export_data(self):
        """Exports data points to a CSV file using a file dialog."""
        if self.extraction.real_coordinates:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "",
                                                      "CSV Files (*.csv);;All Files (*)", options=options)
            if filepath:
                if self.interpolation_mode:
                    self.data_exporter.export_to_csv(self.interpolation.interpolated_real_coordinates, filepath)
                else:
                    self.data_exporter.export_to_csv(self.extraction.real_coordinates, filepath)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()