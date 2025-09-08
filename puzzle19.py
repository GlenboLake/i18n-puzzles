from collections import defaultdict
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Generator
from zoneinfo import ZoneInfo

TZ_TEMPLATE = Template(str(Path(__file__).parent / '$version/usr/share/zoneinfo/$tz'))
VERSIONS = ['2018c', '2018g', '2021b', '2023d']
UTC = ZoneInfo('UTC')


def parse_input(filename: str) -> Generator[tuple[datetime, str], None, None]:
    with open(filename) as f:
        for line in f:
            dt, tz = line.strip().split('; ')
            yield datetime.fromisoformat(dt), tz


def load_zone_info(version: str, tz: str):
    filename = TZ_TEMPLATE.substitute(version=version, tz=tz)
    with open(filename, 'rb') as f:
        return ZoneInfo.from_file(f)


def solve(filename: str):
    times = list(parse_input(filename))
    iana_names = {iana for _, iana in times}
    zone_infos = {
        (version, iana): load_zone_info(version, iana)
        for version in VERSIONS
        for iana in iana_names
    }
    utc_times: dict[datetime, set[str]] = defaultdict(set)
    for local_time, iana_name in times:
        for version in VERSIONS:
            tz = zone_infos[version, iana_name]
            utc_time = local_time.replace(tzinfo=tz).astimezone(UTC)
            utc_times[utc_time].add(iana_name)
    result = max(utc_times, key=lambda t: len(utc_times[t]))
    return result.isoformat()


if __name__ == '__main__':
    assert solve('sample19.txt') == '2024-04-09T17:49:00+00:00'
    print(solve('day19.txt'))
