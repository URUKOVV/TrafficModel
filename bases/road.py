from __future__ import annotations

import math
from typing import List
from .car import Car, DEFAULT_CAR_LENGTH
from .primitives import Point, Line


DEFAULT_TIME_SWITCH = 30.0


class Semaphore:
    GREEN = 1
    RED = 2

    state: int  # GREEN, RED
    position: Point
    time_passed: float

    def __init__(self, position: Point):
        self.state = self.RED
        self.time_passed = 0.0
        self.position = position

    def switch(self):
        if self.state == self.GREEN:
            self.state = self.RED
        else:
            self.state = self.GREEN

    def simulate(self, timedelta: float):
        self.time_passed += timedelta
        if self.time_passed >= DEFAULT_TIME_SWITCH:
            self.time_passed = 0.0
            self.switch()


class CrossRoad:
    X_TYPE = 1  # Х-образный перекресток
    T_TYPE = 2  # Т-образный перекресток
    type: int
    roads: List[RoadPart]
    lines: List[DriveLine]  # полосы движения перекрестка
    incoming_lines: List[DriveLine]  # входящие полосы движения
    outcoming_lines: List[DriveLine]  # исходящие полосы движения
    position: Point

    def __init__(self, roads: List[RoadPart], position: Point):
        count = len(roads)
        if count < 3:
            raise ValueError('Required at least 3 roads')
        elif count == 3:
            self.type = self.T_TYPE
        elif count == 4:
            self.type = self.X_TYPE
        elif count > 4:
            raise ValueError('Max roads is 4')

        self.position = position
        self.roads = roads

        self.incoming_lines = []
        self.outcoming_lines = []
        self.lines = []

        for i in range(len(self.roads)):
            road = self.roads[i]
            road_lines = [road.get_first_line(True), road.get_first_line(False)]
            for j in range(len(road_lines)):
                road_line = road_lines[j]
                distance_to_end_of_line = math.dist(
                    (self.position.x, self.position.y), (road_line.line.p2.x, road_line.line.p2.y)
                )
                distance_to_start_of_line = math.dist(
                    (self.position.x, self.position.y), (road_line.line.p1.x, road_line.line.p1.y)
                )
                # входящая полоса движения
                if distance_to_end_of_line < distance_to_start_of_line:
                    self.incoming_lines.append(road_line)
                # исходящая полоса движения
                elif distance_to_end_of_line > distance_to_start_of_line:
                    self.outcoming_lines.append(road_line)

        for i in range(len(self.incoming_lines)):
            incoming_line = self.incoming_lines[i]
            # нужно получить список возможных путей
            for j in range(len(self.outcoming_lines)):
                outcoming_line = self.outcoming_lines[j]
                if outcoming_line.road.id == incoming_line.road.id:
                    continue
                cross_line = DriveLine(
                    direction=False,
                    line=Line(incoming_line.line.p2, outcoming_line.line.p1)
                )
                cross_line.add_path(outcoming_line)
                incoming_line.add_path(cross_line)
                self.lines.append(cross_line)

    def simulate(self, timedelta: float):
        for i in range(len(self.lines)):
            self.lines[i].simulate(timedelta=timedelta)


