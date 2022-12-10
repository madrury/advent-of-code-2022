from aocd import get_data # type: ignore
from enum import Enum
from dataclasses import dataclass
from itertools import pairwise
from typing import List, Tuple

class Signal(Enum):
    FINISHED = 0
    BLOCKING = 1

class Instruction:
    def tick(self) -> Signal:
        self.counter -= 1
        if self.counter == 0:
            return Signal.FINISHED
        return Signal.BLOCKING

@dataclass
class NoOp(Instruction):
    counter: int = 1

@dataclass
class Add(Instruction):
    dx: int
    counter: int = 2

Program = List[Instruction]


class CRT:

    def __init__(self, width: int = 40, height: int = 6):
        self.width = width
        self.height = height
        self.display = [['.'] * width for _ in range(height)]
        self.beampos = 0

    def render(self, spritepos: int):
        beamx, beamy = (
            self.beampos % self.width,
            (self.beampos // self.width) % self.height
        )
        if abs(beamx - spritepos) <= 1:
            self.display[beamy][beamx] = '#'

    def show(self):
        return '\n'.join([''.join(row) for row in self.display])

    def tick(self):
        self.beampos += 1


class Machine:

    def __init__(self, program: Program):
        self.program = program
        self._ixptr = 0
        self.x = 1
        self.cycle = 0
        self.signal: List[int] = []
        self.crt = CRT()

    def execute(self):
        while self._ixptr < len(self.program):
            self.tick(self.program[self._ixptr])

    def tick(self, ix: Instruction):
        self.crt.render(spritepos=self.x)
        self.crt.tick()
        match ix.tick(), ix:
            case Signal.BLOCKING, _:
                self.signal.append(self.x)
            case Signal.FINISHED, Add(dx, _):
                self.signal.append(self.x)
                self.x += dx
                self._ixptr += 1
            case Signal.FINISHED, NoOp(_):
                self.signal.append(self.x)
                self._ixptr += 1

    def signal_strength(self, idxs: List[int]) -> int:
        return sum(idx * self.signal[idx - 1] for idx in idxs)


def parse_data(data: str) -> Program:
    program: Program = []
    for line in data.split('\n'):
        match line.strip().split(' '):
            case 'noop',:
                program.append(NoOp())
            case 'addx', n:
                program.append(Add(int(n)))
            case x:
                print(x)
    return program


if __name__ == '__main__':
    data = get_data(day=10, year=2022)
    program = parse_data(data)

    machine = Machine(program)
    machine.execute()
    ss = machine.signal_strength([20, 60, 100, 140, 180, 220])
    print(f"The signal strength is {ss}")

    print(machine.crt.show())