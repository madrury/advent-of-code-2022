import re
from dataclasses import dataclass
from operator import itemgetter
from aocd import get_data # type: ignore
from typing import List, Dict, Tuple, FrozenSet

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
    open_valves: FrozenSet[ValveName],
    stop_remaining: int = 0
) -> Tuple[Pressure, FrozenSet[ValveName]]:

    if remaining <= stop_remaining:
        return 0, open_valves

    remaining_closed_with_flow = {
        nm for nm, valve in valves.items()
        if valve.rate != 0 and nm not in open_valves
    }

    pressure = valves[current].rate * (remaining - 1)
    match len(remaining_closed_with_flow):
        case 0:
            return 0, open_valves
        case 1:
            return pressure, open_valves | {current}

    tails: List[Tuple[Pressure, FrozenSet[ValveName]]] = [
        search(
            valves,
            nextnm,
            remaining - (current != 'AA') - valves[current].tunnels[nextnm],
            open_valves | {current},
            stop_remaining
        )
        for nextnm in remaining_closed_with_flow - {current}
    ]
    best = max(tails, key=itemgetter(0))
    return (pressure + best[0], best[1])


if __name__ == '__main__':
    data = get_data(day=16, year=2022)
    valves = parse_data(data)
    wvalves = to_weighted_valves(valves)

    # No 🐘.
    released, _ = search(wvalves, 'AA', 30, frozenset())
    print(f"Without an elephant, you release {released}")

    # With 🐘.
    released = []
    for stop_time in range(0, 27):
        mereleased, meopened = search(wvalves, 'AA', 26, frozenset(), stop_time)
        elereleased, eleopened = search(wvalves, 'AA', 26, meopened)
        totalreleased = mereleased + elereleased
        released.append(totalreleased)
        print("Stop time: ", stop_time, "Total Released: ", totalreleased)
        print(f"    I released {mereleased} by opening valves {meopened}")
        print(f"    They released {elereleased} by opening valves {eleopened - meopened}")
    maxreleased = max(released)

    print(f"With an elephant, we release {maxreleased}")


