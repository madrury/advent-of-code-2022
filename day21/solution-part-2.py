from aocd import get_data # type: ignore
from typing import Dict, Tuple
import z3

MonkeyId = str

def make_model(data: str) -> Tuple[z3.Solver, Dict[MonkeyId, z3.Int]]:
    variables: Dict[MonkeyId, z3.Int] = {}
    model = z3.Solver()

    for line in data.split('\n'):
        id, _ = line.split(': ')
        variables[id] = z3.Int(id)

    for line in data.split('\n'):
        print(line)
        id, rhs = line.split(': ')
        if rhs.isnumeric():
            if id == 'humn' or id == 'root':
                continue
            else:
                model.add(variables[id] == int(rhs))

        else:
            left, operation, right = rhs[0:4], rhs[5], rhs[7:11]
            if id == 'humn':
                continue
            if id == 'root':
                model.add(variables[left] - variables[right] == 0)
                continue

            match operation, left, right:
                case '+', left, right:
                    model.add(variables[id] == variables[left] + variables[right])
                case '-', left, right:
                    model.add(variables[id] + variables[right] == variables[left])
                case '*', left, right:
                    model += (variables[id] == variables[left] * variables[right])
                case '/', left, right:
                    model += (variables[id] * variables[right] == variables[left])

    return model, variables


if __name__ == '__main__':
    data = get_data(day=21, year=2022).strip()

    model, variables = make_model(data)
    print(model)
    model.check()
    print(model.model().eval(variables['humn']))