class DriveLine:
    direction: bool
    road: RoadPart
    queue: List[Car]
    # line.p1 начало, line.p2 конец
    line: Line
    line_vector: Point
    auto_add_car: bool
    semaphore: Semaphore
    paths: List[DriveLine]

    def __init__(self, direction: bool, auto_add: bool = False, line: Line = None):
        """
        :param direction: направление движения полосы относительно участка дороги
        """
        self.direction = direction
        self.line = line
        self.line_vector = self.get_line_vector()
        self.queue = []
        self.auto_add_car = auto_add
        self.time_passed = 0.0
        self.paths = []
        self.semaphore = None

    def set_road(self, road: RoadPart):
        self.road = road
        self.queue = []
        # p1 = road.line.p1
        # p2 = road.line.p2
        # equal_x = bool(math.fabs(p1.x - p2.x) < 0.001)
        # equal_y = bool(math.fabs(p1.y - p2.y) < 0.001)
        # if equal_y and equal_x:
        #     raise ValueError('Точки не могут быть одинаковыми')
        # if equal_x:
        if self.direction:
            self.line = Line(road.line.p1, road.line.p2)
            self.semaphore = Semaphore(position=road.line.p2)
        else:
            self.line = Line(road.line.p2, road.line.p1)
            self.semaphore = Semaphore(position=road.line.p1)
        self.line_vector = self.get_line_vector()

        # перенос полосы от центра дороги
        angle = math.pi / 2
        x = 1.5 * (self.line_vector.x * math.cos(angle) - self.line_vector.y * math.sin(angle))
        y = 1.5 * (self.line_vector.y * math.cos(angle) + self.line_vector.x * math.sin(angle))
        self.line = Line(Point(self.line.p1.x + x, self.line.p1.y + y), Point(self.line.p2.x + x, self.line.p2.y + y))

    def get_line_vector(self):
        if self.line:
            diff_x = self.line.p2.x - self.line.p1.x
            diff_y = self.line.p2.y - self.line.p1.y
            vector_x = 1.0 if diff_x > 0 else 0 if diff_x == 0.0 else -1
            vector_y = 1.0 if diff_y > 0 else 0 if diff_y == 0.0 else -1
            return Point(vector_x, vector_y)
        return None

    def can_recv(self):
        if self.direction:
            return not self.queue or Line(self.queue[-1].position, self.line.p1).distance() > DEFAULT_CAR_LENGTH
        return not self.queue or Line(self.queue[-1].position, self.line.p1).distance() > DEFAULT_CAR_LENGTH

    def can_release(self):
        return not bool(self.semaphore) or self.semaphore.state == self.semaphore.GREEN

    def release_car(self):
        return self.queue.pop(0)

    def simulate(self, timedelta: float):
        if self.semaphore:
            self.semaphore.simulate(timedelta=timedelta)
        for i in range(len(self.queue)):
            if i + 1 <= len(self.queue):
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

    def add_car(self, car: Car):
        if self.can_recv():
            self.queue.append(car)
        else:
            raise ValueError('Check before add!!!')

    def add_path(self, drive_line: DriveLine):
        self.paths.append(drive_line)

    def is_intersect(self, line2: DriveLine):
        xdiff = (self.line.p1.x - self.line.p2.x, line2.line.p1.x - line2.line.p2.x)
        ydiff = (self.line.p1.y - self.line.p2.y, line2.line.p1.y - line2.line.p2.y)

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return False
        return True
        # d = (
        #     det((self.line.p1.x, self.line.p1.y), (self.line.p2.x, self.line.p2.y)),
        #     det((line2.line.p1.x, line2.line.p1.y), (self.line.p2.x, self.line.p2.y))
        # )
        # x = det(d, xdiff) / div
        # y = det(d, ydiff) / div
        # return Point(x, y)


class RoadPart:
    ROAD_COUNT = 0
    line: Line
    forward_road_lines: List[DriveLine]
    backward_road_lines: List[DriveLine]
    length: float
    width: float
    id: int
    rotation_angle: float

    def __init__(
            self,
            point_1: Point,
            point_2: Point,
            lines: List[DriveLine] = [],
            auto_create_for_direction=None,
            rotation_angle=None
    ):
        """
        :param lines: полосы движения назад
        :param length: длина в метрах
        """
        self.forward_road_lines = []
        self.backward_road_lines = []
        self.rotation_angle = rotation_angle
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
                },
                'angle': self.rotation_angle
            }
        }

    def get_cars(self):
        cars = []
        for drive_line in [self.get_first_line(True), self.get_first_line(False)]:
            if drive_line:
                for car in drive_line.queue:
                    cars.append(car.to_dict())
        return cars
