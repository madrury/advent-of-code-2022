from aocd import get_data # type: ignore
from abc import abstractproperty
from dataclasses import dataclass
from itertools import cycle, islice
from typing import Tuple, Set, Iterable, Literal, Dict
import numpy as np

Coord = Tuple[int, int]
Height = int
Direction = Literal['<', '>']
StackTop = np.array
StackTopPattern = Tuple[int, int, int, int ,int, int]


class Piece:

    width = 0

    def __init__(self, position: Coord = (0, 0)):
        self.position = position

    @abstractproperty
    def blocks(self) -> Iterable[Coord]:
        pass

    @abstractproperty
    def top(self) -> int:
        pass

    @abstractproperty
    def pattern(self) -> np.array:
        pass

    def move_left(self, cave: 'Cave') -> 'Piece':
        within_bounds = (self.position[0] >= 1)
        if (within_bounds and self.position[1] > cave.stackheight) or (within_bounds and self.is_unblocked(cave, (-1, 0))):
            self.position = (self.position[0] - 1, self.position[1])
        return self

    def move_right(self, cave: 'Cave') -> 'Piece':
        within_bounds = (self.position[0] + self.width + 1 <= 6)
        if (within_bounds and self.position[1] > cave.stackheight) or (within_bounds and self.is_unblocked(cave, (1, 0))):
            self.position = (self.position[0] + 1, self.position[1])
        return self

    def move_down(self, cave: 'Cave') -> 'Piece':
        if (self.position[1] > cave.stackheight + 1) or self.is_unblocked(cave, (0, -1)):
            self.position = (self.position[0], self.position[1] - 1)
            return self
        return None

    def is_unblocked(self, cave: 'Cave', offset: Coord) -> bool:
            return all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)

class FlatPiece(Piece):

    width = 3

    @property
    def blocks(self) -> Iterable[Coord]:
        yield from (
            (self.position[0] + dx, self.position[1])
            for dx in range(0, 4)
        )

    @property
    def top(self) -> int:
        return self.position[1]

    @property
    def pattern(self) -> np.array:
        return np.full(4, self.position[1])

class CrossPiece(Piece):

    width = 2

    @property
    def blocks(self) -> Iterable[Coord]:
        yield (self.position[0], self.position[1] + 1)
        yield (self.position[0] + 1, self.position[1])
        yield (self.position[0] + 2, self.position[1] + 1)
        yield (self.position[0] + 1, self.position[1] + 2)
        yield (self.position[0] + 1, self.position[1] + 1)

    @property
    def top(self) -> int:
        return self.position[1] + 2

    @property
    def pattern(self) -> np.array:
        return np.full(3, self.position[1]) + np.array([1, 2, 1])

class ElPiece(Piece):

    width = 2

    @property
    def blocks(self) -> Iterable[Coord]:
        yield (self.position[0], self.position[1])
        yield ( self.position[0] + 1, self.position[1])
        yield (self.position[0] + 2, self.position[1])
        yield (self.position[0] + 2, self.position[1] + 1)
        yield (self.position[0] + 2, self.position[1] + 2)

    @property
    def top(self) -> int:
        return self.position[1] + 2

    @property
    def pattern(self) -> np.array:
        return np.full(3, self.position[1]) + np.array([0, 0, 2])

class TallPiece(Piece):

    width = 0

    @property
    def blocks(self) -> Iterable[Coord]:
        yield from (
            (self.position[0], self.position[1] + dy)
            for dy in range(0, 4)
        )

    @property
    def top(self) -> int:
        return self.position[1] + 3

    @property
    def pattern(self) -> np.array:
        return np.array([self.position[1] + 3])

class SquarePiece(Piece):

    width = 1

    @property
    def blocks(self) -> Iterable[Coord]:
        yield (self.position[0], self.position[1])
        yield (self.position[0] + 1, self.position[1])
        yield (self.position[0], self.position[1] + 1)
        yield (self.position[0] + 1, self.position[1] + 1)

    @property
    def top(self) -> int:
        return self.position[1] + 1

    @property
    def pattern(self) -> np.array:
        return np.full(2, self.position[1] + 1)


