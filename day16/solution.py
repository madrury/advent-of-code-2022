import re
from dataclasses import dataclass
from itertools import chain, combinations
from aocd import get_data # type: ignore
from typing import Union, List, Set, Dict, Tuple, Optional, FrozenSet

ValveName = str
Pressure = int
Duration = int

@dataclass
class NaiveValve:
    name: ValveName
    rate: int
    tunnels: List[ValveName]

@dataclass
class WeightedValve:
    name: ValveName
    rate: int
    tunnels: Dict[ValveName, Duration]


PATTERN = r"Valve ([A-Z][A-Z]) has flow rate=(\d+); tunnels? leads? to valves? ([A-Z, ]+)"

def parse_data(data: str) -> Dict[ValveName, NaiveValve]:
    valves: Dict[ValveName, NaiveValve] = {}
    for line in data.split('\n'):
        match = re.search(PATTERN, line)
        tunnels = [t.strip() for t in match.group(3).split(',')]
        valves[match.group(1)] = NaiveValve(match.group(1), int(match.group(2)), tunnels)
    return valves


def to_weighted_valves(valves: Dict[ValveName, NaiveValve]) -> Dict[ValveName, WeightedValve]:
    weightedvalves: Dict[ValveName, WeightedValve] = {}
    for valve in valves.values():
        weightedvalves[valve.name] = to_weighted_valve(valve, valves)
    return weightedvalves


def to_weighted_valve(valve: NaiveValve, valves: Dict[ValveName, NaiveValve]) -> WeightedValve:
    unvisited: Dict[ValveName, int] = {vn: 100 for vn in valves}
    visited: Dict[ValveName, int] = {}

    unvisited[valve.name] = 0

    while unvisited:
        mindist = min(unvisited.values())
        currentnm = next(nm for nm, dist in unvisited.items() if dist == mindist)
        if all(nbrnm in visited for nbrnm in valves[currentnm].tunnels):
            visited[currentnm] = mindist
            del unvisited[currentnm]
            continue
        for nbrnm in valves[currentnm].tunnels:
            unvisited[nbrnm] = min(visited.get(nbrnm, 100), unvisited.get(nbrnm, 100), mindist + 1)
        visited[currentnm] = mindist
        del unvisited[currentnm]

    return WeightedValve(
        name=valve.name,
        rate=valve.rate,
        tunnels=visited
    )


def search(
    valves: Dict[ValveName, WeightedValve],
    current: ValveName,
    remaining: Duration,
    open_valves: FrozenSet[ValveName]
) -> Pressure:
    if remaining <= 0:
        return 0

    remaining_closed_with_flow = {
        nm for nm, valve in valves.items()
        if valve.rate != 0 and nm not in open_valves
    }

    pressure = valves[current].rate * (remaining - 1)
    match len(remaining_closed_with_flow):
        case 0:
            return 0
        case 1:
            return pressure

    return pressure +  max(
        search(
            valves,
            nextnm,
            remaining - (current != 'AA') - valves[current].tunnels[nextnm],
            open_valves | {current}
        )
        for nextnm in remaining_closed_with_flow - {current}
    )

if __name__ == '__main__':
    data = get_data(day=16, year=2022)
#     data = """
# Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
# Valve BB has flow rate=13; tunnels lead to valves CC, AA
# Valve CC has flow rate=2; tunnels lead to valves DD, BB
# Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
# Valve EE has flow rate=3; tunnels lead to valves FF, DD
# Valve FF has flow rate=0; tunnels lead to valves EE, GG
# Valve GG has flow rate=0; tunnels lead to valves FF, HH
# Valve HH has flow rate=22; tunnel leads to valve GG
# Valve II has flow rate=0; tunnels lead to valves AA, JJ
# Valve JJ has flow rate=21; tunnel leads to valve II
#     """.strip()
    valves = parse_data(data)
    wvalves = to_weighted_valves(valves)

    steamyest = search(wvalves, 'AA', 30, frozenset())
    print(f"Without an elephant, you release {steamyest}")