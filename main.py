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


simulation_model = CityModel()
simulation_model.add_road(RoadPart(point_1=Point(0.0, 0.0), point_2=Point(10.0, 0.0), auto_create_for_direction=True))
simulation_model.add_road(RoadPart(point_1=Point(15, 0.0), point_2=Point(30.0, 0.0), auto_create_for_direction=False))
simulation_model.add_road(
    RoadPart(
        point_1=Point(x=12.5, y=2.5),
        point_2=Point(x=12.5, y=17.5),
        auto_create_for_direction=False,
        rotation_angle=math.pi/2
    )
)

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
