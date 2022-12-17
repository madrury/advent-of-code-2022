from aocd import get_data # type: ignore
from abc import ABC, abstractmethod
from itertools import cycle, islice
from typing import Tuple, Set, Optional, Iterable, Literal, Type

Coord = Tuple[int, int]
Cave = int
Direction = Literal['<', '>']


class Piece:

    def __init__(self, position: Coord):
        self.position = position
        self.blocks: Set[Coord] = self._blocks()

    def move_left(self, cave: Cave) -> Optional['Piece']:
        new = self.__class__((self.position[0] - 1, self.position[1]))
        if new.is_unblocked(cave):
            return new
        return None

    def move_right(self, cave: Cave):
        new = self.__class__((self.position[0] + 1, self.position[1]))
        if new.is_unblocked(cave):
            return new
        return None

    def move_down(self, cave: Cave):
        new = self.__class__((self.position[0], self.position[1] - 1))
        if new.is_unblocked(cave):
            return new
        return None

    @abstractmethod
    def is_unblocked(self, cave: Cave, offset: Coord) -> bool:
        pass

    abstractmethod
    def _blocks(self) -> Set[Coord]:
        pass

class FlatPiece(Piece):


    def _blocks(self) -> Iterable[Coord]:
        return {
            (self.position[0] + dx, self.position[1])
            for dx in range(0, 4)
        }

    def is_unblocked(self, cave: Cave) -> bool:
        return (
            self.position[0] >= 0
            and self.position[0] + 3 <= 6
            and all(block not in cave.blocks for block in self.blocks)
        )

class CrossPiece(Piece):

    def _blocks(self) -> Iterable[Coord]:
        return {
            (self.position[0], self.position[1] + 1),
            (self.position[0] + 1, self.position[1]),
            (self.position[0] + 2, self.position[1] + 1),
            (self.position[0] + 1, self.position[1] + 2),
            (self.position[0] + 1, self.position[1] + 1)
        }

    def is_unblocked(self, cave: Cave) -> bool:
        return (
            self.position[0] >= 0
            and self.position[0] + 2 <= 6
            and all(block not in cave.blocks for block in self.blocks)
        )

class ElPiece(Piece):

    def _blocks(self) -> Iterable[Coord]:
        return {
            (self.position[0], self.position[1]),
            (self.position[0] + 1, self.position[1]),
            (self.position[0] + 2, self.position[1]),
            (self.position[0] + 2, self.position[1] + 1),
            (self.position[0] + 2, self.position[1] + 2)
        }

    def is_unblocked(self, cave: Cave) -> bool:
        return (
            self.position[0] >= 0
            and self.position[0] + 2 <= 6
            and all(block not in cave.blocks for block in self.blocks)
        )

class TallPiece(Piece):

    def _blocks(self) -> Iterable[Coord]:
        return {
            (self.position[0], self.position[1] + dy)
            for dy in range(0, 4)
        }

    def is_unblocked(self, cave: Cave) -> bool:
        return (
            self.position[0] >= 0
            and self.position[0] <= 6
            and all(block not in cave.blocks for block in self.blocks)
        )

class SquarePiece(Piece):

    def _blocks(self) -> Set[Coord]:
        return {
            (self.position[0], self.position[1]),
            (self.position[0] + 1, self.position[1]),
            (self.position[0], self.position[1] + 1),
            (self.position[0] + 1, self.position[1] + 1)
        }

    def is_unblocked(self, cave: Cave) -> bool:
        return (
            self.position[0] >= 0
            and self.position[0] + 1 <= 6
            and all(block not in cave.blocks for block in self.blocks)
        )

class Cave:

    def __init__(self):
        self.blocks: Set[Coord] = {
            (x, -1) for x in range(0, 7)
        }

    @property
    def top(self) -> int:
        return max(y for _, y in self.blocks)

    def add(self, piece: Piece):
        self.blocks.update(piece.blocks)

    def cascade(self, pieces: Iterable[Type[Piece]], directions: Iterable[Direction]):
        for n, piece_t in enumerate(pieces):
            # if n % 10_000 == 0:
            #     print('.', end='', flush=True)
            piece = piece_t((2, self.top + 4))
            final = self.drop(piece, directions)
            # print(f"{final.__class__.__name__} rests at {final.position}")
            self.add(final)

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

    PIECES = [FlatPiece, CrossPiece, ElPiece, TallPiece, SquarePiece]
    pieces = islice(cycle(PIECES), 0, 2022)
    directions = cycle(data.strip())

    cave = Cave()
    cave.cascade(pieces, directions)
    print(f"The top is {cave.top + 1} units above the floor")