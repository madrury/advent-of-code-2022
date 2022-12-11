from dataclasses import dataclass
from typing import List, Callable, Dict


WORRY_MODULUS_LCM = 11 * 3 * 5 * 7 * 19 * 2 * 13 * 17

Worry = int
MonkeyId = int


@dataclass
class Item:
    worry: int

    @staticmethod
    def from_list(lst: List[int]) -> List['Item']:
        return [Item(n) for n in lst]


class Monkey:

    def __init__(
        self,
        items: List[Item],
        operation: Callable[[Worry], Worry],
        test: Callable[[Worry], MonkeyId]
    ):
        self.id = id
        self.items = items
        self.operation = operation
        self.test = test
        self.n_inspections = 0


def monkeys() -> Dict[MonkeyId, Monkey]:
    return {
        0: Monkey(
            items = Item.from_list([56, 52, 58, 96, 70, 75, 72]),
            operation = lambda w: w * 17,
            test = lambda w: 2 if w % 11 == 0 else 3
        ),
        1: Monkey(
            items = Item.from_list([75, 58, 86, 80, 55, 81]),
            operation = lambda w: w + 7,
            test = lambda w: 6 if w % 3 == 0 else 5
        ),
        2: Monkey(
            items = Item.from_list([73, 68, 73, 90]),
            operation = lambda w: w * w,
            test = lambda w: 1 if w % 5 == 0 else 7
        ),
        3: Monkey(
            items = Item.from_list([72, 89, 55, 51, 59]),
            operation = lambda w: w + 1,
            test = lambda w: 2 if w % 7 == 0 else 7
        ),
        4: Monkey(
            items = Item.from_list([76, 76, 91]),
            operation = lambda w: w * 3,
            test = lambda w: 0 if w % 19 == 0 else 3
        ),
        5: Monkey(
            items = Item.from_list([88]),
            operation = lambda w: w + 4,
            test = lambda w: 6 if w % 2 == 0 else 4
        ),
        6: Monkey(
            items = Item.from_list([64, 63, 56, 50, 77, 55, 55, 86]),
            operation = lambda w: w + 8,
            test = lambda w: 4 if w % 13 == 0 else 0
        ),
        7: Monkey(
            items = Item.from_list([79, 58]),
            operation = lambda w: w + 6,
            test = lambda w: 1 if w % 17 == 0 else 5
        ),
    }


class MonkeyBusiness:

    def __init__(
        self,
        monkeys: List[Monkey],
        n_rounds=20,
        dividethree: bool = False,
        modulolcm: bool = False,
    ):
        self.monkeys = monkeys
        self.remaining_rounds = n_rounds
        self.dividethree = dividethree
        self.modlulolcm = modulolcm

    def play(self):
        while self.remaining_rounds > 0:
            for monkey in self.monkeys.values():
                self.monkey_around(monkey)
            self.remaining_rounds -= 1

    def monkey_around(self, monkey: Monkey):
        for item in monkey.items:
            monkey.n_inspections += 1
            item.worry = monkey.operation(item.worry)
            if self.dividethree:
                item.worry //= 3
            if self.modlulolcm:
                item.worry %= WORRY_MODULUS_LCM
            self.monkeys[monkey.test(item.worry)].items.append(item)
        monkey.items = []


if __name__ == '__main__':
    business = MonkeyBusiness(
        monkeys=monkeys(),
        n_rounds=20,
        dividethree=True
    )
    business.play()
    inspections = {
        mid: monkey.n_inspections for mid, monkey in business.monkeys.items()
    }
    print("After 20 rounds, each monkey has monkeyed around:")
    print(inspections)

    business = MonkeyBusiness(
        monkeys=monkeys(),
        n_rounds=10_000,
        dividethree=False,
        modulolcm=True
    )
    business.play()
    inspections = {
        mid: monkey.n_inspections for mid, monkey in business.monkeys.items()
    }
    print("After 10000 rounds, each monkey has monkeyed around:")
    print(inspections)