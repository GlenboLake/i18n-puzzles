import string

from unidecode import unidecode


def get_lines(filename):
    with open(filename, encoding='utf-8') as f:
        for line in f:
            yield line.strip()


vowels = 'aeiouAEIOU'
consonants = {letter for letter in string.ascii_letters if letter not in vowels}


def repeat_check(password):
    unaccented = unidecode(password)
    return len(unaccented) == len(set(unaccented.lower()))


rules = [
    # a length of at least 4 and at most 12
    lambda line: 4 <= len(line) <= 12,
    # at least one digit
    lambda line: any(ch in line for ch in string.digits),
    # at least one accented or unaccented vowel1 (a, e, i, o, u) (examples: i, Á or ë)
    lambda line: any(ch in unidecode(line) for ch in vowels),
    # at least one accented or unaccented consonant, examples: s, ñ or ŷ
    lambda line: any(ch in unidecode(line) for ch in consonants),
    # no recurring letters in any form. Ignoring accents and case, letters should not recur.
    # For example, in 'niña' the 'n' occurs twice, one time with accent and one time without.
    # 'Usul' is out because the 'u' occurs twice, first uppercase and then lowercase.
    repeat_check,
]


def check_line(line):
    for i, rule in enumerate(rules):
        if not rule(line):
            return False
    return True


def solve(filename):
    return [check_line(line) for line in get_lines(filename)].count(True)


if __name__ == '__main__':
    assert solve('sample08.txt') == 2
    print(solve('day08.txt'))
