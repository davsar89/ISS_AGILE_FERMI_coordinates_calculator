import sys

###### check python version, required >= 3.6
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    print("This script requires Python version >= 3.6")
    sys.exit(1)
######
import calendar
import re
import datetime
import numpy as np
import skyfield.sgp4lib as sgp4lib
from pathlib import Path
from skyfield import api
import pyproj
import math

######

class satellite_coordinates:
    ##

    def __init__(self, name):
        """
        :param name: satellite name, must be 'ISS' or 'Fermi'
        """
        self.name = name

        self.ISS_data_file = Path("./dataFiles/ISS_orbital_info.txt")
        self.Fermi_data_file = Path("./dataFiles/Fermi_GLAST_orbital_info.txt")
        self.AGILE_data_file = Path("./dataFiles/AGILE_orbital_info.txt")

        if self.name == "ISS":
            self.data_file_path = self.ISS_data_file
        elif self.name == "Fermi":
            self.data_file_path = self.Fermi_data_file
        elif self.name == "AGILE":
            self.data_file_path = self.AGILE_data_file
        else:
            raise Exception("name input argument should be 'Fermi' or 'ISS' or 'AGILE' ")

        self.datetimes, self.TLE_line_1, self.TLE_line_2 = self.read_satellite_TLE_data(self.data_file_path)

        self.time_value = np.array([calendar.timegm(dt.utctimetuple()) for dt in self.datetimes])

        self.ts = api.load.timescale()

        self.ecef = pyproj.Proj(proj='geocent', ellps='WGS84')
        self.lla = pyproj.Proj(proj='latlong', ellps='WGS84')

        self.au_to_Km = 149597870.700
        self.day_to_seconds = 86400.0

    ##
    def gps_to_ecef(self, lat, lon, alt):
        """
        Inputs:
          - lon, lat in degrees
          - alt in meters
        Outputs:
          - x,y,z in meters
        """
        x, y, z = pyproj.transform(self.lla, self.ecef, lon, lat, alt, radians=False)
        return x, y, z
    
    def ecef_to_gps(self, x, y, z):
        """
        Inputs:
          - x,y,z in meters
        Outputs:
          - lon, lat in degrees
          - alt in meters
        """
        lon, lat, alt = pyproj.transform(self.ecef, self.lla, x, y, z, radians=False)
        return lon, lat, alt 

    ##

    def nearestDate(self, base):
        base_timestamp = calendar.timegm(base.utctimetuple())
        differences = np.abs(base_timestamp - self.time_value)
        # print(differences)
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
        TLE_line_1 = []
        TLE_line_2 = []
        datetimes = []

        with open(data_file_path, "r") as f:
            while True:
                line1 = f.readline().strip()
                if not line1:
                    break
                line2 = f.readline().strip()
                if not line2:
                    break

                TLE_line_1.append(line1)
                TLE_line_2.append(line2)

                epoch_str = line1[18:32]
                year_tle = int(epoch_str[:2]) + (1900 if int(epoch_str[:2]) > 70 else 2000)
                DOY = int(epoch_str[2:5])

                day_fraction = float(epoch_str[5:]) / (10**len(epoch_str[5:]))  # Normalize the fractional day
                date = datetime.datetime(year=year_tle, month=1, day=1) + datetime.timedelta(days=DOY-1 + day_fraction)

                datetimes.append(date)

        return datetimes, TLE_line_1, TLE_line_2

    ##

    def get_satellite_coordinates(self, input_datetime):
        """
    Calculates the longitude (deg), latitude (deg), altitude (km) and velocity vector (normalized + magntitude in km/s) of a satellite at a given time
        :param input_datetime: python datetime structure identifying the time where the coordinates of the satellite is wanted
        :return: longitude (deg), latitude (deg), altitude (km), velocity vector (normalized), magnitude of the velocity vector (in km/s)
        """
        
        ## finding which TLE is the closest to the time we want

        closest_idx, delta_t = self.nearestDate(input_datetime)

        print(f"Closest TLE has a delta time of: {delta_t} seconds")

        line1 = self.TLE_line_1[closest_idx]
        line2 = self.TLE_line_2[closest_idx]

        satellite = sgp4lib.EarthSatellite(line1, line2)

        tttt = self.ts.utc(input_datetime.year, input_datetime.month, input_datetime.day, input_datetime.hour,
                      input_datetime.minute, input_datetime.second + input_datetime.microsecond/1.0e6)

        # tttt = ts.utc(input_datetime.year, input_datetime.month, input_datetime.day, input_datetime.hour,
                      # input_datetime.minute, input_datetime.second)

        position, velocity, error = satellite.ITRF_position_velocity_error(tttt)

        norm_velocity = math.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2)

        norm_velocity_km_s = norm_velocity*self.au_to_Km/self.day_to_seconds

        v_vec_itrf = velocity / norm_velocity # unit vector

        position = np.asarray(position) * self.au_to_Km * 1000.0    # to meters

        lon, lat, alt = self.ecef_to_gps(position[0], position[1], position[2])
        alt = alt / 1000.0 # to kilometers

        return lon, lat, alt, v_vec_itrf, norm_velocity_km_s
