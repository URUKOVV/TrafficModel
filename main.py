import json
import math
import time

import redis

from bases import settings
from bases.road import DriveLine, RoadPart, CrossRoad
from bases.car import Car
from bases.primitives import Point, Line
from time import sleep

roads = [
    RoadPart(Point(0.0, 0.0), Point(10.0, 0.0))
]

# for road in roads:
#     for drive_line in [road.get_first_line(True), road.get_first_line(False)]:
#         if drive_line.can_recv():
#             drive_line.queue.append(
#                 Car(
#                     position=drive_line.line.p1,
#                     drive_line=drive_line
#                 )
#             )


redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
for road in roads:
    while True:
        time_start = time.perf_counter_ns()
        for drive_line in [road.get_first_line(True), road.get_first_line(False)]:
            if drive_line.can_recv():
                drive_line.queue.append(
                    Car(
                        position=drive_line.line.p1,
                        drive_line=drive_line,
                    )
                )
            for i in range(len(drive_line.queue)):
                car = drive_line.queue[i]
                moved = car.simulate(timedelta=0.1, queue_position=i)
        cars = [car.to_dict() for car in road.get_first_line(True).queue]
        data = json.dumps(cars)
        redis_instance.set(
            'cars',
            data
        )
        print(len(cars))
        sleep_time = 0.167 - time.perf_counter_ns() - time_start * 1e-9
        if sleep_time > 0.0:
            sleep(sleep_time)
            # симуляция 60 раз в секунду


        # data = [
        #     {
        #         'lines': [
        #             {
        #                 'line': {
        #                     'p1': (line.line.p1.x, line.line.p1.y),
        #                     'p2': (line.line.p2.x, line.line.p2.y),
        #                 },
        #                 'queue': [{'x': car.position.x, 'y': car.position.y} for car in line.queue],
        #             } for line in [road.get_first_line(True), road.get_direction_lines(False)]
        #         ]
        #     } for road in roads
        # ]
        # redis_instance.set('roads', json.dumps(data))
