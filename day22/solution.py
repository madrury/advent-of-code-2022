from aocd import get_data  # type: ignore
from typing import List, Tuple, Dict
from itertools import product
from dataclasses import dataclass
from enum import Enum


class Terrain(Enum):
    OPEN = 0
    BLOCKED = 1


class Side(Enum):
    RIGHT = 0
    TOP = 1
    LEFT = 2
    BOTTOM = 3


class Glueing(Enum):
    MATCHING = 0
    REVERSED = 1


class Facing(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


SquareId = int
Coord = Tuple[int, int]
LocalCoord = Tuple[int, int]


@dataclass
class Square:
    id: SquareId
    coord: Coord
    slen: int
    map: List[List[Terrain]]


NClockwiseRotations = int
GlueingPattern = Dict[
    Tuple[SquareId, Side], Tuple[SquareId, Side, Glueing, NClockwiseRotations]
]


def symmetrize(d: GlueingPattern) -> GlueingPattern:
    r = {}
    for k, v in d.items():
        r[k] = v
        r[(v[0], v[1])] = (k[0], k[1], v[2], (4 - v[3]) % 4)
    return r


class Rotation(Enum):
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1


# Lookup tables for translating rotations into new directions.
CLOCKWISE_ROTATIONS = {
    Facing.RIGHT: Facing.DOWN,
    Facing.DOWN: Facing.LEFT,
    Facing.LEFT: Facing.UP,
    Facing.UP: Facing.RIGHT,
}
COUNTERCLOCKWISE_ROTATIONS = {
    Facing.RIGHT: Facing.UP,
    Facing.UP: Facing.LEFT,
    Facing.LEFT: Facing.DOWN,
    Facing.DOWN: Facing.RIGHT,
}


@dataclass
class Position:
    sqid: SquareId
    coord: LocalCoord


@dataclass
class Player:
    position: Position
    facing: Facing


class World:
    """The game world. Represented as a bunch of squares glued together at their
    boundaries.
    """

    def __init__(
        self, squares: Dict[SquareId, Square], pattern: GlueingPattern, player: Player
    ):
        self.squares = squares
        self.pattern = pattern
        self.player = player

    def execute(self, instructions: List["Instruction"], show=False):
        for instruction in instructions:
            match instruction:
                case Instruction.CLOCKWISE:
                    self.rotate(Rotation.CLOCKWISE)
                case Instruction.COUNTERCLOCKWISE:
                    self.rotate(Rotation.COUNTERCLOCKWISE)
                case Instruction.MOVE, n:
                    for _ in range(n):
                        self.move()
            if show:
                print(instruction)
                print(self.player.position)
                self.show()
                print()
                input()

    def password(self) -> int:
        globalrow = (
            self.squares[self.player.position.sqid].coord[1]
            + self.player.position.coord[0]
        )
        globalcol = (
            self.squares[self.player.position.sqid].coord[0]
            + self.player.position.coord[1]
        )
        facing = {Facing.RIGHT: 0, Facing.DOWN: 1, Facing.LEFT: 2, Facing.UP: 3}[
            self.player.facing
        ]
        return 1000 * (globalrow + 1) + 4 * (globalcol + 1) + facing

    def show(self):
        TOKENS = {Terrain.OPEN: ".", Terrain.BLOCKED: "#"}
        thissquare = [
            [TOKENS[terrain] for terrain in row]
            for row in self.squares[self.player.position.sqid].map
        ]
        ppos = self.player.position.coord
        playertoken = {
            Facing.UP: "^",
            Facing.RIGHT: ">",
            Facing.LEFT: "<",
            Facing.DOWN: "v",
        }[self.player.facing]
        thissquare[ppos[0]][ppos[1]] = playertoken
        for row in thissquare:
            print("".join(row))

    def rotate(self, rotation: Rotation):
        self.player.facing = self._rotate(rotation)

    def _rotate(self, rotation: Rotation, ntimes: int = 1) -> Facing:
        match rotation:
            case Rotation.CLOCKWISE:
                lookup = CLOCKWISE_ROTATIONS
                # return CLOCKWISE_ROTATIONS[self.player.facing]
            case Rotation.COUNTERCLOCKWISE:
                lookup = COUNTERCLOCKWISE_ROTATIONS
                # return COUNTERCLOCKWISE_ROTATIONS[self.player.facing]
        result = self.player.facing
        for _ in range(ntimes):
            result = lookup[result]
        return result

    def move(self):
        self.player = self._move()

    def _move(self) -> Player:
        newcoord: LocalCoord
        match self.player.facing:
            case Facing.RIGHT:
                newcoord = (
                    self.player.position.coord[0],
                    self.player.position.coord[1] + 1,
                )
            case Facing.LEFT:
                newcoord = (
                    self.player.position.coord[0],
                    self.player.position.coord[1] - 1,
                )
            case Facing.UP:
                newcoord = (
                    self.player.position.coord[0] - 1,
                    self.player.position.coord[1],
                )
            case Facing.DOWN:
                newcoord = (
                    self.player.position.coord[0] + 1,
                    self.player.position.coord[1],
                )
        # Coordinates are still within the same square.
        samesquare = (
            0 <= newcoord[0] < self.squares[self.player.position.sqid].slen
            and 0 <= newcoord[1] < self.squares[self.player.position.sqid].slen
        )
        if samesquare:
            newterrain = self.squares[self.player.position.sqid].map[newcoord[0]][
                newcoord[1]
            ]
            match newterrain:
                case Terrain.OPEN:
                    position = Position(self.player.position.sqid, newcoord)
                    return Player(position, self.player.facing)
                case Terrain.BLOCKED:
                    return self.player
        # We've gone over an edge.
        # newsid, newside, glue: Tuple[SquareId, Side, Glueing]
        match self.player.facing:
            case Facing.RIGHT:
                newsid, newside, glue, nrot = self.pattern[
                    self.player.position.sqid, Side.RIGHT
                ]
            case Facing.LEFT:
                newsid, newside, glue, nrot = self.pattern[
                    self.player.position.sqid, Side.LEFT
                ]
            case Facing.UP:
                newsid, newside, glue, nrot = self.pattern[
                    self.player.position.sqid, Side.TOP
                ]
            case Facing.DOWN:
                newsid, newside, glue, nrot = self.pattern[
                    self.player.position.sqid, Side.BOTTOM
                ]
        return self._new_square_move(
            self.player.position.coord, self.player.facing, newsid, newside, glue, nrot
        )

    def _new_square_move(
        self,
        coord: LocalCoord,
        facing: Facing,
        newsquareid: SquareId,
        newside: Side,
        glue: Glueing,
        nrot: int,
    ) -> Position:
        # Coordinate on the edge of the square we just left.
        edgecoord: int
        match facing:
            case Facing.RIGHT | Facing.LEFT:
                edgecoord = coord[0]
            case Facing.UP | Facing.DOWN:
                edgecoord = coord[1]
        # If we are reversing the orientation, then we need to reverse this
        # coordinate.
        N = self.squares[newsquareid].slen
        if glue == Glueing.REVERSED:
            edgecoord = N - edgecoord - 1
        # Local coordinate in the new square we are entering.
        newlocalcoord: LocalCoord
        match newside:
            case Side.RIGHT:
                newlocalcoord = (edgecoord, N - 1)
            case Side.LEFT:
                newlocalcoord = (edgecoord, 0)
            case Side.TOP:
                newlocalcoord = (0, edgecoord)
            case Side.BOTTOM:
                newlocalcoord = (N - 1, edgecoord)
        # Now we can see if we are blocked in the new square.
        newterrain = self.squares[newsquareid].map[newlocalcoord[0]][newlocalcoord[1]]
        match newterrain:
            case Terrain.OPEN:
                position = Position(newsquareid, newlocalcoord)
                facing = self._rotate(Rotation.CLOCKWISE, nrot)
                return Player(position, facing)
            case Terrain.BLOCKED:
                return self.player


def parse_data(data: str) -> Tuple[str, str]:
    mapdata: List[str] = []
    instructiondata: str

    readingmap = True
    for line in data.split("\n"):
        if line.strip() == "":
            readingmap = False
            continue
        if readingmap:
            mapdata.append(line)
        else:
            instructiondata = line.strip()
    return "\n".join(mapdata), instructiondata


ReferencePoints = Dict[SquareId, Coord]


def parse_map_data(
    data: str, N: int, referencepts: ReferencePoints
) -> Dict[SquareId, Square]:
    LOOKUP = {".": Terrain.OPEN, "#": Terrain.BLOCKED}
    squares = {id: Square(id, pt, N, []) for id, pt in referencepts.items()}
    for (n, line), (id, pt) in product(
        enumerate(data.split("\n")), referencepts.items()
    ):
        if pt[1] <= n < pt[1] + N:
            squares[id].map.append([LOOKUP[ch] for ch in line[pt[0] : (pt[0] + N)]])
    return squares


class Instruction(Enum):
    MOVE = 0
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 2


def parse_instruction_data(data: str) -> List[Instruction]:
    buffer: List[str] = []
    instructions: List[Instruction] = []
    for chr in data:
        if chr in {"R", "L"}:
            if buffer:
                instructions.append((Instruction.MOVE, int("".join(buffer))))
                buffer = []
            instructions.append(
                {"R": Instruction.CLOCKWISE, "L": Instruction.COUNTERCLOCKWISE}[chr]
            )
        else:
            buffer.append(chr)
    if buffer:
        instructions.append((Instruction.MOVE, int("".join(buffer))))
    return instructions


if __name__ == "__main__":
    data = get_data(day=22, year=2022)
    mapdata, instructiondata = parse_data(data)

    instructions = parse_instruction_data(instructiondata)

    SIDELEN = 50
    REFPTS = {
        0: (SIDELEN, 0),
        1: (2*SIDELEN, 0),
        2: (SIDELEN, SIDELEN),
        3: (0, 2*SIDELEN),
        4: (SIDELEN, 2*SIDELEN),
        5: (0, 3*SIDELEN)
    }
    squares = parse_map_data(mapdata, SIDELEN, REFPTS)

    FLAT_GLUEING_PATTERN = symmetrize({
        (0, Side.TOP):  (4, Side.BOTTOM, Glueing.MATCHING, 0),
        (0, Side.LEFT): (1, Side.RIGHT, Glueing.MATCHING, 0),
        (1, Side.TOP):  (1, Side.BOTTOM, Glueing.MATCHING, 0),
        (1, Side.LEFT): (0, Side.RIGHT, Glueing.MATCHING, 0),
        (2, Side.TOP):  (0, Side.BOTTOM, Glueing.MATCHING, 0),
        (2, Side.LEFT): (2, Side.RIGHT, Glueing.MATCHING, 0),
        (3, Side.TOP):  (5, Side.BOTTOM, Glueing.MATCHING, 0),
        (3, Side.LEFT): (4, Side.RIGHT, Glueing.MATCHING, 0),
        (4, Side.TOP):  (2, Side.BOTTOM, Glueing.MATCHING, 0),
        (4, Side.LEFT): (3, Side.RIGHT, Glueing.MATCHING, 0),
        (5, Side.TOP):  (3, Side.BOTTOM, Glueing.MATCHING, 0),
        (5, Side.LEFT): (5, Side.RIGHT, Glueing.MATCHING, 0)
    })

    start = Position(0, (0, 0))
    world = World(squares, FLAT_GLUEING_PATTERN, Player(start, Facing.RIGHT))
    world.execute(instructions, False)
    password = world.password()
    print(f"The final password for the flat map is {password}")

    CUBE_GLUEING_PATTERN = symmetrize({
        (2, Side.RIGHT):  (1, Side.BOTTOM, Glueing.MATCHING, 3), # a
        (2, Side.LEFT):   (3, Side.TOP, Glueing.MATCHING, 3),    # b
        (5, Side.RIGHT):  (4, Side.BOTTOM, Glueing.MATCHING, 3), # c
        (1, Side.RIGHT):  (4, Side.RIGHT, Glueing.REVERSED, 2),  # d
        (0, Side.LEFT):   (3, Side.LEFT, Glueing.REVERSED, 2),   # e
        (0, Side.TOP):    (5, Side.LEFT, Glueing.MATCHING, 1),   # f
        (5, Side.BOTTOM): (1, Side.TOP, Glueing.MATCHING, 0),    # g
        (0, Side.RIGHT):  (1, Side.LEFT, Glueing.MATCHING, 0),
        (0, Side.BOTTOM): (2, Side.TOP, Glueing.MATCHING, 0),
        (2, Side.BOTTOM): (4, Side.TOP, Glueing.MATCHING, 0),
        (3, Side.RIGHT):  (4, Side.LEFT, Glueing.MATCHING, 0),
        (3, Side.BOTTOM): (5, Side.TOP, Glueing.MATCHING, 0)
    })
    start = Position(0, (0, 0))
    world = World(squares, CUBE_GLUEING_PATTERN, Player(start, Facing.RIGHT))
    world.execute(instructions, False)
    password = world.password()
    print(f"The final password for the cube map is {password}")