from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QPointF
from PyQt5 import QtGui

class ImageView(QGraphicsView):
    """
    Custom QGraphicsView for displaying and interacting with the image.
    Handles zooming, panning, and drawing calibration and data points.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.pixmap_item = None
        self.zoom_factor = 1
        self.main_window = parent
        self.calibration_points_graphics = []
        self.data_points_graphics = []

    def set_image(self, image):
        """Sets the image to be displayed in the view."""
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
        """Handles mouse wheel events for zooming."""
        if self.pixmap_item:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            self.zoom_factor *= 1.1 ** steps
            self.scale(1.1 ** steps, 1.1 ** steps)

    def mousePressEvent(self, event):
        """Handles mouse press events for calibration and data extraction."""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            if self.pixmap_item.contains(scene_pos):
                if self.main_window.calibration_mode:
                    self.main_window.calibration.add_calibration_point(scene_pos)
                elif self.main_window.extraction_mode:
                    self.main_window.extraction.add_data_point(scene_pos)

    def draw_calibration_points(self, calibration_points):
        """Draws calibration points on the image view."""
        for point_graphic in self.calibration_points_graphics:
            self.scene.removeItem(point_graphic)
        self.calibration_points_graphics = []

        for point in calibration_points:
            x, y = point.x(), point.y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QtGui.QPen(Qt.red), QtGui.QBrush(Qt.red))
            self.calibration_points_graphics.append(point_graphic)

    def draw_data_points(self, data_points):
        """Draws data points on the image view."""
        for point_graphic in self.data_points_graphics:
            self.scene.removeItem(point_graphic)
        self.data_points_graphics = []

        for point in data_points:
            x, y = point.x(), point.y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QtGui.QPen(Qt.blue),
                                                  QtGui.QBrush(Qt.blue))
            self.data_points_graphics.append(point_graphic)