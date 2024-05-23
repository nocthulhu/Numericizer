from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QPointF
from PyQt5 import QtGui

class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.pixmap_item = None
        self.zoom_factor = 1
        self.main_window = parent
        self.calibration_points_graphics = []
        self.data_points_graphics = []
        self.interpolated_points_graphics = []
        self.highlighted_point = None

    def set_image(self, image):
        if len(image.shape) == 3:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        elif len(image.shape) == 2:
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            raise ValueError("Unsupported image format")

        self.pixmap = QPixmap.fromImage(q_image)
        if self.pixmap_item is None:
            self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.pixmap_item)
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        else:
            self.pixmap_item.setPixmap(self.pixmap)
        self.update_scene()

    def wheelEvent(self, event):
        if self.pixmap_item:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            self.zoom_factor *= 1.1 ** steps
            self.scale(1.1 ** steps, 1.1 ** steps)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.pixmap_item and self.pixmap_item.contains(scene_pos):
                if self.main_window.calibration_mode:
                    self.main_window.calibration.add_calibration_point(scene_pos)
                    self.update_scene()  # Update scene to show points
                elif self.main_window.extraction_mode:
                    self.main_window.extraction.add_data_point(scene_pos)
                    self.update_scene()  # Update scene to show points
            elif not self.pixmap_item:
                QMessageBox.warning(self, "No Image Loaded", "Please load an image before adding points.")

    def draw_calibration_points(self, calibration_points):
        """Draws calibration points on the image."""
        for point_graphic in self.calibration_points_graphics:
            self.scene.removeItem(point_graphic)
        self.calibration_points_graphics = []
        for i, point in enumerate(calibration_points):
            coords = point.get_image_coordinates()
            x, y = coords.x(), coords.y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QPen(Qt.red), QBrush(Qt.red))
            text = self.scene.addText(str(i + 1), QFont('Arial', 10))
            text.setPos(x + 5, y - 10)
            text.setDefaultTextColor(Qt.red)
            self.calibration_points_graphics.append(point_graphic)
            self.calibration_points_graphics.append(text)
        if self.highlighted_point:
            x, y = self.highlighted_point.x(), self.highlighted_point.y()
            self.scene.addEllipse(x - 5, y - 5, 10, 10, QPen(Qt.yellow, 2))

    def draw_data_points(self, data_points):
        for point_graphic in self.data_points_graphics:
            self.scene.removeItem(point_graphic)
        self.data_points_graphics = []
        for point in data_points:
            coords = point.get_image_coordinates()
            x, y = coords.x(), coords.y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QPen(Qt.blue), QBrush(Qt.blue))
            self.data_points_graphics.append(point_graphic)

    def draw_interpolated_points(self, interpolated_points):
        for point_graphic in self.interpolated_points_graphics:
            self.scene.removeItem(point_graphic)
        self.interpolated_points_graphics = []
        for point in interpolated_points:
            coords = point.get_image_coordinates()
            x, y = coords.x(), coords.y()
            point_graphic = self.scene.addEllipse(x - 2, y - 2, 4, 4, QPen(Qt.green), QBrush(Qt.green))
            self.interpolated_points_graphics.append(point_graphic)

    def highlight_point(self, point):
        """Highlights a specific point on the image."""
        self.highlighted_point = point.get_image_coordinates()
        self.update_scene()

    def clear_highlight(self):
        self.highlighted_point = None
        self.update_scene()

    def update_scene(self):
        """Updates the scene to reflect the latest points and highlights."""
        self.draw_calibration_points(self.main_window.calibration.calibration_points)
        self.draw_data_points(self.main_window.extraction.data_points)
        self.draw_interpolated_points(self.main_window.interpolation.interpolated_points)
