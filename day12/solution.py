from aocd import get_data # type: ignore
import string
from itertools import product
from typing import Tuple, Dict, Set, List, Optional

Coord = Tuple[int, int]
Elevation = int
Map = Dict[Coord, Elevation]
Distance = int

N_ROW, N_COL = 41, 162
MAX_DISTANCE: Distance = 666_666

LOWEST, HIGHEST = 1, 26
ELEVATIONS = {
    **{'S': LOWEST, 'E': HIGHEST},
    **{chr: n + 1 for chr, n in zip(string.ascii_lowercase, range(26))}
}


def parse_data(data: str) -> Tuple[Coord, Coord, Map]:
    relief = [
        [chr for chr in line.strip()]
        for line in data.split('\n')
    ]
    start = next(
        (x, y) for x, y in product(range(N_ROW), range(N_COL))
        if relief[x][y] == 'S'
    )
    end = next(
        (x, y) for x, y in product(range(N_ROW), range(N_COL))
        if relief[x][y] == 'E'
    )
    N, M = len(relief), len(relief[0])
    map = {
        (x, y): ELEVATIONS[relief[x][y]]
        for (x, y) in product(range(N), range(M))
    }
    return start, end, map

def neighbour_mapping(map: Map, backwards: bool=False) -> Dict[Coord, List[Coord]]:
    neighbours = {
        coord: [] for coord in map.keys()
    }
    for (x, y), elev in map.items():
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if dx == 0 and dy == 0:
                continue
            if x + dx < 0 or y + dy < 0 or x + dx > N_ROW - 1 or y + dy > N_COL - 1:
                continue
            destelev = map[(x + dx, y + dy)]
            if backwards and elev - destelev <= 1:
                neighbours[(x, y)].append((x + dx, y + dy))
            elif not backwards and destelev - elev <= 1:
                neighbours[(x, y)].append((x + dx, y + dy))
    return neighbours


class DijkstraWalker:

    def __init__(self,start: Coord, end: Coord, map: Map, backwards: bool = False):
        self.start = start
        self.end = end
        self.backwards = backwards
        self.map = map
        self.neighbours = neighbour_mapping(map, backwards)
        self.visited: Dict[Coord, Distance] = {}
        self.unvisited: Dict[Coord, Distance] = {
            coord: MAX_DISTANCE for coord in map.keys()
        }

    def walk(self):
        if self.backwards:
            self.unvisited[self.end] = 0
        else:
            self.unvisited[self.start] = 0
        while self.unvisited:
            mindist = min(self.unvisited.values())
            current = next(
                coord for coord, dist in self.unvisited.items()
                if dist == mindist
            )
            for nbr in self.neighbours[current]:
                if nbr in self.unvisited:
                    self.unvisited[nbr] = min(self.unvisited[nbr], mindist + 1)
            self.visited[current] = mindist
            del self.unvisited[current]


if __name__ == '__main__':
    data = get_data(day=12, year=2022)

    start, end, map = parse_data(data)
    walker = DijkstraWalker(start, end, map)
    walker.walk()
    print(f"The number of steps from start to end is: {walker.visited[walker.end]}")

    walker = DijkstraWalker(start, end, map, backwards=True)
    walker.walk()

    elevation_zero = {coord for coord, elev in map.items() if elev == 1}
    distances = {coord: walker.visited[coord] for coord in elevation_zero}
    print(f"The minimum of steps from low elevation to end is: {min(distances.values())}")