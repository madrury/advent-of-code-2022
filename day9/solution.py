from aocd import get_data # type: ignore
from enum import Enum
from dataclasses import dataclass
from itertools import pairwise
from typing import List, Tuple

Position = Tuple[int, int]
PositionΔ = Tuple[int, int]

def sign(n: int) -> int:
    if n == 0: return 0
    if n > 0: return 1
    if n < 0: return -1

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


@dataclass
class Move:
    direction: Direction
    times: int

    @staticmethod
    def from_str(s: str):
        match s.split(' '):
            case 'U', n:
                return Move(Direction.UP, int(n))
            case 'D', n:
                return Move(Direction.DOWN, int(n))
            case 'L', n:
                return Move(Direction.LEFT, int(n))
            case 'R', n:
                return Move(Direction.RIGHT, int(n))

    def to_Δ(self) -> PositionΔ:
        match self:
            case Move(Direction.UP, n):
                return (0, n)
            case Move(Direction.DOWN, n):
                return (0, -n)
            case Move(Direction.LEFT, n):
                return (-n, 0)
            case Move(Direction.RIGHT, n):
                return (n, 0)

class Knot:
    def __init__(self, x: int, y: int):
        self.position = (x, y)
        self.history: List[Position] = [(x, y)]

    def move(self, move: Move):
        moveΔ = move.to_Δ()
        position = (
            self.position[0] + moveΔ[0],
            self.position[1] + moveΔ[1]
        )
        self.move_to(position)

    def move_to(self, position: Position):
        self.position = position
        self.history.append(position)

    def follow(self, leader: 'Knot'):
        positionΔ = (
            leader.position[0] - self.position[0],
            leader.position[1] - self.position[1]
        )
        # They're still touching.
        if max(abs(positionΔ[0]), abs(positionΔ[1])) <= 1:
            return
        # Directly left or right.
        elif abs(positionΔ[0]) > 1 and positionΔ[1] == 0:
            self.move_to((
                leader.position[0] - sign(positionΔ[0]),
                leader.position[1]
            ))
        # Directly above or below.
        elif abs(positionΔ[1]) > 1 and positionΔ[0] == 0:
            self.move_to((
                leader.position[0],
                leader.position[1] - sign(positionΔ[1]),
            ))
        # Nither directly vertical or horizontal: move once diagonally.
        else:
            self.move_to((
                self.position[0] + sign(positionΔ[0]),
                self.position[1] + sign(positionΔ[1])
            ))

def parse_data(data: str) -> List[Move]:
    return to_single_moves([
        Move.from_str(line) for line in data.split('\n')
    ])

def to_single_moves(moves: List[Move]) -> List[Move]:
    flatmoves: List[Move] = []
    for move in moves:
        flatmoves.extend([Move(move.direction, 1) for _ in range(move.times)])
    return flatmoves

def move_rope(head: Knot, tail: Knot, moves: List[Move]):
    for move in moves:
        head.move(move)
        tail.follow(head)

def move_multirope(rope: List[Knot], moves: List[Move]):
    for move in moves:
        rope[0].move(move)
        for head, tail in pairwise(rope):
            # while not head.is_touching(tail):
            tail.follow(head)


if __name__ == '__main__':
    data = get_data(day=9, year=2022)
    moves = parse_data(data)

    head, tail = Knot(0, 0), Knot(0, 0)
    move_rope(head, tail, moves)
    n_visited_tail = len(set(tail.history))
    print(f"The number of positions visited by the tail is {n_visited_tail}")

    multirope = [Knot(0, 0) for _ in range(10)]
    move_multirope(multirope, moves)
    n_visited_tail = len(set(multirope[-1].history))
    print(f"The number of positions visited by the tail is {n_visited_tail}")