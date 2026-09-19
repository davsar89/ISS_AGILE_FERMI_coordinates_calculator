# ISS, Fermi and AGILE coordinates

Compute WGS84 longitude/latitude (degrees), ellipsoidal altitude (km), and Earth-fixed (ITRS/ECEF) velocity (unit vector and km/s) from Space-Track TLEs using Skyfield/SGP4. Python 3.10 or newer is recommended.

## Install and update TLEs

```sh
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and enter your Space-Track account email and password. The `.env` file is ignored by Git; never put credentials in Python source. Environment variables `SPACETRACK_USERNAME` and `SPACETRACK_PASSWORD` override the file. A Space-Track account is required.

```sh
python update_TLE_data.py            # merge the latest elements into the archive
python update_TLE_data.py --history  # also fill history since the saved archive epoch
```

The downloader is adapted from `DOWNLOAD_UPDATE_TLE_DATA.zip`. It uses the current `gp` and `gp_history` API classes, checks satellite IDs, line structure and checksums, retains historical records, removes exact duplicates, sorts by epoch, and replaces each file atomically. Updates are cached for one hour. It does not delete archives before requesting data. Paths are relative to the scripts, so commands also work from another directory.

The ignored `dataFiles/last_update_TLE.json` stores local check times and history checkpoints. Keep it when using latest-only updates before a later history update. If moving archives to another machine, copy this file as well to retain those checkpoints. For a fresh clone, the last archived epoch is the initial checkpoint; existing gaps inside an archive are not automatically repaired. Atomic replacement is per file: an interrupted multi-satellite update may leave some files newer than others; a retry retains completed history checkpoints.

Space-Track guidance: https://www.space-track.org/documentation

### Included data, downloaded 19 September 2026 (UTC)

| Satellite | NORAD ID | Latest TLE epoch (UTC) | Unique records |
| --- | --- | --- | --- |
| ISS | 25544 | 2026-09-19 04:11:54.904992 | 47,850 |
| Fermi/GLAST | 33053 | 2026-09-19 02:40:19.289568 | 10,927 |
| AGILE | 31135 | 2024-02-08 00:00:00 | 5,285 |

ISS and Fermi include the history retrieved since the previous May 2024 archive endpoints. All original unique TLE pairs are retained. AGILE is final: it re-entered in February 2024, and no newer elements were returned. Mission announcement: https://www.asi.it/2024/02/rientrato-in-atmosfera-il-satellite-agile-dellagenzia-spaziale-italiana/

## Calculate coordinates

```python
from datetime import datetime, timezone
from satellite_coordinates import satellite_coordinates

sat = satellite_coordinates('ISS')  # also 'Fermi' or 'AGILE'
when = datetime(2026, 9, 19, 4, 12, tzinfo=timezone.utc)
lon, lat, altitude_km, velocity_direction, speed_km_s = sat.get_satellite_coordinates(when)
x, y, z = sat.get_lvlh_frame(when)
```

Naive datetimes are interpreted as UTC for compatibility; timezone-aware inputs are converted to UTC. TLE epochs retain their fractional day and use the standard 1957/2056 two-digit-year pivot. The nearest epoch is selected with sub-second precision.

`gps_to_ecef(lat, lon, alt)` and `ecef_to_gps(x, y, z)` use **metres** for altitude and Cartesian coordinates. Returned geographic altitude from `get_satellite_coordinates` is in **kilometres**.

`get_lvlh_frame` returns three orthonormal, right-handed unit rows expressed in ECEF axes: X along the orbit tangent, Y opposite inertial angular momentum, Z toward Earth's centre. It uses inertial velocity rotated into ECEF axes. The older examples used Earth-relative velocity, which defines a different, ground-track frame. This is a geometric orbital frame, not a measurement of spacecraft attitude. Both example scripts now use the shared method.

## Accuracy and checks

TLEs are fitted mean elements for SGP4, not exact spacecraft ephemerides. Nearest-epoch selection can switch between independently fitted orbits and produce small discontinuities; do not differentiate across those boundaries. The code warns beyond 3 days from an epoch and rejects propagation beyond 14 days, as practical safeguards, not accuracy guarantees. It rejects SGP4 failures and below-ellipsoid states. Historical AGILE elements must not be used as a current orbit.

Skyfield uses its bundled timescale data here; no measured polar-motion series is configured. These calculations do not establish precision orbit or attitude accuracy. Use mission ephemerides and appropriate Earth-orientation data when that precision is required.

```sh
python -m unittest -v test_checks
python test.py
python get_ISS_velocity_and_position_and_LVLH_frame.py
python get_Fermi_velocity_and_position_and_LVLH_frame.py
```

Checks cover TLE epoch decoding against Skyfield, corrupt-data rejection, retained files after download/write failures, archive merging/checkpoints, timezone equivalence, plausible low-Earth-orbit scales, WGS84 round trips and comparison with Skyfield, finite-difference Earth-fixed velocity, and LVLH geometry/angular momentum. They use representative historical orbits plus the latest ISS/Fermi records. Passing these checks supports implementation consistency; it does not establish agreement with independent tracking measurements.

References: [Skyfield satellite guidance](https://rhodesmill.org/skyfield/earth-satellites.html), [TLE format and epoch convention](https://celestrak.org/columns/v04n03/).
