from aocd import get_data  # type: ignore
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

Snafu = str
Base = int
Numeral = int
Digits = List[Numeral]

def encode(n: int, base: Base) -> Digits:
    if n == 0:
        return [0]
    digits: Digits = []
    while n:
        digits.append(n % base)
        n //= base
    return digits

def decode(digits: Digits, base: Base) -> int:
    placevalue, n = 1, 0
    for digit in digits:
        n += digit * placevalue
        placevalue *= base
    return n

def carry(digits: Digits, base: Base, numerals: List[Numeral]) -> Digits:
    result: Digits = []
    # Add an extraneous zero to handle the final carry.
    digits.append(0)
    for position, numeral in enumerate(digits):
        if numeral in numerals:
            result.append(numeral)
            continue
        while numeral not in numerals:
            numeral -= base
            digits[position + 1] += 1
        result.append(numeral)
    return result

def to_snafu(n: int) -> Snafu:
    base5digits = encode(n, 5)
    snafudigits = carry(base5digits, 5, {2, 1, 0, -1, -2})
    return digits_to_snafu(snafudigits)


SNAFU_TO_DIGIT_LOOKUP = {'2': 2, '1': 1, '0': 0, '-': -1, '=': -2}
DIGIT_TO_SNAFU_LOOKUP = {2: '2', 1: '1', 0: '0', -1: '-', -2: '='}

def digits_to_snafu(digits: Digits) -> Snafu:
    snafu = [DIGIT_TO_SNAFU_LOOKUP[d] for d in digits]
    return ''.join(snafu[::-1]).lstrip('0')

def snafu_to_digits(snafu: Snafu) -> Digits:
    return [SNAFU_TO_DIGIT_LOOKUP[c] for c in snafu][::-1]


def parse_data(data: str) -> List[Digits]:
    digital: List[Digits] = []
    for line in data.split('\n'):
        digital.append(snafu_to_digits(line.strip()))
    return digital


if __name__ == "__main__":
    data = get_data(day=25, year=2022)

    digital = parse_data(data)
    s = sum(decode(digits, 5) for digits in digital)
    print(f"SNAFU: {to_snafu(s)}")
