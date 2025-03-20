from itertools import batched

from puzzle06 import solve_puzzle

bytestring = '616e77c3a4686c65'


def str2bytes(s):
    return bytes(
        int(''.join(b), 16)
        for b in batched(bytestring, 2)
    )


value = str2bytes(bytestring)


def load(filename):
    with open(filename) as f:
        words, puzzle = f.read().split('\n\n')
    encoded_words = [
        bytes(
            int(''.join(b), 16)
            for b in batched(line.strip(), 2)
        )
        for line in words.splitlines()
    ]
    return encoded_words, puzzle.splitlines()


def solve(filename):
    encoded_words, puzzle = load(filename)

    def decode_word(word):
        has_bom = word[:2] in (b'\xff\xfe', b'\xfe\xff')
        if has_bom:
            encodings = ('utf-8-sig', 'utf-16')
        else:
            encodings = ('latin-1', 'utf-8', 'utf-8-sig', 'utf-16-le', 'utf-16-be')

        for encoding in encodings:
            try:
                decoded = word.decode(encoding)
            except UnicodeDecodeError:
                continue
            if decoded.isalnum() and all(ord(ch) < 0x24f for ch in decoded):  # 0x24F is the end of the latin unicode range
                return decoded
        orig_line = ''.join(hex(ch + 0xf00)[3:] for ch in word)
        print(f"Couldn't decode {orig_line}")
    words = [decode_word(w) for w in encoded_words]
    # From here, it's just puzzle 6 again
    return solve_puzzle(words, puzzle)


if __name__ == '__main__':
    assert solve('sample13.txt') == 47
    print(solve('day13.txt'))
