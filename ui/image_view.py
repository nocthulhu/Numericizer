from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem, QLabel
from PyQt5.QtGui import QPixmap, QImage, QPen, QBrush, QFont, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF
import numpy as np

class ImageView(QGraphicsView):
    """Class to handle displaying images and interacting with points on the image."""

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
        self.detected_points_graphics = []  # List to hold graphics items for detected points
        self.highlighted_points = []
        self.perspective_points = []
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("QLabel { background-color : white; color : black; }")
        self.info_label.setFixedWidth(200)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.hide()

    def set_image(self, image):
        """Sets and displays the given image in the view."""
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
        """Handles zooming in and out using the mouse wheel."""
        if self.pixmap_item:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            self.zoom_factor *= 1.1 ** steps
            self.scale(1.1 ** steps, 1.1 ** steps)

    def mousePressEvent(self, event):
        """Handles mouse click events to add points or perform perspective correction."""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.pixmap_item and self.pixmap_item.contains(scene_pos):
                if self.main_window.calibration_mode:
                    self.main_window.calibration.add_calibration_point(scene_pos)
                    self.update_scene()  # Update scene to show points
                elif self.main_window.extraction_mode:
                    self.main_window.extraction.add_data_point(scene_pos)
                    self.update_scene()  # Update scene to show points
                elif self.main_window.perspective_mode:
                    self.add_perspective_point(scene_pos)
                    if len(self.perspective_points) == 4:
                        self.main_window.correct_perspective(self.perspective_points)
                        self.perspective_points.clear()
                        self.info_label.hide()
                    else:
                        self.main_window.update_perspective_info()
                    self.update_scene()
                elif self.main_window.feature_detection_mode:
                    for point in self.main_window.extraction.temp_points:  # Use temp_points instead of detected_points
                        if point.x() - 3 <= scene_pos.x() <= point.x() + 3 and \
                                point.y() - 3 <= scene_pos.y() <= point.y() + 3:
                            self.main_window.extraction.add_data_point(point)
                            self.main_window.show_data_points()
                            self.update_scene()
                            break
    def add_perspective_point(self, point):
        """Adds a point for perspective correction."""
        ellipse = QGraphicsEllipseItem(point.x() - 5, point.y() - 5, 10, 10)
        ellipse.setBrush(QBrush(Qt.red))
        ellipse.setPen(QPen(Qt.red))
        self.scene.addItem(ellipse)
        self.perspective_points.append(point)

    def draw_calibration_points(self, calibration_points):
        """Draws calibration points on the image."""
        for point_graphic in self.calibration_points_graphics:
            self.scene.removeItem(point_graphic)
        self.calibration_points_graphics = []
        for i, point in enumerate(calibration_points):
            coords = point.get_image_coordinates()
            x = coords.x()
            y = coords.y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QPen(Qt.red), QBrush(Qt.red))
            text = self.scene.addText(str(i + 1), QFont('Arial', 10))
            text.setPos(x + 5, y - 10)
            text.setDefaultTextColor(Qt.red)
            self.calibration_points_graphics.append(point_graphic)
            self.calibration_points_graphics.append(text)



    def draw_detected_corners(self, corners):
        """Draws detected corners on the image."""
        for point_graphic in self.detected_points_graphics:
            self.scene.removeItem(point_graphic)
        self.detected_points_graphics = []
        for corner in corners:
            x, y = corner.ravel()
            point_graphic = self.scene.addEllipse(x - 1.5, y - 1.5, 3, 3, QPen(Qt.green), QBrush(Qt.green))
            self.detected_points_graphics.append(point_graphic)
        self.update()
    def draw_data_points(self, data_points):
        """Draws data points on the image."""
        for point_graphic in self.data_points_graphics:
            self.scene.removeItem(point_graphic)
        self.data_points_graphics = []
        for point in data_points:
            x = point.get_image_coordinates().x()
            y = point.get_image_coordinates().y()
            point_graphic = self.scene.addEllipse(x - 3, y - 3, 6, 6, QPen(Qt.blue), QBrush(Qt.blue))
            self.data_points_graphics.append(point_graphic)

    def draw_interpolated_points(self, interpolated_points):
        """Draws interpolated points on the image."""
        for point_graphic in self.interpolated_points_graphics:
            self.scene.removeItem(point_graphic)
        self.interpolated_points_graphics = []
        for point in interpolated_points:
            x = point.get_image_coordinates().x()
            y = point.get_image_coordinates().y()
            point_graphic = self.scene.addEllipse(x - 2, y - 2, 4, 4, QPen(Qt.green), QBrush(Qt.green))
            self.interpolated_points_graphics.append(point_graphic)

    def draw_detected_points(self, detected_points):
        """Draws detected points on the image."""
        for point_graphic in self.detected_points_graphics:
            self.scene.removeItem(point_graphic)
        self.detected_points_graphics = []
        for point in detected_points:
            x = point.x()
            y = point.y()
            point_graphic = self.scene.addEllipse(x - 2, y - 2, 4, 4, QPen(Qt.green),
                                                  QBrush(Qt.green))
            self.detected_points_graphics.append(point_graphic)

    def highlight_point(self, point):
        """Highlights a specific point by adding it to the highlighted points list."""
        self.highlighted_points.append(point)
        self.update_scene()

    def draw_highlights(self):
        """Draws highlighted points on the image."""
        for point in self.highlighted_points:
            coords = point.get_image_coordinates()
            ellipse = QGraphicsEllipseItem(coords.x() - 5, coords.y() - 5, 10, 10)
            ellipse.setBrush(QBrush(Qt.yellow))
            ellipse.setPen(QPen(Qt.yellow))
            self.scene.addItem(ellipse)

    def delete_highlight(self, point):
        """Deletes a specific highlight from the image."""
        new_highlighted_points = []
        for highlighted_point in self.highlighted_points:
            if highlighted_point != point:
                new_highlighted_points.append(highlighted_point)
            else:
                coords = highlighted_point.get_image_coordinates()
                items = self.scene.items(QRectF(coords.x() - 5, coords.y() - 5, 10, 10))
                for item in items:
                    if isinstance(item, QGraphicsEllipseItem):
                        self.scene.removeItem(item)
        self.highlighted_points = new_highlighted_points
        self.update_scene()

    def clear_highlights(self):
        """Clears all highlighted points from the image."""
        for point in self.highlighted_points:
            coords = point.get_image_coordinates()
            items = self.scene.items(QRectF(coords.x() - 5, coords.y() - 5, 10, 10))
            for item in items:
                if isinstance(item, QGraphicsEllipseItem):
                    self.scene.removeItem(item)
        self.highlighted_points = []
        self.update_scene()

    def clear_calibration_points(self):
        """Clears all calibration points from the image."""
        for point_graphic in self.calibration_points_graphics:
            self.scene.removeItem(point_graphic)
        self.calibration_points_graphics = []
        for point, _ in self.highlighted_points:
            self.delete_highlight(point)
        self.update()
    def clear_detected_points(self):
        """Clears all detected points from the scene."""
        for point_graphic in self.detected_points_graphics:
            self.scene.removeItem(point_graphic)
        self.detected_points_graphics = []

    def update_scene(self):
        """Updates the scene with the current points and image."""
        if self.main_window.feature_detection_mode:
            self.draw_detected_points(self.main_window.extraction.temp_points)
        else:
            self.main_window.extraction.clear_temp_points()
            self.clear_detected_points()
        self.draw_highlights()
        self.draw_calibration_points(self.main_window.calibration.calibration_points)
        self.draw_data_points(self.main_window.extraction.data_points)
        self.draw_interpolated_points(self.main_window.interpolation.interpolated_points)

        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    def show_info_label(self, text):
        """Displays an informational label."""
        self.info_label.setText(text)
        self.info_label.adjustSize()
        self.info_label.show()