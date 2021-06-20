import math
import random

from .primitives import SimulateMixin, Point

DEFAULT_CAR_LENGTH = 1
DEFAULT_CAR_SPEED = 1.5
DEFAULT_CAR_ACCELERATION_SPEED = 1.0
DEFAULT_CAR_DELAY = 0.25


class Car(SimulateMixin):
    CAR_COUNT = 0
    STATE_STOPPED = 1
    STATE_RUNNING = 2
    average_wait_time: float
    position: Point
    length = DEFAULT_CAR_LENGTH  # стандартная длина авто
    id: int

    def __init__(self, position: Point, drive_line=None):
        self.average_wait_time = 0.0
        self.position = position
        self.drive_line = drive_line
        self.next_drive_line = None
        self.id = Car.inc_car_count()
        self.speed = 0.0
        self.state = self.STATE_STOPPED
        self.delay_passed = 0.0

    @classmethod
    def inc_car_count(cls):
        cls.CAR_COUNT += 1
        return cls.CAR_COUNT

    def simulate(self, timedelta: float, queue_position: int = None, drive_line=None):
        moved = False
        next_car = None
        if not self.drive_line:
            assert drive_line
            self.drive_line = drive_line
        if queue_position == 0:
            drive_line_distance = self.drive_line.line.distance()
        else:
            next_car = self.drive_line.queue[queue_position - 1]
            drive_line_distance = math.dist(
                (self.drive_line.line.p1.x, self.drive_line.line.p1.y),
                (next_car.position.x, next_car.position.y)
            )
            if next_car.state == Car.STATE_STOPPED and math.dist(
                    (self.position.x, self.position.y), (next_car.position.x, next_car.position.y)
            ) == DEFAULT_CAR_LENGTH + 0.5:
                return moved
        if self.state == self.STATE_STOPPED:
            self.delay_passed += timedelta
            if self.delay_passed >= DEFAULT_CAR_DELAY:
                self.delay_passed = 0.0
                self.state = self.STATE_RUNNING
            else:
                return moved

        line_start_point = self.drive_line.line.p1
        distance_p1 = math.dist(
            (self.position.x, self.position.y), (line_start_point.x, line_start_point.y)
        )
        try:
            # проверка на то, что авто находится внутри полосы движения (между точки p1 и p2)
            assert distance_p1 < drive_line_distance
            new_position = Point(
                self.position.x + self.drive_line.line_vector.x * timedelta * self.speed,
                self.position.y + self.drive_line.line_vector.y * timedelta * self.speed
            )
            distance_new_pos = math.dist(
                (new_position.x, new_position.y), (line_start_point.x, line_start_point.y)
            )
            # новая точка все еще находится внутри полосы
            if queue_position == 0 and distance_new_pos >= drive_line_distance:
                if self.drive_line.can_release():
                    if len(self.drive_line.paths) == 0:
                        self.drive_line.release_car()
                    else:
                        if not self.next_drive_line:
                            self.next_drive_line = self.drive_line.paths[
                                random.randint(0, len(self.drive_line.paths) - 1)
                            ]
                        if self.next_drive_line.can_recv():
                            self.drive_line.release_car()
                            self.drive_line = self.next_drive_line
                            self.next_drive_line = None
                            self.drive_line.add_car(self)
                            self.position = self.drive_line.line.p1
                            moved = True
                            return moved
            else:
                assert distance_new_pos < drive_line_distance
            # между машинами соблюдается дистанция
            assert distance_new_pos < drive_line_distance - int(bool(next_car)) * (DEFAULT_CAR_LENGTH + 0.5)
            self.position = new_position
            moved = True
        except AssertionError:
            self.state = self.STATE_STOPPED
            self.speed = 0.0
            return moved
        if self.speed < DEFAULT_CAR_SPEED:
            self.speed += timedelta * DEFAULT_CAR_ACCELERATION_SPEED
            if self.speed > DEFAULT_CAR_SPEED:
                self.speed = DEFAULT_CAR_SPEED
        return moved

    def to_dict(self):
        return {
            'id': self.id,
            'position': {
                'x': self.position.x,
                'y': self.position.y,
            }
        }

