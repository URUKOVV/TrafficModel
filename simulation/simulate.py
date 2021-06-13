from typing import List
from bases import RoadPart, CrossRoad, SimulateMixin


class CityModel(SimulateMixin):
    __roads: List[RoadPart]
    __cross_roads: List[CrossRoad]

    def __init__(self):
        self.__roads = []
        self.__cross_roads = []

    def simulate(self, timedelta: float, **kwargs):
        for j in range(len(self.__roads)):
            road = self.__roads[j]
            for drive_line in [road.get_first_line(True), road.get_first_line(False)]:
                drive_line.simulate(timedelta=timedelta)
        for j in range(len(self.__cross_roads)):
            self.__cross_roads[j].simulate(timedelta=timedelta)

    def to_dict(self):
        cars = []
        semaphores = []
        for road in self.__roads:
            road_semaphores = road.get_semaphores()
            for semaphore in road_semaphores:
                semaphores.append(semaphore)
            road_cars = road.get_cars()
            for car in road_cars:
                cars.append(car)
        for cross_road in self.__cross_roads:
            cross_road_cars = cross_road.get_cars()
            for car in cross_road_cars:
                cars.append(car)
        return {
            'roads': [road.to_dict() for road in self.__roads],
            'cars': cars,
            'semaphores': semaphores,
        }

    def add_road(self, road: RoadPart):
        self.__roads.append(road)

    def add_cross_road(self, cross_road: CrossRoad):
        self.__cross_roads.append(cross_road)
