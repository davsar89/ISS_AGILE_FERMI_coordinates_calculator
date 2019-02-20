import pymap3d as pm
import re
import datetime
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import julian
import skyfield.sgp4lib as sgp4lib
from pathlib import Path

import sys

###### check python version, required >= 3.6
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    print("This script requires Python version >= 3.6")
    sys.exit(1)
######

class satellite_coordinates():
    ##

    def __init__(self, name):
        """
        :param name: satellite name, must be 'ISS' or 'Fermi'
        """
        self.name = name

        self.ISS_data_file = Path("./dataFiles/ISS_orbital_info_up_to_19_02_2019.txt")
        self.Fermi_data_file = Path("./dataFiles/Fermi_GLAST_orbital_info_up_to_19_02_2019.txt")
        self.AGILE_data_file = Path("./dataFiles/AGILE_orbital_info_up_to_19_02_2019.txt")

        if (self.name == "ISS"):
            self.data_file_path = self.ISS_data_file
        elif (self.name == "Fermi"):
            self.data_file_path = self.Fermi_data_file
        elif (self.name == "AGILE"):
            self.data_file_path = self.AGILE_data_file
        else:
            raise Exception("name input argument should be 'Fermi' or 'ISS' or 'AGILE' ")

        ## Loading TLE data
        with open(self.data_file_path, "r") as f:
            self.datafile = f.read()

        self.datetimes, self.dates_year, self.dates_doy, self.TLE_line_1, self.TLE_line_2 = self.read_data_using_regex()


    def nearestDate(self, date):

        dates_grid = self.datetimes
        timestemp_grid = [item.timestamp() for item in dates_grid]
        differences = np.abs(date.timestamp() - np.array(timestemp_grid))
        return np.argmin(differences)

    ##

    def read_data_using_regex(self):
        """
        convert textfile (txt) containing list of TLE of a given satellite to python lists of times and TLE
        :param txt: string containing the list of Two Line Elements obtained from www.space-track.org
        :return: datetimes : list of datetime read in the file
                 dates_year : list of corresponding years, redundant information with datetimes
                 dates_doy : list of corresponding days of year, redundant information with datetimes
                 TLE_line_1 : first line of TLE at given 'datetimes' date
                 TLE_line_2 : second line of TLE at given 'datetimes' date
        """
        txt = self.datafile

        re1 = '(1)'  # Any Single Character 1
        re2 = '(\\s+)'  # White Space 1
        re3 = '(\\d+)'  # Integer Number 1
        re4 = '(U)'  # Variable Name 1
        re5 = '.*?'  # Non-greedy match on filler
        re6 = '([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'  # Float 1

        rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6, re.IGNORECASE | re.DOTALL)

        m = rg.findall(txt)

        idx_date = 4

        dates_year = []
        dates_doy = []
        TLE_line_1 = []
        TLE_line_2 = []
        datetimes = []


        splited_txt = txt.split('\n')
        splited_txt.pop(-1)

        # sanity check
        if len(splited_txt)/2 != len(m):
            print(len(splited_txt)/2)
            print(len(m))
            raise Exception('error in function read_data_using_regex: splited_txt is not twice the size of m')

        for ii, sub_m in enumerate(m):

            year_raw = int(sub_m[idx_date][0:2])

            if year_raw>70:
                year_raw = 1900+year_raw
            else:
                year_raw = 2000 + year_raw

            dates_year.append(year_raw)
            dates_doy.append(float(sub_m[idx_date][2:]))
            TLE_line_1.append(splited_txt[ii*2])
            TLE_line_2.append(splited_txt[ii * 2+1])

            dt = datetime.timedelta(days=dates_doy[-1], seconds=0)
            datetime0 = datetime.datetime(year=dates_year[-1], month=1, day=1) + dt

            datetimes.append(datetime0)

        return datetimes, dates_year, dates_doy, TLE_line_1, TLE_line_2

    ##

    def get_satellite_coordinates(self, input_datetime):
        """
    Returns the longitude (deg), latitude (deg), altitude (km) of a satellite at a given time
        :param input_datetime: python datetime structure identifying the time where the coordinates of the satellite is wanted
        :return: longitude (deg), latitude (deg), altitude (km)
        """

        #input_datetime = datetime.datetime(year=2018, month=9, day=16, hour=13,minute=15,second=40)

        ## finding which TLE is the closest to the time we want

        closest_idx = self.nearestDate(input_datetime)

        line1 = self.TLE_line_1[closest_idx]
        line2 = self.TLE_line_2[closest_idx]

        satellite = twoline2rv(line1, line2, wgs72)

        position, velocity = satellite.propagate(input_datetime.year,
                                                 input_datetime.month,
                                                 input_datetime.day,
                                                 input_datetime.hour,
                                                 input_datetime.minute,
                                                 input_datetime.second)

        if (satellite.error!=0):    # nonzero on error
            raise Exception("error : something went wrong with the propagate fuction of sgp4 library")

        # WARNING: position and velocity are in the TEME coordinate system
        # Call SGP4 and obtain the position and velocity vectors in TEME
        # Convert the position and velocity vectors to latitude and longitude:
        # Rotate from the TEME to ECEF coordinate frames
        # Use the ECEF vectors to find latitude and longitude

        # Conversion from TEME to ITRS
        time_jd = julian.to_jd(input_datetime, fmt='jd')
        position, velocity = sgp4lib.TEME_to_ITRF(time_jd, np.asarray(position), np.asarray(velocity) * 86400)
        velocity = velocity / 86400

        lat, lon, alt = pm.ecef2geodetic(position[0] * 1000.0, position[1] * 1000.0, position[2] * 1000.0)
        alt = alt / 1000.0

        return lon, lat, alt