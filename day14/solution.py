from aocd import get_data # type: ignore
from enum import Enum
from typing import Union, List, Set, Tuple, Optional

Coord = Tuple[int, int]
Cave = Set[Coord]


def parse_data(data: str) -> Cave:
    cave: Set[Coord] = set()
    for line in data.split('\n'):
        cave.update(parse_line(line))
    return cave

def parse_line(line: str) -> Set[Coord]:
    coord_pairs: List[Coord] = []
    for token in line.split(' -> '):
        x, y = token.split(',')
        coord_pairs.append((int(x), int(y)))

    newcoords: set[Coord] = set()
    prevx, prevy = coord_pairs[0]
    for x, y in coord_pairs[1:]:
        if x == prevx and y > prevy:
            newcoords.update((x, ny) for ny in range(prevy, y + 1))
        if x == prevx and y < prevy:
            newcoords.update((x, ny) for ny in range(y, prevy + 1))
        if y == prevy and x > prevx:
            newcoords.update((nx, y) for nx in range(prevx, x + 1))
        if y == prevy and x < prevx:
            newcoords.update((nx, y) for nx in range(x, prevx + 1))
        prevx, prevy = x, y
    return newcoords


def trickle_no_floor(cave: Cave, pos: Coord, maxy: int) -> Optional[Coord]:
    assert pos not in cave
    prevpos = None
    while True and pos[1] < maxy:
        prevpos = pos
        if (pos[0], pos[1] + 1) not in cave:
            pos = (pos[0], pos[1] + 1)
        elif (pos[0] - 1, pos[1] + 1) not in cave:
            pos = (pos[0] - 1, pos[1] + 1)
        elif (pos[0] + 1, pos[1] + 1) not in cave:
            pos = (pos[0] + 1, pos[1] + 1)
        else:
            break
    if pos[1] >= maxy:
        return None
    else:
        return prevpos

def trickle_with_floor(cave: Cave, pos: Coord, maxy: int) -> Optional[Coord]:
    assert pos not in cave
    prevpos = None
    while True:
        prevpos = pos
        # Check if we're on the floor of the cave.
        if pos[1] == maxy + 1:
            break
        # Drop the sand.
        elif (pos[0], pos[1] + 1) not in cave:
            pos = (pos[0], pos[1] + 1)
        elif (pos[0] - 1, pos[1] + 1) not in cave:
            pos = (pos[0] - 1, pos[1] + 1)
        elif (pos[0] + 1, pos[1] + 1) not in cave:
            pos = (pos[0] + 1, pos[1] + 1)
        # We're otherwise stuck.
        else:
            break
    return prevpos

def fill(cave: Cave, pos: Coord, maxy: int, floor: bool = False):
    tricklef = [trickle_no_floor, trickle_with_floor][floor]
    while True:
        finalpos = tricklef(cave, pos, maxy)
        if finalpos == pos:
            cave.add(finalpos)
            return
        elif finalpos:
            cave.add(finalpos)
        else:
            return


if __name__ == '__main__':
    data = get_data(day=14, year=2022)

    cave = parse_data(data)
    n_rocks = len(cave)
    maxrock = max(y for (_, y) in cave)
    fill(cave, (500, 0), maxrock)
    n_sand = len(cave) - n_rocks
    print(f"{n_sand} grains of sand have accumulated before voiding.")

    cave = parse_data(data)
    n_rocks = len(cave)
    maxrock = max(y for (_, y) in cave)
    fill(cave, (500, 0), maxrock, floor=True)
    n_sand = len(cave) - n_rocks
    print(f"{n_sand} grains of sand have accumulated before filling up.")