@dataclass(frozen=True)
class CycleIdentifier:
    piecereside: int
    windresidue: int
    pattern: StackTopPattern

@dataclass
class CycleValue:
    pieceidx: int
    stackheight: Height

@dataclass
class CascadeReturnValue:
    cycle_height_increase: int
    cycle_length: int
    cycle_start_height: Height
    cycle_start_pieceidx: int

class Cave:

    def __init__(self, n_pieces: int, n_wind: int):
        self.n_pieces = n_pieces
        self.n_wind = n_wind

        self.blocks: Set[Coord] = {
            (x, -1) for x in range(0, 7)
        }

        self.stackheight: Height = -1
        self.stacktop: StackTop = np.full(7, -1)
        self.cycleids: Dict[CycleIdentifier, CycleValue] = {}

    def add(self, piece: Piece):
        self.blocks.update(piece.blocks)

    def cascade(self, pieces: Iterable[Piece], directions: Iterable[Tuple[int, Direction]], check_cycles=True):
        for pieceidx, piece in enumerate(pieces):
            piece.position = (2, self.stackheight + 4)
            windidx, final = self.drop(piece, directions)
            self.stackheight = max(self.stackheight, final.top)
            self.stacktop[final.position[0]:(final.position[0] + final.width + 1)] = final.pattern
            self.add(final)

            cycle_id = CycleIdentifier(
                pieceidx % self.n_pieces,
                windidx % self.n_wind,
                tuple(np.diff(self.stacktop))
            )

            if check_cycles and cycle_id in self.cycleids:
                print(f"Cycle detected at {pieceidx=} and {windidx=}!")
                print(f"Cycle id:", cycle_id)
                previous = self.cycleids[cycle_id]
                cycle_length = pieceidx - previous.pieceidx
                height_increase = self.stackheight - previous.stackheight
                print(f"Cycle started at: {previous.pieceidx}")
                print(f"Cycle Length: {cycle_length}")
                print(f"Height at start of cycle: {previous.stackheight}")
                print(f"Height increase per cycle: {height_increase}")
                return CascadeReturnValue(
                    cycle_height_increase=height_increase,
                    cycle_length=cycle_length,
                    cycle_start_height=previous.stackheight,
                    cycle_start_pieceidx=previous.pieceidx
                )

            self.cycleids[cycle_id] = CycleValue(
                pieceidx=pieceidx,
                stackheight=self.stackheight
            )

    def drop(self, piece: Piece, directions: Iterable[Tuple[int, Direction]]) -> Piece:
        while True:
            match next(directions):
                case n, '<':
                    piece.move_left(self)
                case n, '>':
                    piece.move_right(self)
                case x:
                    raise ValueError(f"Unknown direction {x}.")

            if not piece.move_down(self):
                break

        return n, piece


if __name__ == '__main__':
    TRILLION = 1_000_000_000_000

    data = get_data(day=17, year=2022).strip()
    N_WIND = len(data)

    PIECES = [FlatPiece(), CrossPiece(), ElPiece(), TallPiece(), SquarePiece()]
    N_PIECES = len(PIECES)

    pieces = cycle(PIECES)
    directions = cycle(data.strip())

    cave = Cave(n_pieces=N_PIECES, n_wind=N_WIND)
    crv = cave.cascade(pieces, enumerate(directions), check_cycles=True)

    n_total_cycles = (TRILLION - crv.cycle_start_pieceidx) // crv.cycle_length
    end_of_cycles_height = crv.cycle_start_height + n_total_cycles * crv.cycle_height_increase
    remaining_pieces = TRILLION - crv.cycle_start_pieceidx - n_total_cycles * crv.cycle_length
    print(f"After all the cycles, the height is {end_of_cycles_height}")
    print(f"After all the cycles, there are {remaining_pieces} pieces remaining")

    current_height = cave.stackheight
    cave.cascade(islice(pieces, 0, remaining_pieces), enumerate(directions), check_cycles=False)
    additional_height = cave.stackheight - current_height
    print(f"The {remaining_pieces} contribute {additional_height} additional height.")
    print(f"The top of the cave is {end_of_cycles_height + additional_height} above the floor.")
