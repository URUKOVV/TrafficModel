import json
import math
import time

import redis

from bases import settings
from bases.road import DriveLine, RoadPart, CrossRoad
from bases.car import Car
from utils import gen_lines_around
from bases.primitives import Point, Line
from time import sleep
from simulation import CityModel

roads = [
    RoadPart(point_1=Point(2.5, 0.0), point_2=Point(17.5, 0.0), auto_create_for_direction=False),
    RoadPart(point_1=Point(-2.5, 0.0), point_2=Point(-17.5, 0.0), auto_create_for_direction=False),
    RoadPart(
        point_1=Point(x=0.0, y=-2.5),
        point_2=Point(x=0.0, y=-17.5),
        rotation_angle=math.pi/2,
    ),
    RoadPart(
        point_1=Point(x=0.0, y=2.5),
        point_2=Point(x=0.0, y=17.5),
        rotation_angle=-math.pi/2,
    ),
]

line1, line2, line3, line4 = gen_lines_around(Point(0.0, 20.0))
roads.append(RoadPart(point_1=line1.p1, point_2=line1.p2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line2.p1, point_2=line2.p2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line4.p1, point_2=line4.p2, auto_create_for_direction=False, rotation_angle=math.pi/2))

line1, line2, line3, line4 = gen_lines_around(Point(0.0, -20.0))

roads.append(RoadPart(point_1=line1.p1, point_2=line1.p2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line2.p1, point_2=line2.p2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line3.p1, point_2=line3.p2, auto_create_for_direction=False, rotation_angle=math.pi/2))

line1, line2, line3, line4 = gen_lines_around(Point(20.0, 0.0))

roads.append(RoadPart(point_1=line1.p1, point_2=line1.p2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line3.p1, point_2=line3.p2, rotation_angle=math.pi/2, auto_create_for_direction=False))
roads.append(RoadPart(point_1=line4.p1, point_2=line4.p2, rotation_angle=math.pi/2, auto_create_for_direction=False))

cross_roads = [
    CrossRoad(position=Point(0.0, 0.0), roads=[roads[0], roads[1], roads[2], roads[3]]),
    CrossRoad(position=Point(0.0, 20.0), roads=[roads[3], roads[4], roads[5], roads[6]]),
    CrossRoad(position=Point(0.0, -20.0), roads=[roads[2], roads[7], roads[8], roads[9]]),
    CrossRoad(position=Point(20.0, 0.0), roads=[roads[0], roads[10], roads[11], roads[12]]),
]

simulation_model = CityModel()
for i in range(len(roads)):
    simulation_model.add_road(roads[i])

for i in range(len(cross_roads)):
    simulation_model.add_cross_road(cross_roads[i])

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
redis_instance.delete('cars')

current_time = 0.0
prev_time = 0.0

while True:
    current_time = time.perf_counter_ns() * 1e-9
    simulation_model.simulate(timedelta=current_time - prev_time)
    prev_time = current_time
    simulation_model_dict = simulation_model.to_dict()

    redis_instance.set(
        'traffic_model_data',
        json.dumps(simulation_model_dict)
    )
    sleep_time = 0.167 - time.perf_counter_ns() - current_time
    if sleep_time > 0.0:
        sleep(sleep_time)
        # симуляция 60 раз в секунду
