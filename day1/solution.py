from aocd import get_data # type: ignore
from collections import Counter

from typing import Optional, List, Mapping

ElfId = int
CalorieList = List[Optional[int]]
CalorieCounter = Counter[int]

def parse_data(data: str) -> CalorieList:
    return [int(x.strip()) if x else None for x in data.split('\n')]

def accumulate(xs: CalorieList) -> CalorieCounter:
    counter: CalorieCounter = Counter()
    elfid: ElfId = 0
    for x in xs:
        if x:
            counter[elfid] += x
        else:
            elfid += 1
    return counter


if __name__ == '__main__':
    data = get_data(day=1, year=2022)
    counter = accumulate(parse_data(data))
    eid, calories = counter.most_common(1)[0]
    print(f'Elf {eid} has the most calories, with {calories} total.')

    top3calories = sum(x for _, x in counter.most_common(3))
    print(f'The top 3 most caloried elves have {top3calories} total calories.')