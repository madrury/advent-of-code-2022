
from aocd import get_data  # type: ignore
from typing import List, Tuple, Dict
from itertools import product
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

DIRECTIION_MAPPING = {
    '^': Direction.NORTH,
    'v': Direction.SOUTH,
    '>': Direction.EAST,
    '<': Direction.WEST
}

class Tile(Enum):
    BLOCKED = 0
    OPEN = 1

Coord = Tuple[int, int]
Frame = List[List[Tile]]
FrameNum = int
Position = Tuple[FrameNum, Coord]
Distance = int


class Blizzard:

    def __init__(self, coords: Coord, direction: Direction):
        self.coords = coords
        self.direction = direction

    def update(self):
        coords = self.coords
        match self.direction:
            case Direction.NORTH:
                self.coords = (coords[0] - 1, coords[1])
            case Direction.SOUTH:
                self.coords = (coords[0] + 1, coords[1])
            case Direction.EAST:
                self.coords = (coords[0], coords[1] + 1)
            case Direction.WEST:
                self.coords = (coords[0], coords[1] - 1)


def parse_data(data: str) -> List[Blizzard]:
    blizzards: List[Blizzard] = []
    for row, line in enumerate(data.split('\n')):
        for col, char in enumerate(line):
            if char not in DIRECTIION_MAPPING:
                continue
            blizzards.append(
                Blizzard((row - 1, col - 1), DIRECTIION_MAPPING[char])
            )
    return blizzards

def to_frame(blizzards: List[Blizzard], nrow: int, ncol: int) -> Frame:
    frame = [
        [Tile.OPEN for _ in range(ncol)]
        for _ in range(nrow)
    ]
    for blizz in blizzards:
        frame[blizz.coords[0] % nrow][blizz.coords[1] % ncol] = Tile.BLOCKED
    return frame

def print_frame(frame):
    CHARMAPPING = {Tile.OPEN: '.', Tile.BLOCKED: '#'}
    for row in frame:
        print(''.join(CHARMAPPING[tile] for tile in row))
    print()


@dataclass
class PathReturnValue:
    visited: Dict[Position, Distance]
    blizzards: List[Blizzard]


def path(
    blizzards: List[Blizzard],
    nrow: int,
    ncol: int,
    start: Coord,
    end: Coord
) -> PathReturnValue:
    unvisited: Dict[Position, Distance] = {(0, start): 0}
    visited: Dict[Position, Distance] = {}

    firstframe = to_frame(blizzards, nrow, ncol)
    map: Dict[FrameNum, Frame] = {0: firstframe}
    # print(f"Frame 0:")
    # print_frame(firstframe)

    while unvisited:
        frame, coord = min(unvisited, key=unvisited.get)
        distfromstart = unvisited[frame, coord]
        visited[frame, coord] = distfromstart
        del unvisited[frame, coord]

        # If this is the first time we've visited this frame, generate the next
        # one.
        if frame + 1 not in map:
            for blizz in blizzards:
                blizz.update()
            map[frame + 1] = to_frame(blizzards, nrow, ncol)
            # print(f"Frame {frame + 1}:")
            # print_frame(map[frame + 1])

        # Look into the next frame for the accesable positions and add them to
        # the unvisited queue.
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            newcoord = (coord[0] + dx, coord[1] + dy)
            # Can always wait at the starting position.
            if newcoord == start:
                unvisited[frame + 1, newcoord] = distfromstart + 1
            # We found the end!
            if newcoord == end:
                print("End found!")
                visited[frame + 1, newcoord] = distfromstart + 1
                return PathReturnValue(visited, blizzards)
            withinbounds = (0 <= newcoord[0] < nrow) and (0 <= newcoord[1] < ncol)
            if withinbounds and map[frame + 1][newcoord[0]][newcoord[1]] == Tile.OPEN:
                unvisited[frame + 1, newcoord] = min(
                    distfromstart + 1,
                    unvisited.get((frame + 1, newcoord), 10**5)
                )

    return PathReturnValue(visited, blizzards)


def thereandthenbackandthenthereagain(
    blizzards: List[Blizzard],
    nrow: int,
    ncol: int,
    start: Coord,
    end: Coord
) -> int:
    there = path(blizzards, nrow, ncol, start, end)
    n_there = max(there.visited.values())

    back = path(there.blizzards, nrow, ncol, end, start)
    n_back = max(back.visited.values())

    thereagain = path(back.blizzards, nrow, ncol, start, end)
    n_thereagain = max(thereagain.visited.values())

    return n_there + n_back + n_thereagain







if __name__ == "__main__":
    data = get_data(day=24, year=2022)


    NROW, NCOL = 35, 100

    blizzards = parse_data(data)
    r = path(blizzards, NROW, NCOL, (-1, 0), (NROW, NCOL - 1))
    print(f"The number of moves to the end is {max(r.visited.values())}")

    blizzards = parse_data(data)
    n_round_trip = thereandthenbackandthenthereagain(
        blizzards, NROW, NCOL, (-1, 0), (NROW, NCOL - 1)
    )
    print(f"The number of moves to round trip is {n_round_trip}")