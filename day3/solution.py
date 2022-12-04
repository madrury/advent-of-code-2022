from aocd import get_data # type: ignore
from typing import Tuple, List, Set
from itertools import groupby


Item = str
Compartment = Set[Item]
Rucksack = Tuple[Compartment, Compartment]
Priority = int

def halve(s: str) -> Tuple[str, str]:
    l = len(s)
    return s[:l//2], s[l//2:]

def parse_data(data: str) -> List[Rucksack]:
    splitlines = (halve(line.strip()) for line in data.split('\n'))
    return [
        (set(left), set(right)) for left, right in splitlines
    ]

def group_into_threes(sacks: List[Rucksack]) -> List[Tuple[Rucksack, Rucksack, Rucksack]]:
    keyf = lambda t: t[0] // 3
    threesacks_w_unneeded_idx = (
        list(x) for _, x in groupby(enumerate(sacks), key=keyf)
    )
    return [
        (ts[0][1], ts[1][1], ts[2][1]) for ts in threesacks_w_unneeded_idx
    ]

def unwrap(s: Set[Item]) -> Item:
    return next(iter(s))

def shared(r: Rucksack) -> Item:
    return unwrap(r[0] & r[1])

def badge(r0: Rucksack, r1: Rucksack, r2: Rucksack) -> Item:
    return unwrap((r0[0] | r0[1]) & (r1[0] | r1[1]) & (r2[0] | r2[1]))

def priority(item: Item) -> Priority:
    o = ord(item)
    return (o >= 97)*(o - 96) + (o < 97)*(o - 65 + 27)


if __name__ == '__main__':
    data = get_data(day=3, year=2022)

    totalpriority = sum(priority(shared(r)) for r in parse_data(data))
    print(f"The total priority of shared items is {totalpriority}")

    badges: List[Item] = [
        badge(*sacks) for sacks in group_into_threes(parse_data(data))
    ]
    badgepriority = sum(priority(badge) for badge in badges)
    print(f"The total priority of badges is {badgepriority}")