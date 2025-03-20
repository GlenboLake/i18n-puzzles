def load(filename):
    with open(filename) as f:
        words, puzzle = f.read().split('\n\n')
    return words.splitlines(), puzzle.splitlines()


def fix_word_list(words):
    def fix(word):
        return word.encode('latin-1').decode('utf-8')

    for i, word in enumerate(words, start=1):
        if i % 3 == 0:
            word = fix(word)
        if i % 5 == 0:
            word = fix(word)
        yield word


def solve(filename):
    words, puzzle = load(filename)
    words = list(fix_word_list(words))
    return solve_puzzle(words, puzzle)


def solve_puzzle(words, puzzle):
    solution = 0
    for line in puzzle:
        length = len(line.strip())
        match_index, match_char = [(i, x) for i, x in enumerate(line.strip()) if x != '.'].pop()
        solution += [
            i for i, word in enumerate(words, start=1)
            if len(word) == length and word[match_index] == match_char
        ][0]
    return solution


if __name__ == '__main__':
    assert solve('sample06.txt') == 50
    print(solve('day06.txt'))