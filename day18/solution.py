from aocd import get_data # type: ignore
from typing import Tuple, List, Set, Dict, Iterable
from itertools import product

Cube = Tuple[int, int, int]
Coord = Tuple[int, int, int]
BoundingCube = Tuple[Coord, Coord]
Polytope = Set[Cube]
Permutation = Dict[int, int]
Distance = int

def parse_data(data: str) -> Polytope:
    p: Polytope = set()
    for line in data.split('\n'):
        p.add(tuple(int(x) for x in line.split(',')))
    return p

def l1_distance(c1: Cube, c2: Cube) -> Distance:
    return sum(abs(x - y) for x, y in zip(c1, c2))

def is_adjacent(c1: Cube, c2: Cube) -> bool:
    return l1_distance(c1, c2) == 1

def n_adjacent(c: Cube, p: Polytope) -> int:
    return sum(is_adjacent(c, other) for other in p)

def n_faces(p: Polytope) -> int:
    faces = 0
    checked: List[Polytope] = []
    for c in p:
        shared = sum(is_adjacent(c, old) for old in checked)
        faces += 6 - 2*shared
        checked.append(c)
    return faces

def find_bounding_cube(p: Polytope, buffer: int) -> BoundingCube:
    minx, maxx, miny, maxy, minz, maxz = 100, 0, 100, 0, 100, 0
    for cube in p:
        minx, maxx = min(cube[0], minx), max(cube[0], maxx)
        miny, maxy = min(cube[1], miny), max(cube[1], maxy)
        minz, maxz = min(cube[2], minz), max(cube[2], maxz)
    return (
        (minx - buffer, miny - buffer, minz - buffer),
        (maxx + buffer, maxy + buffer, maxz + buffer)
    )

def neighbours(c: Cube) -> Iterable[Cube]:
    yield (c[0] + 1, c[1], c[2])
    yield (c[0] - 1, c[1], c[2])
    yield (c[0], c[1] + 1, c[2])
    yield (c[0], c[1] - 1, c[2])
    yield (c[0], c[1], c[2] + 1)
    yield (c[0], c[1], c[2] - 1)

def inside(c: Cube, b: BoundingCube) -> bool:
    return (
        (b[0][0] < c[0] < b[1][0])
        and (b[0][1] < c[1] < b[1][1])
        and (b[0][2] < c[2] < b[1][2])
    )

def steamify(p: Polytope, b: BoundingCube) -> Polytope:
    steam: Polytope = set()
    initial = (b[0][0] + 1, b[0][1] + 1, b[0][2] + 1)
    queue: Set[Coord] = {initial}
    while queue:
        next = queue.pop()
        queue.update(
            nbr for nbr in neighbours(next)
            if nbr not in (p | steam) and inside(nbr, b)
        )
        steam.add(next)
    return steam


if __name__ == '__main__':
    data = get_data(day=18, year=2022).strip()
    polytope = parse_data(data)

    bc = find_bounding_cube(polytope, buffer=2)
    print(f"Bounding cube to fill with steam: {bc}")

    steam = steamify(polytope, bc)
    steam_bc = find_bounding_cube(steam, buffer=0)
    print(f"Steam's bounding cube: {steam_bc}")
    steam_bc_surface_area = 2*sum(
        (steam_bc[1][i] - steam_bc[0][i] + 1) * (steam_bc[1][j] - steam_bc[0][j] + 1)
        for i, j in ((0, 1), (0, 2), (1, 2))
    )
    print(f"Steam exterior surface area: {steam_bc_surface_area}")
    steam_exposed_faces = n_faces(steam)
    print(f"Steam total exposed faces: {steam_exposed_faces}")

    exterior_exposed_faces = steam_exposed_faces - steam_bc_surface_area
    print(f"The total number of exterior exposed faces is {exterior_exposed_faces}")