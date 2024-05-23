
from point import Point

class Extraction:
    def __init__(self):
        self.data_points = []  # List of Point objects

    def add_data_point(self, point):
        if len(self.data_points) < 10:  # Örneğin maksimum 10 nokta
            point_obj = Point(point, point_type='data')
            self.data_points.append(point_obj)

    def edit_data_point(self, index, new_point):
        if 0 <= index < len(self.data_points):
            self.data_points[index].set_image_coordinates(new_point)

    def delete_data_point(self, index):
        if 0 <= index < len(self.data_points):
            self.data_points.pop(index)

    def get_data_points(self):
        return self.data_points

    def clear_data_points(self):
        self.data_points = []