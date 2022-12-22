from aocd import get_data # type: ignore
from typing import List, Tuple, Dict
import numpy as np

DATA_IDX, POSITIONAL_IDX = 0, 1

Idx = int

def parse_data(data: str) -> np.array:
    return np.array([int(x) for x in data.split('\n')], dtype=object)

def stack_idx(data: np.array) -> np.array:
    return np.vstack([data, np.arange(len(data), dtype=object)])

def mix(stacked: np.array) -> np.array:
    for idx in range(stacked.shape[1]):
        position = np.where(stacked[POSITIONAL_IDX, :] == idx)[0][0]
        delta = stacked[DATA_IDX, position]
        if delta == 0:
            continue
        stacked = mixonce(stacked, position, delta)
    return stacked

def mixonce(stacked: np.array, position: int, delta: int):
    col = stacked[:, position]
    insertposition = (position + delta) % (stacked.shape[1] - 1)
    removed = np.delete(stacked, position, axis=1)
    return np.insert(removed, insertposition, col, axis=1)

def grove_coordinates(stacked: np.array) -> int:
    array = stacked[DATA_IDX, :]
    N = len(array)
    idxofzero = np.where(array == 0)[0][0]
    idxer = (np.array([1000, 2000, 3000]) + idxofzero) % N
    return sum(array[idxer])



if __name__ == '__main__':
    data = get_data(day=20, year=2022).strip()
    array = parse_data(data)

    mixed = mix(stack_idx(array))
    print(f"The incorrect grove coordinates are: {grove_coordinates(mixed)}")

    ENCRYPTION_KEY = 811589153
    decrypted = stack_idx(array * ENCRYPTION_KEY)
    for _ in range(10):
        decrypted = mix(decrypted)
    print(f"The correct grove coordinates are: {grove_coordinates(decrypted)}")
