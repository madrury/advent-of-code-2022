import re
from itertools import chain
from aocd import get_data # type: ignore
from dataclasses import dataclass
from typing import Union, List, Set, Tuple, Optional

Coord = Tuple[int, int]
Interval = Tuple[int, int]

PATTERN = r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)"


def l1_distance(xs: Coord, ys: Coord) -> int:
    return abs(ys[0] - xs[0]) + abs(ys[1] - xs[1])


@dataclass
class SensorInformation:
    sensor: Coord
    beacon: Coord

    @property
    def l1_distance(self) -> int:
        return l1_distance(self.sensor, self.beacon)


def parse_data(data: str) -> List[SensorInformation]:
    sensors: List[SensorInformation] = []
    for line in data.split('\n'):
        matches = tuple(
            int(match) for match in
            re.search(PATTERN, line).groups()
        )
        sensors.append(
            SensorInformation(matches[:2], matches[2:])
        )
    return sensors


def interval_at_level(sensor: SensorInformation, ylevel: int) -> Optional[Interval]:
    dx = sensor.l1_distance - abs(ylevel - sensor.sensor[1])
    left, right = (
        sensor.sensor[0] - dx, sensor.sensor[0] + dx
    )
    if right < left:
        return None
    return (left, right)


def overlaps(i1: Interval, i2: Interval) -> bool:
    return max(i1[0], i2[0]) <= min(i1[1], i2[1]) + 1


def union(i1: Interval, i2: Interval) -> Interval:
    return (
        min(i1[0], i2[0]), max(i1[1], i2[1])
    )

def reduce(intervals: List[Interval]) -> List[Interval]:
    reduced: List[Interval] = []

    for interval in intervals:
        overlapping = []
        for test_interval in reduced:
            if overlaps(interval, test_interval):
                overlapping.append(test_interval)

        reduced = [i for i in reduced if i not in overlapping]
        match overlapping:
            case []:
                reduced.append(interval)
            case [*ints]:
                for i in ints:
                    interval = union(interval, i)
                reduced.append(interval)

    return reduced


def intersect(intervals: List[Interval], interval: Interval) -> List[Interval]:
    return [
        (max(i[0], interval[0]), min(i[1], interval[1]))
        for i in intervals if overlaps(i, interval)
    ]


def count_objects_in_interval_at_level(
    sensors: List[SensorInformation],
    interval: Interval,
    ylevel: int
) -> int:
    sensors_at_level = {
        sensor.sensor for sensor in sensors
        if (
            sensor.sensor[1] == ylevel
            and (interval[0] <= sensor.sensor[0] <= interval[1])
        )
    }
    beacons_at_level = {
        sensor.beacon for sensor in sensors
        if (
            sensor.beacon[1] == ylevel
            and (interval[0] <= sensor.beacon[0] <= interval[1])
        )
    }
    return len(sensors_at_level | beacons_at_level)


if __name__ == '__main__':
    YLEVEL = 2_000_000
    MAXXY = 4_000_000

    data = get_data(day=15, year=2022)
    sensors = parse_data(data)

    intervals = [interval_at_level(sensor, ylevel=YLEVEL) for sensor in sensors]
    intervals = reduce([i for i in intervals if i is not None])
    print(intervals)
    total_length = sum(
        i[1] - i[0] + 1 for i in intervals
    )
    n_objects_in_intervals = sum(
        count_objects_in_interval_at_level(sensors, interval, ylevel=YLEVEL)
        for interval in intervals
    )
    print(f"The empty intervals are: {intervals}")
    print(f"The total length of those intervals are: {total_length}")
    print(f"The number of objects in those intervals is: {n_objects_in_intervals}")
    print(f"The total empty space is: {total_length - n_objects_in_intervals}")


    for ylevel in range(0, MAXXY + 1):
        if ylevel % 100_000 == 0:
             print('.', end='', flush=True)
        intervals = [interval_at_level(sensor, ylevel=ylevel) for sensor in sensors]
        intervals = reduce([i for i in intervals if i is not None])
        intervals = intersect(intervals, (0, MAXXY))
        total_length = sum(
            i[1] - i[0] + 1 for i in intervals
        )
        # Should be exactly one hit!
        if total_length != MAXXY + 1:
            print(str(ylevel) + ': ' + str(intervals) + '\n')