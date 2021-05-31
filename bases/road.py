from __future__ import annotations

from typing import List
from .car import Car, DEFAULT_CAR_LENGTH
from .primitives import Point, Line


class Semaphore:
    GREEN = 1
    RED = 2

    state: int  # GREEN, RED

    def __init__(self):
        self.state = self.RED

    def switch(self):
        if self.state == self.GREEN:
            self.state = self.RED
        else:
            self.state = self.GREEN


class CrossRoad:
    X_TYPE = 1  # Х-образный перекресток
    T_TYPE = 2  # Т-образный перекресток
    type: int
    lines_map: dict

    def __init__(self, left_road: RoadPart, right_road: RoadPart, forward_road: RoadPart, backward_road: RoadPart):
        road_lines = [left_road, forward_road, right_road, backward_road]
        count = len(list(filter(lambda road: road is not None, road_lines)))
        if count < 3:
            raise ValueError('Required at least 3 roads')
        if count == 3:
            self.type = self.T_TYPE
        elif count == 4:
            self.type = self.X_TYPE

        # сопоставление доступных полос
        self.lines_map = {}

        direction_flag = True
        for _ in range(0, 4):
            road = road_lines[0]
            if road:
                line = road.get_first_line(direction=direction_flag)
                if line:
                    allowed_lines = []
                    oncoming_road = road_lines[2]
                    if oncoming_road:
                        line = oncoming_road.get_first_line(direction=direction_flag)
                        if line:
                            allowed_lines.append(line)
                    left_relative_road = road_lines[1]
                    if left_relative_road:
                        line = left_relative_road.get_first_line(direction=direction_flag)
                        if line:
                            allowed_lines.append(line)
                    right_relative_road = road_lines[3]
                    if right_relative_road:
                        line = right_relative_road.get_first_line(direction=not direction_flag)
                        if line:
                            allowed_lines.append(line)
                    self.lines_map[line] = allowed_lines
            direction_flag = not direction_flag
            road_lines.append(road_lines.pop(0))


class DriveLine:
    direction: bool
    road: RoadPart
    queue: List[Car]
    # line.p1 начало, line.p2 конец
    line: Line
    line_vector: Point
    auto_add_car: bool

    def __init__(self, direction: bool, auto_add: bool = False):
        """
        :param direction: направление движения полосы относительно участка дороги
        """
        self.direction = direction
        self.line = None
        self.line_vector = None
        self.queue = None
        self.auto_add_car = auto_add
        self.time_passed = 0.0

    def set_road(self, road: RoadPart):
        self.road = road
        self.queue = []
        p1 = road.line.p1
        p2 = road.line.p2
        # equal_x = bool(math.fabs(p1.x - p2.x) < 0.001)
        # equal_y = bool(math.fabs(p1.y - p2.y) < 0.001)
        # if equal_y and equal_x:
        #     raise ValueError('Точки не могут быть одинаковыми')
        # if equal_x:
        if self.direction:
            self.line = road.line
        else:
            self.line = Line(road.line.p2, road.line.p1)
        diff_x = self.line.p2.x - self.line.p1.x
        diff_y = self.line.p2.y - self.line.p1.y
        vector_x = 1.0 if diff_x > 0 else 0 if diff_x == 0.0 else -1
        vector_y = 1.0 if diff_y > 0 else 0 if diff_y == 0.0 else -1
        self.line_vector = Point(vector_x, vector_y)

    def can_recv(self):
        if self.direction:
            return not self.queue or Line(self.queue[-1].position, self.line.p1).distance() > DEFAULT_CAR_LENGTH
        return not self.queue or Line(self.queue[-1].position, self.line.p1).distance() > DEFAULT_CAR_LENGTH

    def simulate(self, timedelta: float):
        for i in range(len(self.queue)):
            car = self.queue[i]
            car.simulate(timedelta=timedelta, queue_position=i)
        if self.auto_add_car:
            self.time_passed += timedelta
            if self.time_passed >= 10.0:
                self.time_passed = 0.0
                if self.can_recv():
                    self.queue.append(
                        Car(
                            position=self.line.p1,
                            drive_line=self,
                        )
                    )


class RoadPart:
    ROAD_COUNT = 0
    line: Line
    forward_road_lines: List[DriveLine]
    backward_road_lines: List[DriveLine]
    length: float
    width: float
    id: int

    def __init__(
            self,
            point_1: Point,
            point_2: Point,
            lines: List[DriveLine] = [],
            auto_create_for_direction=None
    ):
        """
        :param lines: полосы движения назад
        :param length: длина в метрах
        """
        self.forward_road_lines = []
        self.backward_road_lines = []
        self.id = RoadPart.inc_road_count()
        if lines:
            for line in lines:
                if line.direction:
                    self.forward_road_lines.append(line)
                else:
                    self.backward_road_lines.append(line)
        else:
            self.forward_road_lines.append(
                DriveLine(direction=True, auto_add=bool(auto_create_for_direction == True))
            )
            self.backward_road_lines.append(
                DriveLine(direction=False, auto_add=bool(auto_create_for_direction == False))
            )

        self.line = Line(point_1, point_2)
        self.width = (len(self.forward_road_lines) + len(self.backward_road_lines)) * 2.5
        self.length = self.line.distance()

        for line in self.forward_road_lines:
            line.set_road(road=self)
        for line in self.backward_road_lines:
            line.set_road(road=self)

    @classmethod
    def inc_road_count(cls):
        cls.ROAD_COUNT += 1
        return cls.ROAD_COUNT

    def get_direction_lines(self, direction: bool) -> List[DriveLine]:
        if direction:
            return self.forward_road_lines
        return self.backward_road_lines

    def has_lines(self, direction: bool):
        if direction:
            return bool(self.forward_road_lines)
        return bool(self.backward_road_lines)

    def get_first_line(self, direction) -> DriveLine:
        if direction:
            return self.forward_road_lines[0] if self.forward_road_lines else None
        return self.backward_road_lines[0] if self.backward_road_lines else None

    def to_dict(self):
        return {
            'id': self.id,
            'position': {
                'p1': {
                    'x': self.line.p1.x,
                    'y': self.line.p1.y,
                },
                'p2': {
                    'x': self.line.p2.x,
                    'y': self.line.p2.y
                }
            }
        }

    def get_cars(self):
        cars = []
        for drive_line in [self.get_first_line(True), self.get_first_line(False)]:
            if drive_line:
                for car in drive_line.queue:
                    cars.append(car.to_dict())
        return cars
