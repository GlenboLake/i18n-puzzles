"""Challenge to myself: Do this without eval()"""
import operator
import re
from fractions import Fraction

DEBUG = False

LRI = '\u2066'
RLI = '\u2067'
PDI = '\u2069'

printable = str.maketrans({RLI: '⏴', LRI: '⏵', PDI: '⏶'})
swap_parens = str.maketrans({'(': ')', ')': '('})
remove_markers = str.maketrans({RLI: None, LRI: None, PDI: None})


class Stack(list):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    @property
    def value(self):
        tokens = self.copy()
        assert len(tokens) % 2 == 1
        while len(tokens) > 1:
            a, op, b, *_ = tokens
            assert isinstance(a, (Fraction, Stack))
            assert isinstance(b, (Fraction, Stack))
            assert callable(op)
            if isinstance(a, Stack):
                a_val = a.value
            else:
                a_val = a
            if isinstance(b, Stack):
                b_val = b.value
            else:
                b_val = b
            tokens[:3] = [op(a_val, b_val)]
        return tokens[0]


def eval_expr(expr: str) -> int:
    stack = Stack()
    operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }
    remaining = expr
    while remaining:
        if match := re.match(r'\d+', remaining):
            stack.append(Fraction(match.group()))
            remaining = remaining[match.end():]
        else:
            token = remaining[0]
            remaining = remaining[1:]
            if token.isspace():
                continue
            elif token == '(':
                new_stack = Stack(parent=stack)
                stack.append(new_stack)
                stack = new_stack
            elif token == ')':
                stack = stack.parent
            else:
                stack.append(operators[token])
    return stack.value


def eval_rex(equation: str) -> int:
    no_markers = ''.join(filter(lambda char: char not in (LRI, RLI, PDI), equation)).strip()
    return eval_expr(no_markers)


def eval_lynx(equation: str) -> int:
    embedded_levels = []
    current_level = 0
    current_direction = LRI
    for ch in equation:
        if ch.isdigit() and current_level % 2 == 1:
            embedded_levels.append(current_level + 1)
        elif ch in (LRI, RLI):
            # assert current_direction != ch, "Can this happen?"
            embedded_levels.append(current_level)
            current_level += 1
            current_direction = ({LRI, RLI} - {current_direction}).pop()
        elif ch == PDI:
            current_level -= 1
            embedded_levels.append(current_level)
            current_direction = ({LRI, RLI} - {current_direction}).pop()
        else:
            embedded_levels.append(current_level)
    flip_levels: range = range(1, 1 + max(embedded_levels))[::-1]

    def find_ranges(threshold: int) -> list[slice]:
        nonlocal embedded_levels
        ranges = []
        start, end = None, None
        for i, level in enumerate(embedded_levels):
            if level >= threshold:
                end = i
                if start is None:
                    start = i
            elif start is not None:
                if start != end:
                    ranges.append(slice(start, end + 1))
                start = end = None
        return ranges

    for flip in flip_levels:
        for r in find_ranges(flip):
            equation = (
                    equation[:r.start] +
                    equation[r][::-1].translate(swap_parens) +
                    equation[r.stop:]
            )
    return eval_expr(equation.translate(remove_markers))


def solve(filename: str):
    total = 0
    with open(filename) as f:
        for i, equation in enumerate(f, start=1):
            equation = equation.rstrip('\n')
            rex = eval_rex(equation)
            lynx = eval_lynx(equation)
            total += abs(rex - lynx)
            if DEBUG:
                print(f'Line {i}: {rex} vs {lynx} ({abs(rex - lynx)})')
    return total


if __name__ == '__main__':
    assert solve('sample18.txt') == 19_282
    print(solve('day18.txt'))
