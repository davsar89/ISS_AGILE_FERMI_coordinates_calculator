"""Shared TLE parsing; epochs are UTC and retain sub-second precision."""
import calendar
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "dataFiles"
SATELLITES = {
    "ISS": (25544, "ISS_orbital_info.txt"),
    "Fermi": (33053, "Fermi_GLAST_orbital_info.txt"),
    "AGILE": (31135, "AGILE_orbital_info.txt"),
}


def tle_epoch(line):
    year = int(line[18:20])
    year += 1900 if year >= 57 else 2000
    day = float(line[20:32])
    if not 1 <= day < 366 + calendar.isleap(year):
        raise ValueError("TLE epoch day is outside its calendar year")
    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day - 1)


def parse_tles(text, norad_id=None):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) % 2:
        raise ValueError("Incomplete TLE pair")
    pairs = list(zip(lines[::2], lines[1::2]))
    for first, second in pairs:
        for number, line in enumerate((first, second), 1):
            if len(line) != 69 or not line.startswith(f"{number} "):
                raise ValueError("Expected a 69-column two-line element record")
            checksum = sum(int(c) if c.isdigit() else c == "-" for c in line[:68]) % 10
            if not line[68].isdigit() or checksum != int(line[68]):
                raise ValueError("TLE checksum mismatch")
        if first[2:7] != second[2:7]:
            raise ValueError("TLE lines refer to different satellites")
        if norad_id is not None and int(first[2:7]) != norad_id:
            raise ValueError("Unexpected satellite in TLE response")
        tle_epoch(first)
    return pairs
