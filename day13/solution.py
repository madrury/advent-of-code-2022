
from aocd import get_data # type: ignore
from enum import Enum
from functools import cmp_to_key
from typing import Union, List, Tuple


Packet = List[Union[int, List['Packet']]]

DIVIDER2 = [[2]]
DIVIDER6 = [[6]]

class Comparison(Enum):
    INORDER = -1
    UNKNOWN = 0
    OUTOFORDER = 1

def parse_data(data: str) -> List[Tuple[Packet, Packet]]:
    pairs: List[Tuple[Packet, Packet]] = []
    left, right = None, None
    for ln, line in enumerate(data.split('\n')):
        if ln % 3 == 0:
            left = eval(line)
        elif ln % 3 == 1:
            right = eval(line)
        else:
            pairs.append((left, right))
            left, right = None, None
    # You'll miss the last one, dumbass. 👎
    pairs.append((left, right))
    return pairs

def to_packet_list(pairs: List[Tuple[Packet, Packet]]) -> List[Packet]:
    plist = [DIVIDER2, DIVIDER6]
    for left, right in pairs:
        plist.append(left)
        plist.append(right)
    return plist

def print_packet_list(packets: List[Packet]):
    for idx, packet in enumerate(packets, start=1):
        print(f"{idx:<3}, {packet}")

def compare(left: Packet, right: Packet):
    match left, right:
        case int(x), int(y):
            return compare_ints(x, y)
        case [*xs], [*ys]:
            return compare_lists(left, right)
        case int(x), [*ys]:
            return compare_lists([x], right)
        case [*xs], int(y):
            return compare_lists(left, [y])

def compare_key(left: Packet, right: Packet) -> int:
    return compare(left, right).value

def compare_ints(x: int, y: int):
    if x < y:
        return Comparison.INORDER
    elif x == y:
        return Comparison.UNKNOWN
    elif x > y:
        return Comparison.OUTOFORDER
    else:
        raise ValueError("Uhhh?")

def compare_lists(xs: List[Packet], ys: List[Packet]) -> Comparison:
    for x, y in zip(xs, ys):
        match cmp := compare(x, y):
            case Comparison.UNKNOWN:
                continue
            case _:
                return cmp
    # Reached here because all comparisons were unkown.
    if len(xs) < len(ys):
        return Comparison.INORDER
    elif len(xs) > len(ys):
        return Comparison.OUTOFORDER
    else:
        return Comparison.UNKNOWN


if __name__ == '__main__':
    data = get_data(day=13, year=2022)
    pairs = parse_data(data)
    in_order = (
        compare(left, right) == Comparison.INORDER
        for left, right in pairs
    )
    idxsum = sum(idx for idx, order in enumerate(in_order, start=1) if order)
    print(f"The index sum of the ordered pairs is {idxsum}")

    packets = to_packet_list(pairs)
    packets = sorted(to_packet_list(pairs), key=cmp_to_key(compare_key))

    for left, right in [(packets[i], packets[i+1]) for i in range(len(packets) - 1)]:
        assert compare(left, right) == Comparison.INORDER

    divider_2_idx = next(idx for idx, p in enumerate(packets, start=1) if p == DIVIDER2)
    divider_6_idx = next(idx for idx, p in enumerate(packets, start=1) if p == DIVIDER6)
    print(f"Packet positions are {divider_2_idx} and {divider_6_idx}")
    print(f"Decoder key is {divider_2_idx*divider_6_idx}")