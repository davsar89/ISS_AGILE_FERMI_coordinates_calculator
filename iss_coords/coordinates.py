"""SGP4 propagation, WGS84 coordinates, and orbital LVLH in ECEF axes."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import warnings

import numpy as np
import pyproj
from skyfield import api
from skyfield.framelib import itrs

from .tle_data import DATA_DIR, SATELLITES, parse_tles, tle_epoch


@dataclass
class SatelliteState:
    """One propagated state; vectors use ECEF axes and LVLH axes are rows.

    tle_age_seconds is the absolute distance from the selected TLE epoch.
    Earth-fixed velocity includes Earth's rotation; LVLH uses inertial motion.
    """
    satellite: str
    time_utc: datetime
    tle_epoch_utc: datetime
    tle_age_seconds: float
    longitude_deg: float
    latitude_deg: float
    altitude_km: float
    position_ecef_km: np.ndarray
    velocity_ecef_km_s: np.ndarray
    speed_km_s: float
    lvlh_ecef: np.ndarray

    def to_dict(self):
        """Return ordinary Python values suitable for JSON serialization."""
        return {key: value.isoformat() if isinstance(value, datetime)
                else value.tolist() if isinstance(value, np.ndarray) else value
                for key, value in asdict(self).items()}


class SatelliteCoordinates:
    """Load an archive once, then call at(time) for each requested instant.

    data_dir defaults to the bundled archives. Use a writable external directory
    for independently updated data. Naive datetimes mean UTC for compatibility.
    """

    def __init__(self, name, *, data_dir=None):
        if name not in SATELLITES:
            raise ValueError("name must be 'ISS', 'Fermi', or 'AGILE'")
        self.name = name
        self.data_file_path = Path(data_dir or DATA_DIR) / SATELLITES[name][1]
        self.datetimes, self.TLE_line_1, self.TLE_line_2 = self.read_satellite_TLE_data(self.data_file_path)
        self.time_value = np.array([dt.timestamp() for dt in self.datetimes])
        self.ts = api.load.timescale()
        self.to_ecef = pyproj.Transformer.from_crs("EPSG:4979", "EPSG:4978", always_xy=True)
        self.to_lla = pyproj.Transformer.from_crs("EPSG:4978", "EPSG:4979", always_xy=True)

    @property
    def coverage(self):
        """First and last UTC TLE epochs; gaps can exist within this interval."""
        return self.datetimes[0], self.datetimes[-1]

    def gps_to_ecef(self, lat, lon, alt):
        """Degrees and altitude in metres -> ECEF x, y, z in metres."""
        return self.to_ecef.transform(lon, lat, alt)

    def ecef_to_gps(self, x, y, z):
        """ECEF metres -> longitude/latitude in degrees and altitude in metres."""
        return self.to_lla.transform(x, y, z)

    def nearestDate(self, base):
        """Return the nearest epoch index and absolute age in seconds."""
        timestamp = self.as_utc(base).timestamp()
        right = int(np.searchsorted(self.time_value, timestamp))
        candidates = [i for i in (right - 1, right) if 0 <= i < len(self.time_value)]
        index = min(candidates, key=lambda i: abs(self.time_value[i] - timestamp))
        # Preserve the former argmin tie rule, including duplicate epochs.
        index = int(np.searchsorted(self.time_value, self.time_value[index]))
        return index, float(abs(self.time_value[index] - timestamp))

    def read_satellite_TLE_data(self, data_file_path):
        pairs = parse_tles(Path(data_file_path).read_text(), SATELLITES[self.name][0])
        if not pairs:
            raise ValueError("TLE archive is empty; run the TLE downloader")
        pairs.sort(key=lambda pair: tle_epoch(pair[0]))
        return ([tle_epoch(first) for first, _ in pairs],
                [first for first, _ in pairs], [second for _, second in pairs])

    @staticmethod
    def as_utc(value):
        if not isinstance(value, datetime):
            raise TypeError("time must be a Python datetime")
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def at(self, time):
        """Return coordinates, velocity, LVLH, and TLE provenance in one call."""
        time = self.as_utc(time)
        index, age = self.nearestDate(time)
        state = self._propagate(time)
        position, velocity = state.frame_xyz_and_velocity(itrs)
        position, velocity = position.km, velocity.km_per_s
        speed = float(np.linalg.norm(velocity))
        if not np.all(np.isfinite(position)) or not np.isfinite(speed) or speed == 0:
            raise ValueError("SGP4 produced an invalid state")
        lon, lat, alt = self.ecef_to_gps(*(position * 1000))
        rotation = itrs.rotation_at(state.t)
        inertial_velocity = rotation @ state.velocity.km_per_s
        z = -position / np.linalg.norm(position)
        y = np.cross(z, inertial_velocity)
        norm_y = np.linalg.norm(y)
        if not np.isfinite(norm_y) or norm_y == 0:
            raise ValueError("Cannot construct LVLH from this state")
        y /= norm_y
        frame = np.array([np.cross(y, z), y, z])
        return SatelliteState(self.name, time, self.datetimes[index], age,
                              lon, lat, alt / 1000, position, velocity, speed, frame)

    def get_satellite_coordinates(self, input_datetime):
        """Compatibility tuple: lon, lat, altitude_km, velocity unit vector, km/s."""
        result = self.at(input_datetime)
        return (result.longitude_deg, result.latitude_deg, result.altitude_km,
                result.velocity_ecef_km_s / result.speed_km_s, result.speed_km_s)

    def get_lvlh_frame(self, input_datetime):
        """Compatibility method returning X, Y, Z unit rows in ECEF axes."""
        return self.at(input_datetime).lvlh_ecef

    def _propagate(self, input_datetime):
        time = self.as_utc(input_datetime)
        index, age = self.nearestDate(time)
        if age > 14 * 86400:
            raise ValueError(
                f"Nearest {self.name} TLE ({self.datetimes[index].isoformat()}) is "
                f"{age / 86400:.1f} days away; maximum allowed is 14 days. "
                "Provide an archive with elements near the requested time.")
        if age > 3 * 86400:
            warnings.warn("Nearest TLE is over 3 days away; positional accuracy is uncertain",
                          RuntimeWarning, stacklevel=3)
        satellite = api.EarthSatellite(self.TLE_line_1[index], self.TLE_line_2[index], ts=self.ts)
        state = satellite.at(self.ts.from_datetime(time))
        if state.message:
            raise ValueError(f"SGP4 propagation failed: {state.message}")
        if api.wgs84.height_of(state).m < 0:
            raise ValueError("Propagated satellite is below the WGS84 ellipsoid")
        return state
