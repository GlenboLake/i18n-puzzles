from pendulum import DateTime


def load(filename):
    zones = 'America/Halifax', 'America/Santiago'
    with open(filename) as f:
        for line in f:
            t, correct, incorrect = line.split()
            dt = DateTime.fromisoformat(t)
            correct = int(correct)
            incorrect = int(incorrect)
            for tz in zones:
                check = dt.in_tz(tz)
                if check.offset == dt.offset:
                    yield check, correct, incorrect
                    break


def solve(filename):
    fixed_times = [
        dt.add(minutes=correct - incorrect)
        for dt, correct, incorrect in load(filename)
    ]
    return sum(i*dt.hour for i, dt in enumerate(fixed_times, start=1))


if __name__ == '__main__':
    assert solve('sample07.txt') == 866
    print(solve('day07.txt'))
