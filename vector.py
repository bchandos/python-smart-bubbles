from math import sqrt, atan2, cos, sin

class Vector:
    """ Basic 2D Vector object with operator overrides """
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    @property
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return atan2(self.y, self.x)

    @classmethod
    def from_angle(cls, angle, magnitude=1):
        x = magnitude * cos(angle)
        y = magnitude * sin(angle)
        return cls(x, y)

    def normalize(self):
        self.x /= self.magnitude
        self.y /= self.magnitude

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __sub__(self, other):
        x = self.x + -other.x
        y = self.y + -other.y
        return Vector(x, y)

    def __mul__(self, scalar):
        # this is not dot product or cross product, just a simple vector scaling, accepting a scalar as argument
        x = self.x * scalar
        y = self.y * scalar
        return Vector(x, y)

    def __truediv__(self, scalar):
        # again, this is just simple vector scaling
        if scalar:
            x = self.x / scalar
            y = self.y / scalar
            return Vector(x, y)

    def __floordiv__(self, scalar):
        # again, this is just simple vector scaling
        if scalar:
            x = self.x // scalar
            y = self.y // scalar
            return Vector(x, y)

    def __str__(self):
        return f'Vector at ({round(self.x, 4)}, {round(self.y, 4)}), ' \
               f'of magnitude {round(self.magnitude, 4)} ' \
               f'and theta {round(self.angle, 4)}.'