import string

from unidecode import unidecode


def get_lines(filename):
    with open(filename, encoding='utf-8') as f:
        for line in f:
            yield line.strip()


rules = [
    # a length of at least 4 and at most 12
    lambda line: 4 <= len(line) <= 12,
    # at least one digit
    lambda line: any(ch in line for ch in string.digits),
    # at least one uppercase letter (with or without accents, examples: A or Ż)
    lambda line: any(ch in unidecode(line) for ch in string.ascii_uppercase),
    # at least one lowercase letter (with or without accents, examples: a or ŷ)
    lambda line: any(ch in unidecode(line) for ch in string.ascii_lowercase),
    # at least one character that is outside the standard 7-bit ASCII character set (examples: Ű, ù or ř)
    lambda line: any(ord(ch) > 0b1111111 for ch in line),
]


def check_line(line):
    for rule in rules:
        if not rule(line):
            return False
    return True


def solve(filename):
    return [check_line(line) for line in get_lines(filename)].count(True)


if __name__ == '__main__':
    assert solve('sample03.txt') == 2
    print(solve('day03.txt'))
