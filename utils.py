from bases.primitives import Point, Line


def gen_lines_around(point: Point):
    line1 = Line(Point(point.x + 2.5, point.y), Point(point.x + 17.5, point.y))
    line2 = Line(Point(point.x - 2.5, point.y), Point(point.x - 17.5, point.y))
    line3 = Line(Point(point.x, point.y - 2.5), Point(point.x, point.y - 17.5))
    line4 = Line(Point(point.x, point.y + 2.5), Point(point.x, point.y + 17.5))

    return line1, line2, line3, line4
