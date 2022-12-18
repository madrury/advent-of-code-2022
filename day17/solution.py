from aocd import get_data # type: ignore
from abc import ABC, abstractmethod, abstractproperty
from itertools import cycle, islice
from typing import Tuple, Set, Optional, Iterable, Literal, Type

Coord = Tuple[int, int]
Cave = int
Direction = Literal['<', '>']


class Piece:

    def __init__(self, position: Coord = (0, 0)):
        self.position = position

    @abstractproperty
    def blocks(self) -> Iterable[Coord]:
        pass

    @abstractproperty
    def top(self) -> int:
        pass

    def move_left(self, cave: Cave) -> Optional['Piece']:
        if self.is_unblocked(cave, (-1, 0)):
            self.position = (self.position[0] - 1, self.position[1])
            return self
        return None

    def move_right(self, cave: Cave):
        if self.is_unblocked(cave, (1, 0)):
            self.position = (self.position[0] + 1, self.position[1])
            return self
        return None

    def move_down(self, cave: Cave):
        if self.is_unblocked(cave, (0, -1)):
            self.position = (self.position[0], self.position[1] - 1)
            return self
        return None

    @abstractmethod
    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        pass


class FlatPiece(Piece):

    @property
    def blocks(self) -> Iterable[Coord]:
        yield from (
            (self.position[0] + dx, self.position[1])
            for dx in range(0, 4)
        )

    @property
    def top(self) -> int:
        return self.position[1]

    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        return (
            self.position[0] + offset[0] >= 0
            and self.position[0] + offset[0] + 3 <= 6
            and all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)
        )

class CrossPiece(Piece):

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

    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        return (
            self.position[0] + offset[0] >= 0
            and self.position[0] + offset[0] + 2 <= 6
            and all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)
        )

class ElPiece(Piece):

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

    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        return (
            self.position[0] + offset[0] >= 0
            and self.position[0] + offset[0] + 2 <= 6
            and all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)
        )

class TallPiece(Piece):

    @property
    def blocks(self) -> Iterable[Coord]:
        yield from (
            (self.position[0], self.position[1] + dy)
            for dy in range(0, 4)
        )

    @property
    def top(self) -> int:
        return self.position[1] + 3

    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        return (
            self.position[0] + offset[0] >= 0
            and self.position[0] + offset[0] <= 6
            and all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)
        )

class SquarePiece(Piece):

    @property
    def blocks(self) -> Iterable[Coord]:
        yield (self.position[0], self.position[1])
        yield (self.position[0] + 1, self.position[1])
        yield (self.position[0], self.position[1] + 1)
        yield (self.position[0] + 1, self.position[1] + 1)

    @property
    def top(self) -> int:
        return self.position[1] + 1

    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        return (
            self.position[0] + offset[0] >= 0
            and self.position[0] + offset[0] + 1 <= 6
            and all((block[0] + offset[0], block[1] + offset[1]) not in cave.blocks for block in self.blocks)
        )

class Cave:

    def __init__(self):
        self.blocks: Set[Coord] = {
            (x, -1) for x in range(0, 7)
        }
        self.top = -1

    def gc(self):
        yidx = self.top
        while True:
            if all((xidx, yidx) in self.blocks for xidx in range(0, 7)):
                break
            yidx -= 1
        self.blocks = {
            block for block in self.blocks if block[1] >= yidx
        }

    def add(self, piece: Piece):
        self.blocks.update(piece.blocks)

    def cascade(self, pieces: Iterable[Piece], directions: Iterable[Direction]):
        for n, piece in enumerate(pieces):
            if n % 1_000_000 == 0:
                self.gc()
            if n % 10_000 == 0:
                print('.', end='', flush=True)
            piece.position = (2, self.top + 4)
            final = self.drop(piece, directions)
            self.add(final)
            self.top = max(self.top, final.top)
            # print(f"{final.__class__.__name__} rests at {final.position}")
            # print(f"Blocks: {self.blocks}")

    def drop(self, piece: Piece, directions: Iterable[Direction]) -> Piece:
        while True:
            match next(directions):
                case '<':
                    nextpiece = piece.move_left(self)
                case '>':
                    nextpiece = piece.move_right(self)
                case _:
                    raise ValueError(f"Unknown direction.")
            if nextpiece:
                piece = nextpiece

            nextpiece = piece.move_down(self)
            if nextpiece:
                piece = nextpiece
                continue
            else:
                break

        return piece


if __name__ == '__main__':
    data = get_data(day=17, year=2022)

    PIECES = [FlatPiece(), CrossPiece(), ElPiece(), TallPiece(), SquarePiece()]
    pieces = islice(cycle(PIECES), 0, 2022)
    directions = cycle('>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>')
    directions = cycle(data.strip())

    cave = Cave()
    cave.cascade(pieces, directions)
    print(f"The top is {cave.top + 1} units above the floor")