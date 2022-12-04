from aocd import get_data # type: ignore
from typing import Tuple, List, Set

Interval = Tuple[int, int]

def str_to_interval(s: str) -> Interval:
    spl = s.split('-')
    return (int(spl[0]), int(spl[1]))

def parse_data(data: str) -> List[Tuple[Interval, Interval]]:
    return [
        (str_to_interval(x), str_to_interval(y))
        for x, y in (line.split(',') for line in data.split('\n'))
    ]

def contains(i0: Interval, i1: Interval) -> bool:
    return (
        ((i0[0] <= i1[0]) and (i0[1] >= i1[1]))
        or
        ((i1[0] <= i0[0]) and (i1[1] >= i0[1]))
    )

def disjoint(i0: Interval, i1: Interval) -> bool:
    return (
        (i0[1] < i1[0]) or (i1[1] < i0[0])
    )


if __name__ == '__main__':
    data = get_data(day=4, year=2022)
    ncontains = sum(contains(*t) for t in parse_data(data))
    print(f"The number of containments is {ncontains}")

    noverlaps = sum(not disjoint(*t) for t in parse_data(data))
    print(f"The number of overlaps is {noverlaps}")