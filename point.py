# point.py

class Point:
    def __init__(self, image_coordinates, real_coordinates=None):
        self.image_coordinates = image_coordinates
        self.real_coordinates = real_coordinates

    def get_image_coordinates(self):
        return self.image_coordinates

    def get_real_coordinates(self):
        return self.real_coordinates

    def set_image_coordinates(self, new_coords):
        self.image_coordinates = new_coords

    def set_real_coordinates(self, new_coords):
        self.real_coordinates = new_coords
