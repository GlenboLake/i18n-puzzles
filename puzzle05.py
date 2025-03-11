def get_park(filename):
    with open(filename) as f:
        return f.read().splitlines()


poop = '💩'


def solve(filename):
    park = get_park(filename)
    return sum(1 for i, line in enumerate(park) if line[2 * i % len(line)] == poop)


if __name__ == '__main__':
    assert solve('sample05.txt') == 2
    print(solve('day05.txt'))