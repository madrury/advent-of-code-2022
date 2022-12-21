from aocd import get_data # type: ignore
from typing import List, Tuple, Dict
from dataclasses import dataclass
import cpmpy as cp
import numpy as np
import re

PATTERN = r"Blueprint (\d+): Each ore robot costs (\d) ore. Each clay robot costs (\d) ore. Each obsidian robot costs (\d) ore and (\d+) clay. Each geode robot costs (\d) ore and (\d+) obsidian."
N_ROUNDS = 25

MAX_N_RESOURCES = 500
MAX_N_ROBOTS = 50

ORE_IDX, CLAY_IDX, OBSIDIAN_IDX, GEODE_IDX = range(4)

Cost = int
BlueprintId = int

@dataclass
class RobotCost:
    ore: Cost
    clay: Cost
    obsidian: Cost

@dataclass
class Blueprint:
    id: BlueprintId
    ore: RobotCost
    clay: RobotCost
    obsidian: RobotCost
    geode: RobotCost

@dataclass
class ModelVariables:
    resources: cp.IntVar
    robots: cp.IntVar
    constructions: cp.BoolVar


def parse_data(data: str) -> List[Blueprint]:
    return [
        parse_line(line) for line in data.split('\n')
    ]

def parse_line(line: str) -> Blueprint:
    match = re.match(PATTERN, line)
    return Blueprint(
        id=int(match.group(1)),
        ore=RobotCost(int(match.group(2)), 0, 0),
        clay=RobotCost(int(match.group(3)), 0, 0),
        obsidian=RobotCost(int(match.group(4)), int(match.group(5)), 0),
        geode=RobotCost(int(match.group(6)), 0, int(match.group(7)))
    )

def print_array_values(vars: ModelVariables):
    it = zip(vars.constructions, vars.resources, vars.robots)
    print("         Construct     Resource       Robot")
    for idx, (crow, rrow, robrow) in enumerate(it):
        # print(crow, rrow, robrow)
        print(
            f'round {idx:<3}: '
            + ', '.join(str(v.value()) for v in crow)
            + '  :  '
            + (' '*10 if idx == 0 else ', '.join(str(v.value()) for v in rrow))
            + '  :  '
            + (' '*10 if idx == 0 else ', '.join(str(v.value()) for v in robrow))
        )


def make_model(blueprint: Blueprint) -> Tuple[cp.Model, ModelVariables]:
    resources = cp.intvar(0, MAX_N_RESOURCES, shape=(N_ROUNDS, 4), name='resources')
    robots = cp.intvar(0, MAX_N_ROBOTS, shape=(N_ROUNDS, 4), name='robots')
    constructions = cp.intvar(0, 1, shape=(N_ROUNDS, 4), name='constructions')

    model = cp.Model(maximize=resources[-1, GEODE_IDX])

    # Initial conditions.
    resources[0, :] = np.array([0, 0, 0, 0])
    robots[0, :] = np.array([1, 0, 0, 0])

    for round in range(1, N_ROUNDS):

        # Can constuct one robot a minute.
        model += (
            constructions[round, ORE_IDX]
            + constructions[round, CLAY_IDX]
            + constructions[round, OBSIDIAN_IDX]
            + constructions[round, GEODE_IDX]
            <= 1
        )

        # When we construct a robot, we have one more available on the next round.
        for j in range(4):
            model += (robots[round, j] == robots[round - 1, j] + constructions[round - 1, j])

        # Can't spend more of each resource type than we have available.
        model += (
            resources[round, ORE_IDX] >=
                constructions[round, ORE_IDX] * blueprint.ore.ore
                + constructions[round, CLAY_IDX] * blueprint.clay.ore
                + constructions[round, OBSIDIAN_IDX] * blueprint.obsidian.ore
                + constructions[round, GEODE_IDX] * blueprint.geode.ore
        )
        model += (
            resources[round, CLAY_IDX] >=
                constructions[round, OBSIDIAN_IDX] * blueprint.obsidian.clay
        )
        model += (
            resources[round, OBSIDIAN_IDX] >=
                constructions[round, GEODE_IDX] * blueprint.geode.obsidian
        )

        # Each round we:
        #  - Lose any spent resources
        #  - Get one additional resource per robot that makes that resource
        model += (
            resources[round, ORE_IDX] ==
              resources[round - 1, ORE_IDX]
                - constructions[round - 1, ORE_IDX] * blueprint.ore.ore
                - constructions[round - 1, CLAY_IDX] * blueprint.clay.ore
                - constructions[round - 1, OBSIDIAN_IDX] * blueprint.obsidian.ore
                - constructions[round - 1, GEODE_IDX] * blueprint.geode.ore
                + robots[round - 1, ORE_IDX]
        )
        model += (
            resources[round, CLAY_IDX] ==
              resources[round - 1, CLAY_IDX]
                - constructions[round - 1, OBSIDIAN_IDX] * blueprint.obsidian.clay
                + robots[round - 1, CLAY_IDX]
        )
        model += (
            resources[round, OBSIDIAN_IDX] ==
              resources[round - 1, OBSIDIAN_IDX]
                - constructions[round - 1, GEODE_IDX] * blueprint.geode.obsidian
                + robots[round - 1, OBSIDIAN_IDX]
        )
        model += (
            resources[round, GEODE_IDX] ==
              resources[round - 1, GEODE_IDX]
                + robots[round - 1, GEODE_IDX]
        )

    return model, ModelVariables(resources, robots, constructions)


if __name__ == '__main__':
    data = get_data(day=19, year=2022).strip()
    blueprints = parse_data(data)

    # blueprint = Blueprint(
    #     id=1,
    #     ore=RobotCost(4, 0, 0),
    #     clay=RobotCost(2, 0, 0),
    #     obsidian=RobotCost(3, 14, 0),
    #     geode=RobotCost(3, 0, 7)
    # )
    # blueprint = Blueprint(
    #     id=1,
    #     ore=RobotCost(2, 0, 0),
    #     clay=RobotCost(3, 0, 0),
    #     obsidian=RobotCost(3, 8, 0),
    #     geode=RobotCost(3, 0, 12)
    # )

    optimals: Dict[BlueprintId, int] = {}
    for blueprint in blueprints:
        model, vars = make_model(blueprint=blueprint)
        model.solve()
        max_geodes = model.objective_value()
        print(f"Maximum geodes for blueprint {blueprint.id} is {max_geodes}")
        optimals[blueprint.id] = max_geodes
    total_quality = sum(id * optim for id, optim in optimals.items())
    print(f"The total quality of all the blueprints is {total_quality}")