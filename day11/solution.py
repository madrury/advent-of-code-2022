from math import lcm
from dataclasses import dataclass
from typing import List, Callable, Dict

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
        # Monkey 0:
        #   Starting items: 56, 52, 58, 96, 70, 75, 72
        #   Operation: new = old * 17
        #   Test: divisible by 11
        #     If true: throw to monkey 2
        #     If false: throw to monkey 3
        0: Monkey(
            items = Item.from_list([56, 52, 58, 96, 70, 75, 72]),
            operation = lambda w: w * 17,
            test = lambda w: 2 if w % 11 == 0 else 3
        ),
        # Monkey 1:
        #   Starting items: 75, 58, 86, 80, 55, 81
        #   Operation: new = old + 7
        #   Test: divisible by 3
        #     If true: throw to monkey 6
        #     If false: throw to monkey 5
        1: Monkey(
            items = Item.from_list([75, 58, 86, 80, 55, 81]),
            operation = lambda w: w + 7,
            test = lambda w: 6 if w % 3 == 0 else 5
        ),
        # Monkey 2:
        #   Starting items: 73, 68, 73, 90
        #   Operation: new = old * old
        #   Test: divisible by 5
        #     If true: throw to monkey 1
        #     If false: throw to monkey 7
        2: Monkey(
            items = Item.from_list([73, 68, 73, 90]),
            operation = lambda w: w * w,
            test = lambda w: 1 if w % 5 == 0 else 7
        ),
        # Monkey 3:
        #   Starting items: 72, 89, 55, 51, 59
        #   Operation: new = old + 1
        #   Test: divisible by 7
        #     If true: throw to monkey 2
        #     If false: throw to monkey 7
        3: Monkey(
            items = Item.from_list([72, 89, 55, 51, 59]),
            operation = lambda w: w + 1,
            test = lambda w: 2 if w % 7 == 0 else 7
        ),
        # Monkey 4:
        #   Starting items: 76, 76, 91
        #   Operation: new = old * 3
        #   Test: divisible by 19
        #     If true: throw to monkey 0
        #     If false: throw to monkey 3
        4: Monkey(
            items = Item.from_list([76, 76, 91]),
            operation = lambda w: w * 3,
            test = lambda w: 0 if w % 19 == 0 else 3
        ),
        # Monkey 5:
        #   Starting items: 88
        #   Operation: new = old + 4
        #   Test: divisible by 2
        #     If true: throw to monkey 6
        #     If false: throw to monkey 4
        5: Monkey(
            items = Item.from_list([88]),
            operation = lambda w: w + 4,
            test = lambda w: 6 if w % 2 == 0 else 4
        ),
        # Monkey 6:
        #   Starting items: 64, 63, 56, 50, 77, 55, 55, 86
        #   Operation: new = old + 8
        #   Test: divisible by 13
        #     If true: throw to monkey 4
        #     If false: throw to monkey 0
        6: Monkey(
            items = Item.from_list([64, 63, 56, 50, 77, 55, 55, 86]),
            operation = lambda w: w + 8,
            test = lambda w: 4 if w % 13 == 0 else 0
        ),
        # Monkey 7:
        #   Starting items: 79, 58
        #   Operation: new = old + 6
        #   Test: divisible by 17
        #     If true: throw to monkey 1
        #     If false: throw to monkey 5
        7: Monkey(
            items = Item.from_list([79, 58]),
            operation = lambda w: w + 6,
            test = lambda w: 1 if w % 17 == 0 else 5
        ),
    }

WORRY_MODULUS_LCM = 11 * 3 * 5 * 7 * 19 * 2 * 13 * 17

class MonkeyBusiness:

    def __init__(
        self,
        monkeys: List[Monkey],
        wupdate: Callable[[Worry], Worry],
        reduce: bool = False,
        n_rounds=20,

    ):
        self.monkeys = monkeys
        self.wupdate = wupdate
        self.reduce = reduce
        self.remaining_rounds = n_rounds

    def play(self):
        while self.remaining_rounds > 0:
            for monkey in self.monkeys.values():
                for item in monkey.items:
                    monkey.n_inspections += 1
                    item.worry = self.wupdate(monkey.operation(item.worry))
                    if self.reduce:
                        item.worry %= WORRY_MODULUS_LCM
                    self.monkeys[monkey.test(item.worry)].items.append(item)
                monkey.items = []
            self.remaining_rounds -= 1


if __name__ == '__main__':
    ms = monkeys()
    business = MonkeyBusiness(
        monkeys=ms,
        n_rounds=20,
        wupdate=lambda w: w // 3
    )
    business.play()
    inspections = {
        mid: monkey.n_inspections for mid, monkey in business.monkeys.items()
    }
    print(inspections)

    ms = monkeys()
    business = MonkeyBusiness(
        monkeys=ms,
        n_rounds=10_000,
        wupdate=lambda w: w,
        reduce=True
    )
    business.play()
    inspections = {
        mid: monkey.n_inspections for mid, monkey in business.monkeys.items()
    }
    print(inspections)