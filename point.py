class Point:
    """Class to represent a point with image coordinates, real coordinates, and type."""

    def __init__(self, image_coordinates, real_coordinates=None, point_type=None):
        self.image_coordinates = image_coordinates
        self.real_coordinates = real_coordinates
        self.point_type = point_type  # Added parameter

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
