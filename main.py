from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QFileDialog, QSlider, QHBoxLayout,\
    QVBoxLayout, \
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QAction, QMenu, QMenuBar
from PyQt5.QtGui import QPixmap, QImage, QCursor
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
        self.main_window = parent

    def set_image(self, image):
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
        if self.pixmap_item:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            self.zoom_factor *= 1.1 ** steps
            self.scale(1.1 ** steps, 1.1 ** steps)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.main_window.calibration_mode:  # use main_window referance
                self.main_window.calibration.add_calibration_point(self.mapToScene(event.pos()))
            elif self.main_window.extraction_mode:  # use main_window referance
                self.main_window.data_extraction.add_data_point(self.mapToScene(event.pos()))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.calibration = Calibration(self)
        self.data_extraction = DataExtraction(self, self.calibration)
        self.data_exporter = DataExporter()
        self.initUI()

        self.calibration_mode = False
        self.extraction_mode = False

        self.original_image = None

    def initUI(self):
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

        exportAction = QAction('&Export Data', self)
        exportAction.triggered.connect(self.export_data)
        toolsMenu.addAction(exportAction)

        interpolateAction = QAction('&Interpolate Data', self)
        interpolateAction.triggered.connect(self.interpolate_data)
        toolsMenu.addAction(interpolateAction)
        # Toolbar
        toolbar = self.addToolBar('Tools')
        toolbar.addAction(calibrationAction)
        toolbar.addAction(extractionAction)
        toolbar.addAction(exportAction)
        toolbar.addAction(interpolateAction)

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

    def adjust_contrast(self, value):
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
        """Updates the image view with the processed image."""
        if self.image_processor.image is not None:
            self.image_view.set_image(self.image_processor.image)

    def toggle_calibration_mode(self):
        self.calibration_mode = not self.calibration_mode
        self.extraction_mode = False
        if self.calibration_mode:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_extraction_mode(self):
        self.extraction_mode = not self.extraction_mode
        self.calibration_mode = False
        if self.extraction_mode:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def export_data(self):
        if self.data_extraction.data_points:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Data", "",
                                                      "CSV Files (*.csv);;All Files (*)", options=options)
            if filepath:
                self.data_exporter.export_to_csv(self.data_extraction.data_points, filepath)

    def interpolate_data(self):
        self.data_extraction.interpolate_data()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
