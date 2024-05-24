from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QPointF
from image_view import ImageView
from image_processor import ImageProcessor
from calibration import Calibration
from data_extraction import Extraction
from interpolation import Interpolation
from data_exporter import DataExporter
import matplotlib.pyplot as plt
import numpy as np
import cv2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.extraction = Extraction()
        self.interpolation = Interpolation(self.calibration)
        self.data_exporter = DataExporter()

        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False

        self.original_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Numericizer')
        self.setGeometry(100, 100, 1000, 600)

        self.image_view = ImageView(self)
        self.setCentralWidget(self.image_view)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        openAction = QAction('&Open Image', self)
        openAction.triggered.connect(self.open_image)
        fileMenu.addAction(openAction)

        exportMenu = fileMenu.addMenu('&Export Data')
        exportCsvAction = QAction('&Export as CSV', self)
        exportCsvAction.triggered.connect(self.export_data_as_csv)
        exportMenu.addAction(exportCsvAction)

        exportJsonAction = QAction('&Export as JSON', self)
        exportJsonAction.triggered.connect(self.export_data_as_json)
        exportMenu.addAction(exportJsonAction)

        toolsMenu = menubar.addMenu('&Tools')
        self.calibrationAction = QAction('&Calibrate Axes', self)
        self.calibrationAction.setEnabled(False)
        self.calibrationAction.triggered.connect(self.toggle_calibration_mode)
        toolsMenu.addAction(self.calibrationAction)

        self.automaticCalibrationAction = QAction('&Automatic Calibration (Experimental)', self)
        self.automaticCalibrationAction.setEnabled(False)
        self.automaticCalibrationAction.triggered.connect(self.automatic_calibration)
        toolsMenu.addAction(self.automaticCalibrationAction)

        self.extractionAction = QAction('&Extract Data', self)
        self.extractionAction.setEnabled(False)
        self.extractionAction.triggered.connect(self.toggle_extraction_mode)
        toolsMenu.addAction(self.extractionAction)

        self.interpolationAction = QAction('&Interpolate Data', self)
        self.interpolationAction.setEnabled(False)
        self.interpolationAction.triggered.connect(self.toggle_interpolation_mode)
        toolsMenu.addAction(self.interpolationAction)

        imageProcessingMenu = menubar.addMenu('&Image Processing')
        self.histogramAction = QAction('&Equalize Histogram', self)
        self.histogramAction.setEnabled(False)
        self.histogramAction.triggered.connect(self.equalize_histogram)
        imageProcessingMenu.addAction(self.histogramAction)

        self.edgeAction = QAction('&Edge Detection', self)
        self.edgeAction.setEnabled(False)
        self.edgeAction.triggered.connect(self.edge_detection)
        imageProcessingMenu.addAction(self.edgeAction)

        self.denoiseAction = QAction('&Denoise Image', self)
        self.denoiseAction.setEnabled(False)
        self.denoiseAction.triggered.connect(self.denoise_image)
        imageProcessingMenu.addAction(self.denoiseAction)

        self.perspectiveAction = QAction('&Correct Perspective', self)
        self.perspectiveAction.setEnabled(False)
        self.perspectiveAction.triggered.connect(self.toggle_perspective_mode)
        imageProcessingMenu.addAction(self.perspectiveAction)

        self.rotateAction = QAction('&Rotate Image', self)
        self.rotateAction.setEnabled(False)
        self.rotateAction.triggered.connect(self.rotate_image)
        imageProcessingMenu.addAction(self.rotateAction)

        self.data_points_list = QListWidget(self)
        self.data_points_list.setGeometry(800, 50, 200, 500)
        self.data_points_list.itemDoubleClicked.connect(self.edit_data_point)

        deletePointAction = QAction('&Delete Data Point', self)
        deletePointAction.triggered.connect(self.delete_data_point)
        toolsMenu.addAction(deletePointAction)

        self.show_data_points()

        viewMenu = self.menuBar().addMenu('&View')
        plotPointsAction = QAction('&Plot Data Points', self)
        plotPointsAction.triggered.connect(self.plot_data_points)
        viewMenu.addAction(plotPointsAction)

    def open_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "",
                                                   "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)",
                                                   options=options)
        if file_path:
            self.image_processor.load_image(file_path)
            self.original_image = self.image_processor.image.copy()
            self.image_view.set_image(self.image_processor.image)

            self.calibrationAction.setEnabled(True)
            self.automaticCalibrationAction.setEnabled(True)
            self.extractionAction.setEnabled(True)
            self.histogramAction.setEnabled(True)
            self.edgeAction.setEnabled(True)
            self.denoiseAction.setEnabled(True)
            self.perspectiveAction.setEnabled(True)
            self.rotateAction.setEnabled(True)

    def correct_perspective(self, points):
        if len(points) != 4:
            return
        pts1 = np.float32([[point.x(), point.y()] for point in points])
        width, height = self.image_processor.image.shape[1], self.image_processor.image.shape[0]
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        self.image_processor.correct_perspective(pts1, pts2)
        self.update_image()

    def toggle_perspective_mode(self):
        self.perspective_mode = not self.perspective_mode
        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.perspective_mode else Qt.ArrowCursor))
        self.update_perspective_info()

    def update_perspective_info(self):
        messages = [
            "Please select the top-left corner",
            "Please select the top-right corner",
            "Please select the bottom-left corner",
            "Please select the bottom-right corner"
        ]
        if self.perspective_mode and len(self.image_view.perspective_points) < 4:
            self.image_view.show_info_label(messages[len(self.image_view.perspective_points)])
        else:
            self.image_view.info_label.hide()

    def rotate_image(self):
        angle, ok = QInputDialog.getDouble(self, "Rotate Image", "Enter angle (degrees) (clockwise):", 0, -360, 360, 1)
        if ok and self.image_processor.image is not None:
            self.image_processor.rotate_image(angle)
            self.update_image()

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
        self.perspective_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.calibration_mode else Qt.ArrowCursor))

    def toggle_extraction_mode(self):
        self.extraction_mode = not self.extraction_mode
        self.calibration_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.extraction_mode else Qt.ArrowCursor))

    def toggle_interpolation_mode(self):
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 3:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before interpolation. Please calibrate at least 3 points.")
            return

        self.interpolation_mode = not self.interpolation_mode
        self.calibration_mode = False
        self.extraction_mode = False
        self.perspective_mode = False

        if self.interpolation_mode:
            self.interpolation.calibration = self.calibration
            print("Interpolation mode activated.")
            print("Data points:", self.extraction.data_points)
            self.interpolation.interpolate_data(self.extraction.data_points)
            self.show_data_points()
            self.update_image()

    def export_data_as_csv(self):
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 3:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before exporting data points. Please calibrate at least 3 points.")
            return

        if self.interpolation_mode:
            real_coordinates = [point.get_real_coordinates() for point in self.interpolation.interpolated_points]
        else:
            real_coordinates = [point.get_real_coordinates() for point in self.extraction.data_points]

        if real_coordinates:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv);;All Files (*)",
                                                      options=options)
            if filepath:
                self.data_exporter.export_to_csv(real_coordinates, filepath)

    def export_data_as_json(self):
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 3:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before exporting data points. Please calibrate at least 3 points.")
            return

        if self.interpolation_mode:
            real_coordinates = [point.get_real_coordinates() for point in self.interpolation.interpolated_points]
        else:
            real_coordinates = [point.get_real_coordinates() for point in self.extraction.data_points]

        if real_coordinates:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json);;All Files (*)",
                                                      options=options)
            if filepath:
                self.data_exporter.export_to_json(real_coordinates, filepath)

    def automatic_calibration(self):
        if self.image_processor.image is not None:
            print("Running automatic calibration...")
            self.calibration.automatic_calibration(self.image_processor.image)
        else:
            print("Load an image first.")

    def show_data_points(self):
        self.data_points_list.clear()
        data_points = self.extraction.get_data_points()
        interpolated_points = self.interpolation.interpolated_points if self.interpolation_mode else []

        for i, point in enumerate(data_points):
            item = QListWidgetItem(f"Data Point {i + 1}: {point.get_real_coordinates()}")
            self.data_points_list.addItem(item)

        for i, point in enumerate(interpolated_points):
            item = QListWidgetItem(f"Interpolated Point {i + 1}: {point.get_real_coordinates()}")
            self.data_points_list.addItem(item)

    def edit_data_point(self, item):
        index = self.data_points_list.row(item)
        total_points = len(self.extraction.get_data_points())

        if index < total_points:
            point = self.extraction.get_data_points()[index]
            x, y = point.get_real_coordinates()
        else:
            point = self.interpolation.interpolated_points[index - total_points]
            x, y = point.get_real_coordinates()

        if x is None or y is None:
            return

        new_x, ok = QInputDialog.getDouble(self, "Edit Data Point", "New X Coordinate:", x)
        if ok:
            new_y, ok = QInputDialog.getDouble(self, "Edit Data Point", "New Y Coordinate:", y)
            if ok:
                new_point = (new_x, new_y)
                if index < total_points:
                    self.extraction.edit_data_point(index, QPointF(*new_point))
                else:
                    self.interpolation.interpolated_points[index - total_points].set_real_coordinates(new_point)
                self.show_data_points()
                self.update_image()

    def delete_data_point(self):
        items = self.data_points_list.selectedItems()
        total_points = len(self.extraction.get_data_points())

        if items:
            for item in items:
                index = self.data_points_list.row(item)
                if index < total_points:
                    self.extraction.delete_data_point(index)
                else:
                    self.interpolation.interpolated_points.pop(index - total_points)
                self.show_data_points()
                self.update_image()

    def plot_data_points(self):
        data_points = self.extraction.get_data_points()
        if not data_points:
            print("No data points to plot.")
            return

        valid_data_points = [point for point in data_points if point.get_real_coordinates() is not None]
        x_coords = [point.get_real_coordinates()[0] for point in valid_data_points]
        y_coords = [point.get_real_coordinates()[1] for point in valid_data_points]

        plt.scatter(x_coords, y_coords, c='blue', label='Data Points')

        if self.interpolation_mode and self.interpolation.interpolated_points:
            valid_interpolated_points = [point for point in self.interpolation.interpolated_points if
                                         point.get_real_coordinates() is not None]
            x_interp_coords = [point.get_real_coordinates()[0] for point in valid_interpolated_points]
            y_interp_coords = [point.get_real_coordinates()[1] for point in valid_interpolated_points]
            plt.scatter(x_interp_coords, y_interp_coords, c='red', label='Interpolated Points')

        plt.xlabel('X Coordinates')
        plt.ylabel('Y Coordinates')
        plt.title('Data Points Plot')
        plt.legend()
        plt.show()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
