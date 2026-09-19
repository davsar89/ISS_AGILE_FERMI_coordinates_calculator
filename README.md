# ISS, Fermi and AGILE coordinates

WGS84 longitude/latitude, ellipsoidal altitude, Earth-fixed ECEF velocity, and orbital LVLH from local TLEs using Skyfield/SGP4. Requires Python 3.10+.

## Install and use

```sh
python -m pip install .
```

```python
from datetime import datetime, timezone
from iss_coords import SatelliteCoordinates

sat = SatelliteCoordinates("ISS")  # also "Fermi" or "AGILE"; load once, reuse
state = sat.at(datetime(2026, 9, 19, 4, 12, tzinfo=timezone.utc))
print(state.longitude_deg, state.latitude_deg, state.altitude_km)
print(state.position_ecef_km, state.velocity_ecef_km_s, state.lvlh_ecef)
print(state.tle_epoch_utc, state.tle_age_seconds)
payload = state.to_dict()  # JSON-compatible values
```

Use `SatelliteCoordinates("ISS", data_dir="path/to/archives")` for external TLEs. `sat.coverage` gives the first and last epochs, not a guarantee of continuous coverage. Naive datetimes mean UTC. LVLH rows are X along-track, Y opposite inertial angular momentum, Z toward Earth's centre, expressed in ECEF axes; they are not measured spacecraft attitude.

Other software can call the CLI; `--json` writes one JSON object to stdout, with errors on stderr and a nonzero exit status:

```sh
satellite-coordinates ISS 2026-09-19T04:12:00Z --json
# Equivalent: python -m iss_coords ISS 2026-09-19T04:12:00Z --json
```

The original `satellite_coordinates` import and its coordinate/LVLH methods still work. Coordinate conversion helpers use **metres**; state positions and altitude use **kilometres**, velocity **km/s**, and TLE age absolute **seconds**.

## Update TLEs

Copy `.env.example` to `.env` and set `SPACETRACK_USERNAME` and `SPACETRACK_PASSWORD`. `.env` is ignored by Git; environment variables override it. Calculations work offline without credentials.

```sh
python update_TLE_data.py            # source checkout: update bundled archives
python update_TLE_data.py --history  # also fill history since the saved checkpoint
# Installed use: choose a writable directory and point the reader there too.
update-tle-data --data-dir ./archives --env-file .env --history
```

Updates preserve historical records, validate checksums, and replace each file atomically. Successful checks are cached for one hour. Keep `last_update_TLE.json` beside your archives to retain checkpoints; existing gaps before a checkpoint are not automatically filled.

Bundled archives (`iss_coords/dataFiles/`), checked **19 September 2026**:

| Satellite | NORAD ID | Latest TLE epoch (UTC) |
| --- | --- | --- |
| ISS | 25544 | 2026-09-19 04:11:54.904992 |
| Fermi/GLAST | 33053 | 2026-09-19 02:40:19.289568 |
| AGILE | 31135 | 2024-02-08 00:00:00 (final archive) |

A historical reconciliation with Space-Track returned no additional records. Largest remaining gaps: ISS **6.77 days**, Fermi **4.62 days**, AGILE **58.67 days** (8 September–6 November 2007). AGILE is no longer in orbit; its data is historical only.

TLE accuracy degrades away from its epoch: calls warn beyond 3 days and fail beyond 14 days. These are safeguards, not accuracy guarantees. Nearest-TLE changes can introduce discontinuities. Precision work needs mission ephemerides and Earth-orientation data; measured polar motion is not configured here.

## Checks and layout

```sh
python -m unittest discover -s tests -v
python examples/coordinates.py
```

`iss_coords/` contains propagation, TLE parsing, downloading, and the CLI; `examples/` contains one reusable example; `tests/` checks physics consistency, data integrity, and the public API. Root Python files retain compatibility with earlier usage. Checks do not establish accuracy against independent tracking measurements.
