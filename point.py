class Point:
    def __init__(self, image_coordinates, real_coordinates=None, point_type=None):
        """Initializes a Point with image, real coordinates, and type."""
        self.image_coordinates = image_coordinates
        self.real_coordinates = real_coordinates
        self.point_type = point_type  # Yeni eklenen parametre

    def get_image_coordinates(self):
        """Returns the image coordinates."""
        return self.image_coordinates

    def get_real_coordinates(self):
        """Returns the real coordinates."""
        return self.real_coordinates

    def set_image_coordinates(self, new_coords):
        """Sets new image coordinates."""
        self.image_coordinates = new_coords

    def set_real_coordinates(self, new_coords):
        """Sets new real coordinates."""
        self.real_coordinates = new_coords

    def get_point_type(self):
        """Returns the point type."""
        return self.point_type

    def set_point_type(self, point_type):
        """Sets a new point type."""
        self.point_type = point_type