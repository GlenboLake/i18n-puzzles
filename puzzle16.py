import curses
from _curses import window  # noqa just for type hints
from collections import defaultdict, deque
from typing import NamedTuple


class Pipe(NamedTuple):
    chr: str
    next: str
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0
    max_rot: int = 4


CELLS = {
    '═': Pipe('═', '║', left=2, right=2, max_rot=2),
    '║': Pipe('║', '═', up=2, down=2, max_rot=2),
    '─': Pipe('─', '│', left=1, right=1, max_rot=2),
    '│': Pipe('│', '─', up=1, down=1, max_rot=2),
    '╔': Pipe('╔', '╗', right=2, down=2),
    '╗': Pipe('╗', '╝', down=2, left=2),
    '╝': Pipe('╝', '╚', left=2, up=2),
    '╚': Pipe('╚', '╔', up=2, right=2),
    '┌': Pipe('┌', '┐', right=1, down=1),
    '┐': Pipe('┐', '┘', down=1, left=1),
    '┘': Pipe('┘', '└', left=1, up=1),
    '└': Pipe('└', '┌', up=1, right=1),
    '╦': Pipe('╦', '╣', right=2, down=2, left=2),
    '╣': Pipe('╣', '╩', down=2, left=2, up=2),
    '╩': Pipe('╩', '╠', left=2, up=2, right=2),
    '╠': Pipe('╠', '╦', up=2, right=2, down=2),
    '┬': Pipe('┬', '┤', right=1, down=1, left=1),
    '┤': Pipe('┤', '┴', down=1, left=1, up=1),
    '┴': Pipe('┴', '├', left=1, up=1, right=1),
    '├': Pipe('├', '┬', up=1, right=1, down=1),
    '╤': Pipe('╤', '╢', right=2, down=1, left=2),
    '╢': Pipe('╢', '╧', down=2, left=1, up=2),
    '╧': Pipe('╧', '╟', left=2, up=1, right=2),
    '╟': Pipe('╟', '╤', up=2, right=1, down=2),
    '╥': Pipe('╥', '╡', right=1, down=2, left=1),
    '╡': Pipe('╡', '╨', down=1, left=2, up=1),
    '╨': Pipe('╨', '╞', left=1, up=2, right=1),
    '╞': Pipe('╞', '╥', up=1, right=2, down=1),
    '╪': Pipe('╪', '╫', up=1, down=1, left=2, right=2, max_rot=2),
    '╫': Pipe('╫', '╪', up=2, down=2, left=1, right=1, max_rot=2),
    '╬': Pipe('╬', '╬', up=2, down=2, left=2, right=2, max_rot=1),
    '┼': Pipe('┼', '┼', up=1, down=1, left=1, right=1, max_rot=1),
}


def load_puzzle(filename):
    with open(filename, encoding='CP437') as f:
        grid = [
            list(row.strip('\n'))
            for row in f
        ]

    return grid


CURSOR = 1 << 0
DEFAULT = 1 << 1
WATER = 1 << 2
OVERFLOW = 1 << 3
IGNORE = 1 << 4


def init_colors():
    foreground = {
        DEFAULT: curses.COLOR_WHITE,
        WATER: curses.COLOR_BLUE,
        OVERFLOW: curses.COLOR_RED,
        IGNORE: curses.COLOR_BLACK,
    }
    background = {
        0: curses.COLOR_BLACK,
        CURSOR: curses.COLOR_GREEN,
    }
    for fg in foreground:
        for bg in background:
            curses.init_pair(fg | bg, foreground[fg], background[bg])


def solve(filename):
    grid = load_puzzle(filename)
    height = len(grid)
    width = len(grid[0])
    # For convenience, hard-code size of actual grid
    input_pipe = 4, 7
    xmin, xmax = 7, 72
    ymin, ymax = 5, 18

    def check_flow():
        """Color water flow blue; water flowing out with no destination pipe is red"""
        prev_pipe = (input_pipe[0] - 1, input_pipe[1])
        water = {prev_pipe, input_pipe}
        overflow = set()
        queue = deque([input_pipe])
        blank = Pipe(' ', ' ')
        dirs = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1),
        }
        opposite = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left',
        }
        while queue:
            row, col = queue.popleft()
            pipe = CELLS[grid[row][col]]
            good = set()
            bad = set()
            for dir_name, (dr, dc) in dirs.items():
                flow_size = getattr(pipe, dir_name)
                if flow_size == 0:
                    continue
                next_pipe = CELLS.get(grid[row + dr][col + dc], blank)
                if getattr(next_pipe, opposite[dir_name]) == flow_size:
                    good.add((row + dr, col + dc))
                else:
                    bad.add((row + dr, col + dc))
            for pos in good:
                if pos not in water:
                    queue.append(pos)
            water.update(good)
            if bad:
                overflow.add((row, col))
        return water, overflow

    check_flow()

    def play(screen: window):
        init_colors()
        log_pos = height, 2
        screen.clear()
        curses.curs_set(False)
        rotations = defaultdict(int)
        cursor_x, cursor_y = xmin, ymin
        key = ''

        def draw():
            flow, overflow = check_flow()
            for r, row in enumerate(grid):
                for c, char in enumerate(row):
                    if (r, c) in overflow:
                        color = OVERFLOW
                    elif (r, c) in flow:
                        color = WATER
                    elif char not in CELLS and ord(char) > 255:
                        color = IGNORE
                    else:
                        color = DEFAULT
                    if (r, c) == (cursor_y, cursor_x):
                        color |= CURSOR
                    screen.addch(r, c, char, curses.color_pair(color))
            screen.addstr(*log_pos, f'Rotations: {sum(rotations.values() or [0])}')
            # Some debugging output
            # screen.addstr(1, width + 2, key)
            # screen.addstr(2, width + 2, f'({cursor_x}, {cursor_y})')
            # screen.addstr(3, width + 2, str((width, height)))
            screen.refresh()

        draw()

        while True:
            match screen.getkey():
                case 'q' | 'Q':
                    break
                case 'KEY_UP':
                    if cursor_y > ymin:
                        cursor_y -= 1
                case 'KEY_DOWN':
                    if cursor_y < ymax:
                        cursor_y += 1
                case 'KEY_LEFT':
                    if cursor_x > xmin:
                        cursor_x -= 1
                case 'KEY_RIGHT':
                    if cursor_x < xmax:
                        cursor_x += 1
                case ' ':
                    pos = cursor_x, cursor_y
                    under_cursor = grid[cursor_y][cursor_x]
                    if under_cursor in CELLS:
                        rotations[pos] += 1
                        rotations[pos] %= CELLS[under_cursor].max_rot
                        grid[cursor_y][cursor_x] = CELLS[under_cursor].next
            draw()

    curses.wrapper(play)


if __name__ == '__main__':
    # solve('sample16.txt')
    solve('day16.txt')
