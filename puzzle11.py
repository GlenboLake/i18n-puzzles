def load(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()


greek_upper = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
greek_lower = 'αβγδεζηθικλμνξοπρστυφχψω'


def normalize_sigma(text):
    return text.replace('ς', 'σ')


# Copy text straight from puzzle website, but just use normal sigma
odysseus = {
    normalize_sigma(o) for o in
    ('Οδυσσευς', 'Οδυσσεως', 'Οδυσσει', 'Οδυσσεα', 'Οδυσσευ')
}


def shift(text, n):
    shifted_upper = greek_upper[n:] + greek_upper[:n]
    shifted_lower = greek_lower[n:] + greek_lower[:n]
    mapping = dict(zip(
        [*greek_upper, *greek_lower],
        [*shifted_upper, *shifted_lower]
    ))
    return ''.join(
        mapping.get(ch, ch)
        for ch in normalize_sigma(text)
    )


def find_odysseus(line):
    for i in range(1, 25):
        shifted = shift(line, i)
        if any(o in shifted for o in odysseus):
            return i
    return 0


def solve(filename):
    total = 0
    for line in load(filename):
        total += find_odysseus(line)
    return total


if __name__ == '__main__':
    assert solve('sample11.txt') == 19
    print(solve('day11.txt'))