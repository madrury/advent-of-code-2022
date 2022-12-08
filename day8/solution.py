from aocd import get_data # type: ignore
from itertools import pairwise, product
from typing import List, Tuple, Dict

TreePlot = List[List[int]]
TreeRow = List[int]
Position = Tuple[int, int]


def parse_data(data: str) -> TreePlot:
    return [
        [int(d) for d in line]
        for line in data.split('\n')
    ]

def transpose(trees: TreePlot) -> TreePlot:
    N, M = len(trees), len(trees[0])
    return [
        [trees[j][i] for j in range(N)]
        for i in range(M)
    ]

def visible_from_one_end(row: TreeRow) -> List[bool]:
    N = len(row)
    # Cumulative maximum.
    maxfromend = [max(row[:idx+1]) for idx in range(N)]
    return [True] + [left < right for left, right in pairwise(maxfromend)]

def visible_1d(row: TreeRow) -> List[bool]:
    visiblefromleft = visible_from_one_end(row)
    visiblefromright = visible_from_one_end(row[::-1])[::-1]
    # Componentwise or.
    visible = [vfl or vfr for vfl, vfr in zip(visiblefromleft, visiblefromright)]
    return visible

def visible_rowwise(trees: TreePlot) -> List[List[bool]]:
    return [visible_1d(row) for row in trees]

def visible_from_edges(trees: TreePlot) -> List[List[bool]]:
    rowwise = visible_rowwise(trees)
    colwise = transpose(visible_rowwise(transpose(trees)))
    # Componentwise or.
    return [
        [rwv or cwv for rwv, cwv in zip(rwrow, cwrow)]
        for rwrow, cwrow in zip(rowwise, colwise)
    ]

def viewing_distance(row: TreeRow, height: int) -> int:
    for idx, h in enumerate(row):
        if h >= height:
            return idx + 1
    return len(row)

def score_viewing_distance_from_position(trees: TreePlot, p: Position) -> int:
    N, M = len(trees), len(trees[0])
    height = trees[p[0]][p[1]]
    rightwards = trees[p[0]][p[1] + 1:]
    leftwards = trees[p[0]][:p[1]][::-1]
    above = [trees[i][p[1]] for i in range(0, p[0])][::-1]
    below = [trees[i][p[1]] for i in range(p[0]+1, N)]
    return (
        viewing_distance(rightwards, height)
        * viewing_distance(leftwards, height)
        * viewing_distance(above, height)
        * viewing_distance(below, height)
    )

def score_viewing_distance_from_each_position(trees: TreePlot) -> Dict[Position, int]:
    N, M = len(trees), len(trees[0])
    scores = {}
    for i, j in product(range(N), range(M)):
        scores[i, j] = score_viewing_distance_from_position(trees, (i, j))
    return scores


if __name__ == '__main__':
    data = get_data(day=8, year=2022)
    trees = parse_data(data)

    totvis = sum(sum(row) for row in visible_from_edges(trees))
    print(f"The total number of visible trees is {totvis}")

    scores = score_viewing_distance_from_each_position(trees)
    maxscore = max(scores.values())
    print(f"The maximum treehouse score is {maxscore}")

