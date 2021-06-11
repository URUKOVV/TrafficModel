import json
import math
import time

import redis

from bases import settings
from bases.road import DriveLine, RoadPart, CrossRoad
from bases.car import Car
from bases.primitives import Point, Line
from time import sleep
from simulation import CityModel

roads = [
    RoadPart(point_1=Point(0.0, 0.0), point_2=Point(10.0, 0.0), auto_create_for_direction=True),
    RoadPart(point_1=Point(15, 0.0), point_2=Point(30.0, 0.0), auto_create_for_direction=False),
    RoadPart(
        point_1=Point(x=12.5, y=2.5),
        point_2=Point(x=12.5, y=17.5),
        auto_create_for_direction=False,
        rotation_angle=math.pi/2
    )
]

cross_roads = [
    CrossRoad(position=Point(12.5, y=0.0), roads=[roads[0], roads[1], roads[2]])
]

simulation_model = CityModel()
simulation_model.add_road(roads[0])
simulation_model.add_road(roads[1])
simulation_model.add_road(roads[2])
simulation_model.add_cross_road(cross_roads[0])

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
