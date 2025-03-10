from zoneinfo import ZoneInfo

from pendulum import Duration
from pendulum.parser import parse


def get_itineraries(filename):
    with open(filename) as f:
        itineraries = f.read().split('\n\n')
    for itinerary in itineraries:
        depart, arrive = itinerary.splitlines()
        _, depart_zone, depart_time = depart.split(maxsplit=2)
        departure = parse(depart_time, strict=False).naive().in_tz(depart_zone)
        _, arrive_zone, arrive_time = arrive.split(maxsplit=2)
        arrival = parse(arrive_time, strict=False).naive().in_tz(arrive_zone)
        yield departure, arrival


def solve(filename):
    return int(sum(
        (arrival-departure for departure, arrival in get_itineraries(filename)),
        start=Duration()
    ).total_minutes())


if __name__ == '__main__':
    assert solve('sample04.txt') == 3143
    print(solve('day04.txt'))