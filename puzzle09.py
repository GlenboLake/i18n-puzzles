from collections import defaultdict

import pendulum


def load(filename):
    with open(filename) as f:
        for line in f:
            date, names = line.strip().split(': ')
            yield date, names.split(', ')


def solve(filename):
    data = list(load(filename))
    formats = {'YY-MM-DD', 'YY-DD-MM', 'DD-MM-YY', 'MM-DD-YY'}
    options = defaultdict(formats.copy)
    entries = defaultdict(set)

    def check_format(data_string, format_):
        try:
            pendulum.from_format(data_string, format_)
        except ValueError:
            return False
        return True

    for date, names in data:
        valid_formats = {
            f for f in formats
            if check_format(date, f)
        }
        for name in names:
            options[name] &= valid_formats
            entries[name].add(date)
    user_formats = {
        name: list(opts)[0]
        for name, opts in options.items()
    }

    nine_eleven = pendulum.Date(2001, 9, 11)

    wrote_of_nine_eleven = [
        name
        for name, dates in entries.items()
        if nine_eleven.format(user_formats[name]) in dates
    ]
    return ' '.join(sorted(wrote_of_nine_eleven))


if __name__ == '__main__':
    assert solve('sample09.txt') == 'Margot Peter'
    print(solve('day09.txt'))
