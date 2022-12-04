from aocd import get_data # type: ignore
from typing import Tuple, List, Set, Dict
from enum import Enum


class Shape(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

OPPONENT_MAPPING = {char: shape for (char, shape) in zip(['A', 'B', 'C'], Shape)}
PLAYER_MAPPING = {char: shape for (char, shape) in zip(['X', 'Y', 'Z'], Shape)}

Game = Tuple[Shape, Shape]

WINNING_PLAYS: Set[Game] = {
    (Shape.ROCK, Shape.PAPER),
    (Shape.PAPER, Shape.SCISSORS),
    (Shape.SCISSORS, Shape.ROCK)
}

Score = int

SHAPE_SCORES: Dict[Shape, Score] = {
    Shape.ROCK: 1,
    Shape.PAPER: 2,
    Shape.SCISSORS: 3
}

class Result(Enum):
    WIN = 0
    LOSE = 1
    DRAW = 2

RESULT_SCORES: Dict[Result, Score] = {
    Result.WIN: 6,
    Result.LOSE: 0,
    Result.DRAW: 3
}

PLAYER_RESULT_MAPPING = {
    char: result for (char, result) in zip(['Z', 'X', 'Y'], Result)
}

PLAYER_MOVE_MAPPING: Dict[Tuple[Shape, Result], Shape] = {
    (Shape.ROCK, Result.WIN): Shape.PAPER,
    (Shape.ROCK, Result.DRAW): Shape.ROCK,
    (Shape.ROCK, Result.LOSE): Shape.SCISSORS,
    (Shape.PAPER, Result.WIN): Shape.SCISSORS,
    (Shape.PAPER, Result.DRAW): Shape.PAPER,
    (Shape.PAPER, Result.LOSE): Shape.ROCK,
    (Shape.SCISSORS, Result.WIN): Shape.ROCK,
    (Shape.SCISSORS, Result.DRAW): Shape.SCISSORS,
    (Shape.SCISSORS, Result.LOSE): Shape.PAPER
}


def parse_data_shapes(data: str) -> List[Game]:
    gamechrs = (ln.strip().split(' ') for ln in data.split('\n'))
    return [
        (OPPONENT_MAPPING[opchr], PLAYER_MAPPING[plychr])
        for opchr, plychr in gamechrs
    ]

def parse_data_results(data: str) -> List[Tuple[Shape, Shape]]:
    gamechrs = (ln.strip().split(' ') for ln in data.split('\n'))
    return [
        (
            OPPONENT_MAPPING[opchr],
            PLAYER_MOVE_MAPPING[OPPONENT_MAPPING[opchr], PLAYER_RESULT_MAPPING[plychr]]
        )
        for opchr, plychr in gamechrs
    ]

def result(gm: Game) -> Result:
    if gm[0] == gm[1]:
        return Result.DRAW
    elif gm in WINNING_PLAYS:
        return Result.WIN
    return Result.LOSE

def score(gm: Game) -> Score:
    res, ply = result(gm), gm[1]
    return SHAPE_SCORES[ply] + RESULT_SCORES[res]


if __name__ == '__main__':
    data = get_data(day=2, year=2022)
    total = sum(score(gm) for gm in parse_data_shapes(data))
    print(f"Your total score misinterpreting the data is {total}")

    total = sum(score(gm) for gm in parse_data_results(data))
    print(f"Your total score correctly interpreting the data is {total}")
