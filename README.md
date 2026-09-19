# ISS, Fermi and AGILE coordinates

Calculate WGS84 longitude/latitude (degrees), altitude (km), and Earth-fixed ECEF velocity (unit vector and km/s) from TLEs using Skyfield/SGP4. Recommended: Python 3.10+.

## Setup and TLE updates

```sh
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in `SPACETRACK_USERNAME` and `SPACETRACK_PASSWORD` with your [Space-Track](https://www.space-track.org) credentials. `.env` is ignored by Git; environment variables override it.

```sh
python update_TLE_data.py            # latest elements
python update_TLE_data.py --history  # also fill history since the saved checkpoint
```

Updates preserve historical records, validate TLE checksums, replace files atomically, and cache successful checks for one hour. Keep the ignored `dataFiles/last_update_TLE.json` to retain history checkpoints. Existing gaps before a checkpoint are not automatically filled.

Included data, downloaded **19 September 2026**:

| Satellite | NORAD ID | Latest TLE epoch (UTC) |
| --- | --- | --- |
| ISS | 25544 | 2026-09-19 04:11:54.904992 |
| Fermi/GLAST | 33053 | 2026-09-19 02:40:19.289568 |
| AGILE | 31135 | 2024-02-08 00:00:00 (final archive) |

AGILE is no longer in orbit; its data is for historical calculations only.

## Usage

```python
from datetime import datetime, timezone
from satellite_coordinates import satellite_coordinates

sat = satellite_coordinates('ISS')  # also 'Fermi' or 'AGILE'
when = datetime(2026, 9, 19, 4, 12, tzinfo=timezone.utc)
lon, lat, altitude_km, velocity_direction, speed_km_s = sat.get_satellite_coordinates(when)
x, y, z = sat.get_lvlh_frame(when)
```

Naive datetimes mean UTC. `gps_to_ecef` and `ecef_to_gps` use **metres**, while `get_satellite_coordinates` returns altitude in **kilometres**. LVLH axes are expressed in ECEF: X along-track, Y opposite inertial angular momentum, Z toward Earth's centre. They describe the orbital frame, not measured spacecraft attitude.

TLE accuracy degrades away from its epoch: the code warns beyond 3 days and rejects beyond 14 days. These limits are not accuracy guarantees. Switching between nearest TLEs can introduce discontinuities. Precision work requires mission ephemerides and Earth-orientation data; measured polar motion is not configured here.

## Checks and examples

```sh
python -m unittest -v test_checks
python test.py
python get_ISS_velocity_and_position_and_LVLH_frame.py
python get_Fermi_velocity_and_position_and_LVLH_frame.py
```

Checks cover parsing, download integrity, UTC handling, coordinate/velocity consistency, and LVLH geometry on real archived TLEs; they do not establish accuracy against independent tracking data.
