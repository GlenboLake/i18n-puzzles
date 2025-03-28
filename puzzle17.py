from itertools import pairwise
from textwrap import wrap
from typing import Iterable, Sequence

DEBUG = False

INVALID = chr(65533)  # codepoint inserted from bytes.decode(errors='replace')
CHUNK_WIDTH = 16  # Constant in input
EMPTY = ord(' ')
X_MARKS_THE_SPOT = chr(9587)

top_left = '╔'.encode()
top_right = '╗'.encode()
bottom_left = '╚'.encode()
bottom_right = '╝'.encode()
vertical_edge = '║'.encode()
horizontal_edge = '═'.encode()
pad = ' '.encode()  # Used for padding if any rows start from the right

top = set('╔╗═-')
bottom = set('╚╝═-')
left = set('╔╚║|')
right = set('╗╝║|')

type Chunk = Sequence[bytes]


def load(filename: str) -> list[Chunk]:
    with open(filename) as f:
        def parse_chunk(lines):
            return tuple(
                bytes([
                    int(byte, 16)
                    for byte in wrap(line, 2)
                ])
                for line in lines
            )

        return [
            parse_chunk(ch.splitlines())
            for ch in f.read().split('\n\n')
        ]


def check_line(line: str):
    for bit in line.split():
        # Replacement character at the start or end of a chunk isn't a problem
        if INVALID in bit.strip(INVALID):
            return False
    return True


def check(lines):
    if DEBUG:
        print('Checking map:')
        print_map(lines)
    try:
        printable: list[str] = [
            line.decode(errors='replace')
            for line in lines
        ]
        assert all(map(check_line, printable)), 'Invalid character in middle of a line'
        assert set(printable[0]) - {' '} <= top, 'Non-top characters in first line'
        assert set(printable[-1]) - {' '} <= bottom, 'Non-bottom characters in last line'
        assert set(line[0] for line in printable) - {' '} <= left, 'Non-left characters in first column'
        assert set(line[-1] for line in printable) - {' '} <= right, 'Non-right characters in last column'
    except AssertionError as e:
        if DEBUG:
            print('Failure:', e)
        return False
    return True


def place(piece: Iterable[bytes], treasure_map: list[bytes], row: int, col: int) -> list[bytes]:
    new_map = treasure_map.copy()
    for i, line in enumerate(piece, start=row):
        map_row = list(new_map[i])
        map_row[col:col + len(line)] = list(line)
        new_map[i] = bytes(map_row)
    return new_map


def solve(filename: str):
    chunks = load(filename)
    if DEBUG:
        print(f'Piecing together map with {len(chunks)} pieces')
    start = next(chunk for chunk in chunks if chunk[0].startswith(top_left))
    map_width_in_chunks = sum(1 for chunk in chunks if horizontal_edge in chunk[0])
    map_width = map_width_in_chunks * CHUNK_WIDTH
    map_height = sum(len(chunk) for chunk in chunks) // map_width_in_chunks
    empty_map = [
        bytes([EMPTY] * map_width)
        for _ in range(map_height)
    ]
    treasure_map = place(start, empty_map, 0, 0)
    pieces = set(chunks.copy()) - {start}
    check(treasure_map)
    solution = [
        line.decode()
        for line in try_solve(treasure_map, pieces, map_width)
    ]
    if DEBUG:
        print('\n'.join(solution).replace(X_MARKS_THE_SPOT, f'\033[91m{X_MARKS_THE_SPOT}\033[0m'))
    return next(
        line.index(X_MARKS_THE_SPOT) * i
        for i, line in enumerate(solution)
        if X_MARKS_THE_SPOT in line
    )


def print_map(treasure_map: list[bytes]):
    treasure_map = [line.decode(errors='replace') for line in treasure_map]
    while not treasure_map[-1]:
        treasure_map.pop()
    print('*' * (len(treasure_map[0]) + 2))
    for line in treasure_map:
        print('*' + line + '*')
    print('*' * (len(treasure_map[0]) + 2))


def try_solve(
        treasure_map: list[bytes],
        pieces: set[Chunk],
        map_width: int,
) -> list[bytes] | None:
    """
    Iteratively try to piece the map together

    :param treasure_map: The part of the map already pieced together
    :param pieces: Pieces to assemble
    :param map_width: Edge width of map, in bytes
    :return: The completed treasure map
    """
    if not pieces:
        return treasure_map

    # Find first incomplete row
    r = next(
        i
        for i, line in enumerate(treasure_map)
        if b' ' in line
    )
    c = next(
        i if b == EMPTY else i - CHUNK_WIDTH
        for i, (a, b) in enumerate(pairwise(treasure_map[r]), start=1)
        if (a == EMPTY) ^ (b == EMPTY)
    )

    for piece in pieces:
        # Place the piece, then check it. If it works, keep trying. If not, try the next piece
        if check(new_map := place(piece, treasure_map, r, c)):
            return try_solve(new_map, pieces - {piece}, map_width)

    return None


if __name__ == '__main__':
    # print(solve('sample17.txt'))
    print(solve('day17.txt'))
