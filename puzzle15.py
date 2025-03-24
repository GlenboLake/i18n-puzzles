from datetime import date
from textwrap import dedent
from typing import Iterable

import dateutil.parser
from pendulum import Date, Interval, WeekDay, DateTime, Time, Timezone, UTC


class Office:
    def __init__(self, name: str, tz_name: str, holidays: list[date]):
        self.name = name
        self.tz = tz_name
        self.holidays = holidays

    def __str__(self):
        return self.name

    @classmethod
    def parse(cls, text: str):
        """:rtype: Office"""
        name, tz, holidays = text.split('\t')
        holidays = [
            dateutil.parser.parse(h).date()
            for h in holidays.split(';')
        ]
        return cls(name, tz, holidays)

    def open_times(self, year: int, day_start, day_end):
        weekdays = [
            WeekDay.MONDAY,
            WeekDay.TUESDAY,
            WeekDay.WEDNESDAY,
            WeekDay.THURSDAY,
            WeekDay.FRIDAY,
        ]
        jan1 = Date(year, 1, 1)
        start = jan1.subtract(days=1)
        end = jan1.add(years=1)
        days = (
            d
            for d in Interval(start, end).range('days')
            if d.day_of_week in weekdays and d not in self.holidays
        )
        days = list(days)
        tz = Timezone(self.tz)
        for day in days:
            start = DateTime.combine(day, day_start, tzinfo=tz)
            end = DateTime.combine(day, day_end, tzinfo=tz)
            yield Interval(start, end)


class Client(Office):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overtime = 0


def merge_ranges(ranges: Iterable[Interval]):
    rs = iter(ranges)
    prev_range = next(rs)
    for r in rs:
        if interval_overlap(prev_range, r):
            prev_range = Interval(
                min(prev_range.start, r.start),
                max(prev_range.end, r.end),
            )
        else:
            yield prev_range
            prev_range = r
    yield prev_range


def interval_overlap(interval_1: Interval, interval_2: Interval):
    left = max(interval_1.start, interval_2.start)
    right = min(interval_1.end, interval_2.end)
    if left < right:
        return Interval(left, right)


def load(filename):
    with open(filename) as f:
        office_lines, customer_lines = f.read().split('\n\n')
    offices = [Office.parse(line) for line in office_lines.splitlines()]
    customers = [Client.parse(line) for line in customer_lines.splitlines()]
    return offices, customers


def solve(filename):
    offices, customers = load(filename)
    year_start = DateTime(2022, 1, 1, tzinfo=UTC)
    year_end = DateTime(2023, 1, 1, tzinfo=UTC)
    num_blocks: int = int((year_end - year_start).total_minutes() // 30)
    covered_time_blocks = [False] * num_blocks
    office_time_blocks = {
        office: covered_time_blocks.copy()
        for office in offices + customers
    }

    def time_block(dt: DateTime):
        offset = int(max((dt - year_start).total_minutes(), 0))
        return offset // 30

    for office in offices:
        for time_range in office.open_times(2022, day_start=Time(8, 30), day_end=Time(17)):
            start = time_block(time_range.start)
            end = time_block(time_range.end)
            if end:
                for i in range(start, end):
                    covered_time_blocks[i] = True
                    office_time_blocks[office][i] = True
    for customer in customers:
        for time_range in customer.open_times(2022, day_start=Time(), day_end=Time().subtract(microseconds=1)):
            start = time_block(time_range.start)
            end = time_block(time_range.end)
            if end:
                for i in range(start, end + 1):
                    office_time_blocks[customer][i] = True

    def print_coverage(d: Date):
        """Print the coverage for a specific date, formatted as in the problem statement"""
        day_of_week = d.format('dddd')
        date_string = d.format('DD MMMM YYYY')
        start = DateTime.combine(d, Time(), tzinfo=UTC)
        end = start.add(days=1)
        time_range = slice(time_block(start), time_block(end))
        print(dedent(f'''\
        {day_of_week:<9}               Hour (UTC): 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 1 1 1 1 1 2 2 2 2 
        {date_string:<20}                                    0 1 2 3 4 5 6 7 8 9 0 1 2 3 
                                            | | | | | | | | | | | | | | | | | | | | | | | | 
        ''').rstrip('\n'))
        for office in offices:
            print(f'{office.name[17:]:>35} ', end='')
            print(''.join(
                'S' if tb else ' '
                for tb in office_time_blocks[office][time_range]
            ))
        print('                                    | | | | | | | | | | | | | | | | | | | | | | | | ')
        for client in customers:
            print(f'{client.name:>35} ', end='')
            print(''.join(
                'R' if tb else ' '
                for tb in office_time_blocks[client][time_range]
            ))

    overtime = {
        customer: sum(
            30
            for covered, support_required in zip(covered_time_blocks, office_time_blocks[customer])
            if support_required and not covered
        )
        for customer in customers
    }
    return max(overtime.values()) - min(overtime.values())


if __name__ == '__main__':
    assert solve('sample15.txt') == 3030
    print(solve('day15.txt'))