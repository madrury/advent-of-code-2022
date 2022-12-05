from aocd import get_data # type: ignore
from typing import Tuple, List, Iterable
from itertools import takewhile, dropwhile, groupby
from dataclasses import dataclass

STACKS_LINE_LEN = 35
N_STACKS = 9
N_CHARS_IN_BOX_TOKEN = 4


BoxId = str
Position = int
Stacks = List[List[BoxId]]

@dataclass
class Move:
    n: int
    frm: Position
    to: Position


def split(s: str, splitlen: int) -> List[str]:
     return [
         ''.join(x for _, x in g[1])
         for g in groupby(enumerate(s), lambda t: t[0] // splitlen)
     ]

def parse_data(data: str) -> Tuple[Stacks, List[Move]]:
    stacksitr = takewhile(
        lambda line: len(line) == STACKS_LINE_LEN, data.split('\n')
    )
    movesitr = dropwhile(
        lambda line: len(line) in {STACKS_LINE_LEN, 0},
        data.split('\n')
    )
    return parse_stacks(stacksitr), parse_moves(movesitr)

def parse_stacks(stackitr: Iterable[str]) -> Stacks:
    stackstrs = list(stackitr)[:-1]
    stacks: Stacks = [[] for _ in range(N_STACKS)]
    for line in stackstrs[::-1]:
        tokens = split(line, splitlen=N_CHARS_IN_BOX_TOKEN)
        boxes = [t.strip('[] ') for t in tokens]
        for box, stack in zip(boxes, stacks):
            if box: stack.append(box)
    return stacks

def parse_moves(moveitr: Iterable[str]) -> List[Move]:
    movestrs = list(moveitr)
    moves: List[Move] = []
    for line in movestrs:
        moves.append(Move(*[
            int(n)
            for n in line.replace('move ', '')
                .replace(' from ', '|')
                .replace(' to ', '|')
                .split('|')
        ]))
    return moves

def make_moves_9000(stacks: Stacks, moves: List[Move]) -> Stacks:
    for mv in moves:
        for _ in range(mv.n):
            id = stacks[mv.frm - 1].pop()
            stacks[mv.to - 1].append(id)
    return stacks

def make_moves_9001(stacks: Stacks, moves: List[Move]) -> Stacks:
    for mv in moves:
        fromstack = stacks[mv.frm - 1]
        topstack, btmstack = fromstack[-mv.n:], fromstack[:-mv.n]
        stacks[mv.to - 1] += topstack
        stacks[mv.frm - 1] = btmstack
    return stacks

def top(stacks: Stacks) -> List[BoxId]:
    return [stack[-1] for stack in stacks]


if __name__ == '__main__':
    data = get_data(day=5, year=2022)
    stacks, moves = parse_data(data)

    topstr = ''.join(top(make_moves_9000(stacks, moves)))
    print(f"The top reads {topstr} after moves are made with the 9000 model.")

    stacks, moves = parse_data(data)
    topstr = ''.join(top(make_moves_9001(stacks, moves)))
    print(f"The top reads {topstr} after moves are made with the 9001 model.")