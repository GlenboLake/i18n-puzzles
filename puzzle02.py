from collections import defaultdict
from datetime import datetime, timezone


def get_timestamps(filename):
    with open(filename) as f:
        for line in f:
            yield datetime.fromisoformat(line.rstrip())


counts = defaultdict(int)
for ts in get_timestamps('day02.txt'):
    counts[ts.astimezone(timezone.utc).isoformat()] += 1

for ts, count in counts.items():
    if count >= 4:
        print(ts)
