# main.py

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
from point import Point

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
        self.setWindowTitle('Numericizer')
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

        automaticCalibrationAction = QAction('&Automatic Calibration', self)
        automaticCalibrationAction.triggered.connect(self.automatic_calibration)
        toolsMenu.addAction(automaticCalibrationAction)

        extractionAction = QAction('&Extract Data', self)
        extractionAction.triggered.connect(self.toggle_extraction_mode)
        toolsMenu.addAction(extractionAction)

        interpolationAction = QAction('&Interpolate Data', self)
        interpolationAction.triggered.connect(self.toggle_interpolation_mode)
        toolsMenu.addAction(interpolationAction)

        # New Image Processing Actions
        histogramAction = QAction('&Equalize Histogram', self)
        histogramAction.triggered.connect(self.equalize_histogram)
        toolsMenu.addAction(histogramAction)

        edgeAction = QAction('&Edge Detection', self)
        edgeAction.triggered.connect(self.edge_detection)
        toolsMenu.addAction(edgeAction)

        denoiseAction = QAction('&Denoise Image', self)
        denoiseAction.triggered.connect(self.denoise_image)
        toolsMenu.addAction(denoiseAction)

    def open_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_path:
            self.image_processor.load_image(file_path)
            self.original_image = self.image_processor.image.copy()
            self.image_view.set_image(self.image_processor.image)

    def update_image(self):
        if self.image_processor.image is not None:
            self.image_view.set_image(self.image_processor.image)

    def equalize_histogram(self):
        self.image_processor.equalize_histogram()
        self.update_image()

    def edge_detection(self):
        self.image_processor.edge_detection()
        self.update_image()

    def denoise_image(self):
        self.image_processor.denoise_image()
        self.update_image()

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
            print("Interpolation mode activated.")
            print("Data points:", self.extraction.data_points)
            self.interpolation.interpolate_data(self.extraction.data_points)
            self.update_image()

    def export_data(self):
        if self.calibration.calibration_done:
            if self.interpolation_mode:
                real_coordinates = [point.get_real_coordinates() for point in self.interpolation.interpolated_points]
            else:
                real_coordinates = [point.get_real_coordinates() for point in self.extraction.data_points]
            if real_coordinates:
                options = QFileDialog.Options()
                filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
                if filepath:
                    self.data_exporter.export_to_csv(real_coordinates, filepath)
        else:
            print("Calibration is required before exporting data points.")

    def automatic_calibration(self):
        if self.image_processor.image is not None:
            print("Running automatic calibration...")
            self.calibration.automatic_calibration(self.image_processor.image)
        else:
            print("Load an image first.")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
