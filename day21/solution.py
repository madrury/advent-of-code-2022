from aocd import get_data # type: ignore
from typing import List, Tuple, Dict, Callable, Optional, Literal
from dataclasses import dataclass
from enum import Enum

ROOT = "root"

MonkeyId = str
Operation = Literal['+', '-', '*', '/']
VarName = str
MonkeyNamespace = Dict[MonkeyId, 'Monkey']
ValueNamespace = Dict[MonkeyId, int]

class Result(Enum):
    SUCCESS =0
    FAILURE = 1


class Monkey:

    def __init__(
        self,
        id: MonkeyId,
        operation: Operation,
        left: VarName,
        right: VarName
    ):
        self.id = id
        self.operation = operation
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Monkey({self.id}, {self.left} {self.operation} {self.right})"

    def evaluate(self, namespace: ValueNamespace) -> Result:
        if self.left not in namespace or self.right not in namespace:
            return Result.FAILURE
        left, right = namespace[self.left], namespace[self.right]
        match self.operation, left, right:
            case '+', x, y:
                namespace[self.id] = x + y
            case '-', x, y:
                namespace[self.id] = x - y
            case '*', x, y:
                namespace[self.id] = x * y
            case '/', x, y:
                namespace[self.id] = x // y
        return Result.SUCCESS


def parse_data(data: str) -> Tuple[MonkeyNamespace, ValueNamespace]:
    monkeyspace: MonkeyNamespace = {}
    valuespace: ValueNamespace = {}
    for line in data.split('\n'):
        id, rhs = line.split(': ')
        if rhs.isnumeric():
            valuespace[id] = int(rhs)
        else:
            left, operation, right = rhs[0:4], rhs[5], rhs[7:11]
            monkeyspace[id] = Monkey(id, operation, left, right)
    return monkeyspace, valuespace


def evaluate(monkeyspace: MonkeyNamespace, valuespace: ValueNamespace) -> int:
    remaining = set(monkeyspace)
    while remaining:
        successes: List[MonkeyId] = {
            id for id, monkey in monkeyspace.items()
            if id in remaining and monkey.evaluate(valuespace) == Result.SUCCESS
        }
        remaining = remaining - successes
    return valuespace[ROOT]



if __name__ == '__main__':
    data = get_data(day=21, year=2022).strip()

    monkeyspace, valuespace = parse_data(data)
    # print(evaluate(monkeyspace, valuespace.copy()))

    monkeyspace[ROOT].operation = '-'
    for input in range(10000):
        vs = valuespace.copy()
        vs['humn'] = input
        result = evaluate(monkeyspace, vs)
        print(f"For input {input} root yells {result}.")
        if result == 0:
            break
