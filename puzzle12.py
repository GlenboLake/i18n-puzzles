import string
import unicodedata
from itertools import count

from unidecode import unidecode


def load(filename):
    def parse_line(line):
        name, number = line.split(': ')
        return name, int(number)

    with open(filename) as f:
        return list(map(parse_line, f.read().splitlines()))


alphabet = dict(zip(string.ascii_uppercase, count(1)))
alphabet['Å'] = 27
alphabet['Ä'] = alphabet['Æ'] = 28
alphabet['Ö'] = alphabet['Ø'] = 29

# Normalize unicode in lookup
alphabet = {
    unicodedata.normalize('NFC', k): v
    for k, v in alphabet.items()
}


def english_key(value):
    name, _ = value
    decoded = unidecode(name).upper()
    return [ch for ch in decoded if ch in string.ascii_uppercase]


def swedish_key(value):
    name, _ = value
    indices = [
        alphabet.get(letter) or alphabet.get(unidecode(letter)) or f'WHERE IS {letter}?'
        for letter in unicodedata.normalize('NFC', name).upper()
        if letter.isalnum()
    ]
    return indices


def dutch_key(value):
    name, number = value
    first_upper = next(i for i, ch in enumerate(name) if ch == ch.upper() and ch.isalnum())
    return english_key((name[first_upper:], number))


def solve(filename):
    names = load(filename)
    middle_index = len(names) // 2
    result = 1
    for sort_key in (english_key, swedish_key, dutch_key):
        # print(sort_key.__name__)
        sort_names = sorted(names, key=sort_key)
        # for i, (name, value) in enumerate(sort_names):
        #     if i == middle_index:
        #         print('* ', end='')
        #     else:
        #         print('  ', end='')
        #     print(name, value)
        result *= sort_names[middle_index][-1]
    return result


if __name__ == '__main__':
    assert solve('sample12.txt') == 1885816494308838
    print(solve('day12.txt'))