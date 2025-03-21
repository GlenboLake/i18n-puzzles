import operator
import re
from fractions import Fraction
from functools import reduce
from itertools import pairwise

digits: dict[str, int] = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
}
powers: dict[str, int] = {
    '十': 10,
    '百': 100,
    '千': 1000,
}
myriads: dict[str, int] = {
    '万': 10_000,
    '億': 10_000 ** 2
}

digit_re = f'[{''.join(digits)}]'
power_re = f'[{''.join(powers)}]'
myriad_re = f'[{''.join(myriads)}]'
number_regex = re.compile(f'{digit_re}{power_re}|{digit_re}|{power_re}|{myriad_re}')

values: dict[str, int] = {
    **digits,
    **powers,
    **myriads,
}
shaku = Fraction(10, 33)
units = {
    '尺': 1 * shaku,
    '間': 6 * shaku,
    '丈': 10 * shaku,
    '町': 360 * shaku,
    '里': 12960 * shaku,
    '毛': 1 * shaku / 10000,
    '厘': 1 * shaku / 1000,
    '分': 1 * shaku / 100,
    '寸': 1 * shaku / 10,
}


def parse_japanese_number(n):
    bits = number_regex.findall(n)
    total = partial = 0
    for bit in bits:
        if bit in myriads:
            total += partial * myriads[bit]
            partial = 0
        else:
            value = reduce(operator.mul, [values[b] for b in bit])
            partial += value
    total += partial
    return total


number_samples = [
    (300, '三百'),
    (321, '三百二十一'),
    (4_000, '四千'),
    (50_000, '五万'),
    (99_999, '九万九千九百九十九'),
    (420_042, '四十二万四十二'),
    (987_654_321, '九億八千七百六十五万四千三百二十一'),
]

for arabic, japanese in number_samples:
    assert (parsed := parse_japanese_number(japanese)) == arabic, f'{parsed} != {arabic}'


def solve(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    total = Fraction(0)
    for line in lines:
        a, b = line.split(' × ')
        value = parse_japanese_number(a[:-1]) * units[a[-1]] * parse_japanese_number(b[:-1]) * units[b[-1]]
        total += value
    return total


if __name__ == '__main__':
    assert solve('sample14.txt') == 2177741195
    print(solve('day14.txt'))
