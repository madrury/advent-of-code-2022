from aocd import get_data # type: ignore
from typing import Optional
from collections import deque

Position = int

def find_repeats(data: str, markerlen: int) -> Optional[Position]:
    buffer: deque[str] = deque(data[:markerlen], maxlen=markerlen)
    for idx, chr in enumerate(data, start=markerlen):
        buffer.append(chr)
        if len(set(buffer)) == markerlen:
            return idx - markerlen + 1
    return None

if __name__ == '__main__':
    data = get_data(day=6, year=2022)

    soppos = find_repeats(data, markerlen=4)
    print(f"The first start-of-packet marker for length 4 packets is at position {soppos}")

    soppos = find_repeats(data, markerlen=14)
    print(f"The first start-of-packet marker for length 14 packets is at position {soppos}")