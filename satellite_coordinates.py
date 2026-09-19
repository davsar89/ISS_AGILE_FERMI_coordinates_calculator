import datetime
import warnings
from pathlib import Path

import numpy as np
import pyproj
from skyfield import api
from skyfield.framelib import itrs

from tle_data import DATA_DIR, SATELLITES, parse_tles, tle_epoch


class satellite_coordinates:
    ##

    def __init__(self, name):
        """
        :param name: satellite name, must be 'ISS', 'Fermi', or 'AGILE'
        """
        self.name = name

        if name not in SATELLITES:
            raise ValueError("name must be 'ISS', 'Fermi', or 'AGILE'")
        self.data_file_path = DATA_DIR / SATELLITES[name][1]
        self.datetimes, self.TLE_line_1, self.TLE_line_2 = self.read_satellite_TLE_data(self.data_file_path)
        self.time_value = np.array([dt.timestamp() for dt in self.datetimes])
        self.ts = api.load.timescale()
        self.to_ecef = pyproj.Transformer.from_crs("EPSG:4979", "EPSG:4978", always_xy=True)
        self.to_lla = pyproj.Transformer.from_crs("EPSG:4978", "EPSG:4979", always_xy=True)

    ##
    def gps_to_ecef(self, lat, lon, alt):
        """
        Inputs:
          - lon, lat in degrees
          - alt in meters
        Outputs:
          - x,y,z in meters
        """
        x, y, z = self.to_ecef.transform(lon, lat, alt)
        return x, y, z
    
    def ecef_to_gps(self, x, y, z):
        """
        Inputs:
          - x,y,z in meters
        Outputs:
          - lon, lat in degrees
          - alt in meters
        """
        lon, lat, alt = self.to_lla.transform(x, y, z)
        return lon, lat, alt 

    ##

    def nearestDate(self, base):
        base_timestamp = self.as_utc(base).timestamp()
        differences = np.abs(base_timestamp - self.time_value)
        arggmin = np.argmin(differences)
        delta_t = differences[arggmin]
        return arggmin, delta_t

    ##

    def read_satellite_TLE_data(self,data_file_path):
        """
        Convert textfile (txt) containing list of TLE of a given satellite to python lists of times and TLE
        :return: datetimes: list of datetime read in the file
                TLE_line_1: first line of TLE at given 'datetimes' date
                TLE_line_2: second line of TLE at given 'datetimes' date
        """
        pairs = parse_tles(Path(data_file_path).read_text(), SATELLITES[self.name][0])
        if not pairs:
            raise ValueError("TLE archive is empty; run update_TLE_data.py")
        return ([tle_epoch(first) for first, _ in pairs],
                [first for first, _ in pairs], [second for _, second in pairs])

    @staticmethod
    def as_utc(value):
        """For backward compatibility naive datetimes mean UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(datetime.timezone.utc)

    def get_satellite_coordinates(self, input_datetime):
        """
    Calculates the longitude (deg), latitude (deg), altitude (km) and velocity vector (normalized + magntitude in km/s) of a satellite at a given time
        :param input_datetime: python datetime structure identifying the time where the coordinates of the satellite is wanted
        :return: longitude (deg), latitude (deg), altitude (km), velocity vector (normalized), magnitude of the velocity vector (in km/s)
        """
        
        state = self._propagate(input_datetime)
        position, velocity = state.frame_xyz_and_velocity(itrs)
        position = position.m
        velocity = velocity.km_per_s
        speed = np.linalg.norm(velocity)
        if not np.all(np.isfinite(position)) or not np.isfinite(speed) or speed == 0:
            raise ValueError("SGP4 produced an invalid state")
        lon, lat, alt = self.ecef_to_gps(*position)
        if alt < 0:
            raise ValueError("Propagated satellite is below the WGS84 ellipsoid")
        return lon, lat, alt / 1000, velocity / speed, speed

    def get_lvlh_frame(self, input_datetime):
        """Return X,Y,Z unit rows in ECEF: along-track, -orbit-normal, nadir.

        Orbital angular momentum uses inertial velocity, rotated into ECEF
        axes. Earth-relative velocity would instead define a ground-track frame.
        """
        state = self._propagate(input_datetime)
        rotation = itrs.rotation_at(state.t)
        position = rotation @ state.xyz.km
        velocity = rotation @ state.velocity.km_per_s
        z = -position / np.linalg.norm(position)
        y = np.cross(z, velocity)
        y /= np.linalg.norm(y)
        frame = np.array([np.cross(y, z), y, z])
        if not np.all(np.isfinite(frame)):
            raise ValueError("Cannot construct LVLH from this state")
        return frame

    def _propagate(self, input_datetime):
        input_datetime = self.as_utc(input_datetime)
        closest_idx, delta_t = self.nearestDate(input_datetime)
        # TLEs are local orbit fits, not an ephemeris valid for arbitrary dates.
        if delta_t > 14 * 86400:
            raise ValueError("Nearest TLE is more than 14 days away; update the archive or request historical data")
        if delta_t > 3 * 86400:
            warnings.warn("Nearest TLE is over 3 days away; positional accuracy is uncertain", RuntimeWarning)
        print(f"Closest TLE has a delta time of: {delta_t:.3f} seconds")
        satellite = api.EarthSatellite(self.TLE_line_1[closest_idx], self.TLE_line_2[closest_idx], ts=self.ts)
        state = satellite.at(self.ts.from_datetime(input_datetime))
        if state.message:
            raise ValueError(f"SGP4 propagation failed: {state.message}")
        if api.wgs84.height_of(state).m < 0:
            raise ValueError("Propagated satellite is below the WGS84 ellipsoid")
        return state
