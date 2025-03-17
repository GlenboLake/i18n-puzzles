from itertools import product

import bcrypt
import unicodedata


def load(filename):
    with open(filename, 'rb') as f:
        db, attempts = f.read().split(b'\n\n')
    users = dict(line.split() for line in db.splitlines())
    attempts = [line.split() for line in attempts.splitlines()]
    return users, attempts


def all_encodings(pw: str):
    characters = [
        {
            unicodedata.normalize('NFC', c).encode(),
            unicodedata.normalize('NFD', c).encode(),
        } for c in pw
    ]
    yield from (b''.join(encoding) for encoding in product(*characters))


def solve(filename):
    db, attempts = load(filename)
    cache = {}
    valid_attempts = 0
    for name, entry in attempts:
        text: str = unicodedata.normalize('NFC', entry.decode())
        if cache.get(name) == text:
            valid_attempts += 1
            continue
        for option in all_encodings(text):
            if bcrypt.checkpw(option, db[name]):
                cache[name] = text
                valid_attempts += 1
                break
    return valid_attempts




if __name__ == '__main__':
    assert solve('sample10.txt') == 4
    print(solve('day10.txt'))
