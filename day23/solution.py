from aocd import get_data  # type: ignore
from typing import List, Tuple, Dict, Set, Optional
from itertools import cycle, islice, product, count
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

ELF = '#'

ElfId = int
Coord = Tuple[int, int]

class Direction(Enum):
    NORTH = 0
    SOUTH = 1
    WEST = 2
    EAST = 3


Board = Dict[Coord, ElfId]
ProposedMoves = Dict[Coord, List[ElfId]]


def parse_data(data: str) -> Board:
    board: Board = {}
    elfid: ElfId = 0
    for rowidx, row in enumerate(data.split('\n')):
        for colidx, ch in enumerate(row):
            if ch == ELF:
                board[(rowidx, colidx)] = elfid
                elfid += 1
    return board


def get_bounds(board: Board) -> Tuple[Coord, Coord]:
    minrow = min(coord[0] for coord in board)
    maxrow = max(coord[0] for coord in board)
    mincol = min(coord[1] for coord in board)
    maxcol = max(coord[1] for coord in board)
    return (minrow, mincol), (maxrow, maxcol)


def print_board(board: Board):
    (minrow, mincol), (maxrow, maxcol) = get_bounds(board)
    for rowidx in range(minrow - 1, maxrow + 2):
        row = [
            ('#' if (rowidx, colidx) in board else '.')
            for colidx in range(mincol - 1, maxcol + 2)
        ]
        print(''.join(row))


def scatter(board: Board, n_rounds: int, doprint: bool = False) -> Board:
    if doprint:
        print("Initial Board:")
        print_board(board)
        print()
    for round in range(n_rounds):
        proposals = make_proposals(board, round=round)
        board = update_board(board, proposals)
        if doprint:
            print(f"Round {round} Proposals:")
            print(proposals)
            print(f"After Round {round}:")
            print_board(board)
            print()
    return board


def scatter_until_stable(board: Board) -> int:
    for round in count(0):
        lastboard = board.copy()
        proposals = make_proposals(board, round=round)
        board = update_board(board, proposals)
        if board == lastboard:
            break
    return round, board


def make_proposals(board: Board, round: int) -> ProposedMoves:
    proposals: Dict[Coord, List[ElfId]] = defaultdict(list)
    for coord, elfid in board.items():
        # print(f"Elf {elfid} at {coord} considering...")
        firstproposal: Optional[Coord] = None
        n_proposals: int = 0
        for direction in islice(cycle(Direction), round, round+4):
            # print("    ", direction)
            thisproposal = make_proposal(coord, direction, board)
            # print("    Proposal: ", thisproposal)
            n_proposals += (thisproposal is not None)
            if thisproposal and not firstproposal:
                firstproposal = thisproposal
        if n_proposals == 4:
            # print("    All proposals accepted, staying put.")
            proposals[coord].append(elfid)
        elif firstproposal is not None:
            # print(f"    Accepted proposal is {firstproposal}.")
            proposals[firstproposal].append(elfid)
    return proposals


def make_proposal(coord: Coord, direction: Direction, board: Board) -> Coord:
    coords: List[Coord]
    match direction:
        case Direction.NORTH:
            coords = [(coord[0] - 1, coord[1] - 1), (coord[0] - 1, coord[1]), (coord[0] - 1, coord[1] + 1)]
        case Direction.SOUTH:
            coords = [(coord[0] + 1, coord[1] - 1), (coord[0] + 1, coord[1]), (coord[0] + 1, coord[1] + 1)]
        case Direction.WEST:
            coords = [(coord[0] - 1, coord[1] - 1), (coord[0], coord[1] - 1), (coord[0] + 1, coord[1] - 1)]
        case Direction.EAST:
            coords = [(coord[0] - 1, coord[1] + 1), (coord[0], coord[1] + 1), (coord[0] + 1, coord[1] + 1)]
    allempty = all(coord not in board for coord in coords)
    if allempty:
        return coords[1] # The middle one!
    return None


def update_board(board: Board, proposals: ProposedMoves) -> Board:
    newboard: Board = {}
    allelves = set(board.values())
    for coord, maybeelves in proposals.items():
        if len(maybeelves) == 1:
            newboard[coord] = maybeelves[0]
    remainingelves = allelves - set(newboard.values())
    for elf in remainingelves:
        currentcoord = next(iter({coord for coord, elfid in board.items() if elfid == elf}))
        newboard[currentcoord] = elf
    return newboard


def count_empty_tiles(board: Board) -> int:
    (minrow, mincol), (maxrow, maxcol) = get_bounds(board)
    return sum(
        (row, col) not in board
        for row, col in product(
            range(minrow, maxrow + 1),
            range(mincol, maxcol + 1)
        )
    )


if __name__ == "__main__":
    data = get_data(day=23, year=2022)

    board = parse_data(data)
    finalboard = scatter(board, n_rounds=20)
    empty_tiles = count_empty_tiles(finalboard)
    print(f"The number of empty tiles in the enveloping rectangle is {empty_tiles}")

    n_rounds, board = scatter_until_stable(board)
    print(f"Eleves stabalize after {n_rounds + 1} rounds.")