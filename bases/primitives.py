import math


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Line:
    p1: Point
    p2: Point

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def distance(self):
        return math.dist([self.p1.x, self.p1.y], [self.p2.x, self.p2.y])


class SimulateMixin:
    def simulate(self, time_delta: float, **kwargs):
        raise NotImplementedError