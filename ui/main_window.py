from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QListWidget, QListWidgetItem, QInputDialog, \
    QMessageBox, QToolTip
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtCore import Qt, QPointF
from ui.image_view import ImageView
from image_processing import ImageProcessor  # Adjust this import if needed
from calibration import Calibration
from data_extraction import DataExtraction
from interpolation import Interpolation
from export import DataExporter
import matplotlib.pyplot as plt
import numpy as np
import cv2


class MainWindow(QMainWindow):
    """Main application window class."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.extraction = DataExtraction(self.calibration, self)
        self.interpolation = Interpolation(self.calibration, self)
        self.data_exporter = DataExporter()

        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False
        self.feature_detection_mode = False

        self.original_image = None
        self.initUI()

    def initUI(self):
        """Initializes the user interface components."""
        self.setWindowTitle('Numericizer')
        self.setGeometry(100, 100, 1000, 600)

        self.image_view = ImageView(self)
        self.setCentralWidget(self.image_view)

        # Tooltip configuration
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is the main window of the application.')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        openAction = QAction('&Open Image', self)
        openAction.setToolTip('Open an image file for processing')
        openAction.triggered.connect(self.open_image)
        fileMenu.addAction(openAction)

        exportMenu = fileMenu.addMenu('&Export Data')
        exportCsvAction = QAction('&Export as CSV', self)
        exportCsvAction.setToolTip('Export the extracted data points as a CSV file')
        exportCsvAction.triggered.connect(self.export_data_as_csv)
        exportMenu.addAction(exportCsvAction)

        exportJsonAction = QAction('&Export as JSON', self)
        exportJsonAction.setToolTip('Export the extracted data points as a JSON file')
        exportJsonAction.triggered.connect(self.export_data_as_json)
        exportMenu.addAction(exportJsonAction)

        toolsMenu = menubar.addMenu('&Tools')
        self.calibrationAction = QAction('&Calibrate Axes', self)
        self.calibrationAction.setToolTip('Calibrate the axes using known reference points')
        self.calibrationAction.setEnabled(False)
        self.calibrationAction.triggered.connect(self.toggle_calibration_mode)
        toolsMenu.addAction(self.calibrationAction)

        self.automaticCalibrationAction = QAction('&Automatic Calibration (Experimental)', self)
        self.automaticCalibrationAction.setToolTip('Automatically calibrate the axes')
        self.automaticCalibrationAction.setEnabled(False)
        self.automaticCalibrationAction.triggered.connect(self.automatic_calibration)
        toolsMenu.addAction(self.automaticCalibrationAction)

        self.extractionAction = QAction('&Extract Data', self)
        self.extractionAction.setToolTip('Extract data points from the image')
        self.extractionAction.setEnabled(False)
        self.extractionAction.triggered.connect(self.toggle_extraction_mode)
        toolsMenu.addAction(self.extractionAction)

        self.interpolationAction = QAction('&Interpolate Data', self)
        self.interpolationAction.setToolTip('Interpolate data points between the extracted points')
        self.interpolationAction.setEnabled(False)
        self.interpolationAction.triggered.connect(self.toggle_interpolation_mode)
        toolsMenu.addAction(self.interpolationAction)

        self.detected_points_action = QAction('&Advanced Feature Detection', self)
        self.detected_points_action.setToolTip('Detect advanced features like lines and intersections in the image')
        self.detected_points_action.setEnabled(False)
        self.detected_points_action.triggered.connect(self.toggle_feature_detection_mode)
        toolsMenu.addAction(self.detected_points_action)

        imageProcessingMenu = menubar.addMenu('&Image Processing')
        self.histogramAction = QAction('&Equalize Histogram', self)
        self.histogramAction.setToolTip('Apply histogram equalization to the image')
        self.histogramAction.setEnabled(False)
        self.histogramAction.triggered.connect(self.equalize_histogram)
        imageProcessingMenu.addAction(self.histogramAction)

        self.edgeAction = QAction('&Edge Detection', self)
        self.edgeAction.setToolTip('Apply edge detection to the image')
        self.edgeAction.setEnabled(False)
        self.edgeAction.triggered.connect(self.edge_detection)
        imageProcessingMenu.addAction(self.edgeAction)

        self.denoiseAction = QAction('&Denoise Image', self)
        self.denoiseAction.setToolTip('Apply denoising to the image')
        self.denoiseAction.setEnabled(False)
        self.denoiseAction.triggered.connect(self.denoise_image)
        imageProcessingMenu.addAction(self.denoiseAction)

        self.perspectiveAction = QAction('&Correct Perspective', self)
        self.perspectiveAction.setToolTip('Correct the perspective of the image')
        self.perspectiveAction.setEnabled(False)
        self.perspectiveAction.triggered.connect(self.toggle_perspective_mode)
        imageProcessingMenu.addAction(self.perspectiveAction)

        self.rotateAction = QAction('&Rotate Image', self)
        self.rotateAction.setToolTip('Rotate the image by a specified angle')
        self.rotateAction.setEnabled(False)
        self.rotateAction.triggered.connect(self.rotate_image)
        imageProcessingMenu.addAction(self.rotateAction)

        self.data_points_list = self.init_data_points_list()
        deletePointAction = QAction('&Delete Data Point', self)
        deletePointAction.setToolTip('Delete a selected data point')
        deletePointAction.triggered.connect(self.delete_data_point)
        toolsMenu.addAction(deletePointAction)

        self.show_data_points()

        viewMenu = self.menuBar().addMenu('&View')
        plotPointsAction = QAction('&Plot Data Points', self)
        plotPointsAction.setToolTip('Plot the extracted data points')
        plotPointsAction.triggered.connect(self.plot_data_points)
        viewMenu.addAction(plotPointsAction)

    def init_data_points_list(self):
        data_points_list = QListWidget(self)
        data_points_list.setGeometry(800, 50, 200, 500)
        data_points_list.itemDoubleClicked.connect(self.edit_data_point)
        return data_points_list

    def open_image(self):
        """Opens an image file and displays it."""
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
            self.detected_points_action.setEnabled(True)

    def toggle_extraction_mode(self):
        """Toggles the data extraction mode."""
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 4:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before extraction. Please calibrate at least 4 points.")
            return

        self.image_view.update_scene()
        self.image_view.update()
        self.extraction_mode = not self.extraction_mode
        self.feature_detection_mode = False
        self.calibration_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.extraction_mode else Qt.ArrowCursor))

        if self.extraction_mode:
            if self.image_processor.image is not None:
                print("Extraction mode enabled.")
            else:
                print("Load an image first.")
        else:
            print("Extraction mode disabled.")
        self.image_view.selection_mode = not self.extraction_mode

        self.image_view.update_scene()
        self.image_view.update()

    def advanced_feature_detection(self):
        """Performs advanced feature detection on the image."""
        if self.image_processor.image is not None:
            print("Running advanced feature detection...")
            result_image = self.extraction.automatic_extraction(self.image_processor.image)
            self.image_view.set_image(result_image)
        else:
            print("Load an image first.")

    def correct_perspective(self, points):
        """Corrects the perspective of the image using four points."""
        if len(points) != 4:
            return
        pts1 = np.float32([[point.x(), point.y()] for point in points])
        width, height = self.image_processor.image.shape[1], self.image_processor.image.shape[0]
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        self.image_processor.correct_perspective(pts1, pts2)
        self.update_image()

    def toggle_feature_detection_mode(self):
        """Toggles the advanced feature detection mode."""
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 4:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before feature detection. Please calibrate at least 4 points.")
            return

        self.image_view.update_scene()
        self.feature_detection_mode = not self.feature_detection_mode
        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.feature_detection_mode else Qt.ArrowCursor))

        if self.feature_detection_mode:
            if self.image_processor.image is not None:
                print("Running advanced feature detection...")
                result_image = self.extraction.automatic_extraction(self.image_processor.image)
                self.image_view.set_image(result_image)
                self.image_view.draw_detected_points(self.extraction.temp_points)
            else:
                print("Load an image first.")
        else:
            self.extraction.clear_temp_points()
            self.image_view.clear_detected_points()
            self.image_view.update_scene()
        self.image_view.selection_mode = not self.feature_detection_mode

    def mousePressEvent(self, event):
        """Handles mouse press events to select data points."""
        if event.button() == Qt.LeftButton and self.feature_detection_mode:
            pos = event.pos()
            scene_pos = self.image_view.mapToScene(pos)
            items = self.image_view.items(scene_pos.toPoint())
            for item in items:
                if isinstance(item, QGraphicsEllipseItem):
                    point = item.data(0)
                    if point in self.extraction.temp_points:
                        self.extraction.add_data_point(point)
                        self.show_data_points()
                        self.update_image()
                        break

    def toggle_perspective_mode(self):
        self.image_view.update_scene()
        """Toggles the perspective correction mode."""
        self.perspective_mode = not self.perspective_mode
        self.calibration_mode = False
        self.extraction_mode = False
        self.interpolation_mode = False
        self.feature_detection_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.perspective_mode else Qt.ArrowCursor))
        self.update_perspective_info()
        self.image_view.selection_mode = not self.perspective_mode

    def update_perspective_info(self):
        """Updates the informational label for perspective correction."""
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
        """Rotates the image by a specified angle."""
        angle, ok = QInputDialog.getDouble(self, "Rotate Image", "Enter angle (degrees) (clockwise):", 0, -360, 360, 1)
        if ok and self.image_processor.image is not None:
            self.image_processor.rotate_image(angle)
            self.update_image()

    def update_image(self):
        """Updates the displayed image."""
        if self.image_processor.image is not None:
            self.image_view.set_image(self.image_processor.image)

    def equalize_histogram(self):
        """Equalizes the histogram of the image."""
        self.image_processor.equalize_histogram()
        self.update_image()

    def edge_detection(self):
        """Applies edge detection to the image."""
        self.image_processor.edge_detection()
        self.update_image()

    def denoise_image(self):
        """Applies denoising to the image."""
        self.image_processor.denoise_image()
        self.update_image()

    def toggle_calibration_mode(self):
        """Toggles the calibration mode."""
        self.calibration_mode = not self.calibration_mode
        self.extraction_mode = False
        self.interpolation_mode = False
        self.perspective_mode = False
        self.feature_detection_mode = False
        self.setCursor(QCursor(Qt.CrossCursor if self.calibration_mode else Qt.ArrowCursor))
        self.image_view.selection_mode = not self.calibration_mode

    def toggle_interpolation_mode(self):
        """Toggles the interpolation mode."""
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 4:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before interpolation. Please calibrate at least 4 points.")
            return

        self.interpolation_mode = not self.interpolation_mode
        self.calibration_mode = False
        self.extraction_mode = False
        self.feature_detection_mode = False
        self.perspective_mode = False

        if self.interpolation_mode:
            if len(self.extraction.data_points) >= 2:
                self.interpolation.calibration = self.calibration
                print("Interpolation mode activated.")
                print("Data points:", self.extraction.get_data_points())
                self.interpolation.interpolate_data(self.extraction.get_data_points())
                self.show_data_points()
                self.update_image()
            else:
                QMessageBox.warning(self, "Insufficient Data Points",
                                    "At least 2 data points are required for interpolation.")
                self.interpolation_mode = False
        self.image_view.selection_mode = not self.interpolation_mode

    def export_data_as_csv(self):
        """Exports the data points as a CSV file."""
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 4:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before exporting data points. Please calibrate at least 4 points.")
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
        """Exports the data points as a JSON file."""
        if not self.calibration.calibration_done or len(self.calibration.calibration_points) < 4:
            QMessageBox.warning(self, "Calibration Required",
                                "Calibration is required before exporting data points. Please calibrate at least 4 points.")
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

    # Automatic calibration handler in main_window.py
    def automatic_calibration(self):
        """Performs automatic calibration of the image."""
        if self.image_processor.image is not None:
            print("Running automatic calibration...")
            self.calibration.automatic_calibration(self.image_processor.image)
        else:
            print("Load an image first.")

    def show_data_points(self):
        """Displays the list of data points."""
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
        """Edits the selected data point."""
        index = self.data_points_list.row(item)
        total_points = len(self.extraction.get_data_points())
        if index < total_points:
            point = self.extraction.data_points[index]
            coords = point.get_real_coordinates()
            x, ok_x = QInputDialog.getDouble(self, "Edit Point", "X Coordinate:", coords.x(), -10000, 10000, 2)
            y, ok_y = QInputDialog.getDouble(self, "Edit Point", "Y Coordinate:", coords.y(), -10000, 10000, 2)
            if ok_x and ok_y:
                new_coords = QPointF(x, y)
                point.set_image_coordinates(new_coords)
                point.set_real_coordinates(self.calibration.image_to_real_coordinates(new_coords))
                self.image_view.update_scene()
                self.show_data_points()
        else:
            QMessageBox.warning(self, "Invalid Selection", "Cannot edit an interpolated point.")

    def delete_data_point(self):
        """Deletes a selected data point."""
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
        """Plots the data points using matplotlib."""
        data_points = self.extraction.get_data_points()
        if not data_points:
            print("No data points to plot.")
            return

        valid_data_points = [point for point in data_points if point.get_real_coordinates() is not None]
        x_coords = [point.get_real_coordinates().x() for point in valid_data_points]
        y_coords = [point.get_real_coordinates().y() for point in valid_data_points]

        plt.scatter(x_coords, y_coords, c='blue', label='Data Points')

        if self.interpolation_mode and self.interpolation.interpolated_points:
            valid_interpolated_points = [point for point in self.interpolation.interpolated_points if
                                         point.get_real_coordinates() is not None]
            x_interp_coords = [point.get_real_coordinates().x() for point in valid_interpolated_points]
            y_interp_coords = [point.get_real_coordinates().y() for point in valid_interpolated_points]
            plt.scatter(x_interp_coords, y_interp_coords, c='red', label='Interpolated Points')

        plt.xlabel('X Coordinates')
        plt.ylabel('Y Coordinates')
        plt.title('Data Points Plot')
        plt.legend()
        plt.show()
