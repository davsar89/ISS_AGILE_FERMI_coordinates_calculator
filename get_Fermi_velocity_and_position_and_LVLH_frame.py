import datetime
from satellite_coordinates import satellite_coordinates
import os
import pyproj
import math
import numpy as np

#Fermi TEB: dt = '2009-12-14T11:53:27.83'

# test for ISS:
# 2019-Mar-24 00:31:53.135444
# should be close to 0.157454678525265    55.3015430661528

if __name__ == "__main__":

    #sat_coordinates = satellite_coordinates(name='ISS')
    sat_coordinates = satellite_coordinates(name='Fermi')

    #input_datetime = datetime.datetime(year=2019, month=3, day=24, hour=0, minute=31, second=53, microsecond=135444)
    input_datetime = datetime.datetime(year=2009, month=12, day=14, hour=11, minute=53, second=27, microsecond=830000)
    
    lon, lat, alt, v_vec, v_km_s = sat_coordinates.get_satellite_coordinates(input_datetime)

    X,Y,Z = self.gps_to_ecef_pyproj(lat, lon, alt)

    # Z: normalized inverted position vector
    LVLH_baseZ = np.array([-1.0*X,-1.0*Y,-1.0*Z])
    LVLH_baseZ = LVLH_baseZ/np.linalg.norm(LVLH_baseZ)

    v_vec = v_vec/np.linalg.norm(v_vec)

    # Y: Z cross velocity
    LVLH_baseY = np.cross(LVLH_baseZ, v_vec)
    LVLH_baseY = LVLH_baseY/np.linalg.norm(LVLH_baseY)
    # X: Y cross Z
    LVLH_baseX = np.cross(LVLH_baseY, LVLH_baseZ)
    LVLH_baseX = LVLH_baseX/np.linalg.norm(LVLH_baseX)

    print(f'Satellite name: {sat_coordinates.name}')
    print(f'Requested time: {input_datetime}')
    print(f'Longitude (deg), Latitude (deg), Altitude (km): {round(lon,4)}, {round(lat,4)}, {round(alt,4)}')
    print(f'Magnitude of velocity: {v_km_s:.4f} km/s')
    print(f'Velocity vector (ECEF, unit): {round(v_vec[0],8)}, {round(v_vec[1],8)}, {round(v_vec[2],8)}')
    print(f'Position vector (ECEF, unit): {round(LVLH_baseZ[0],8)}, {round(LVLH_baseZ[1],8)}, {round(LVLH_baseZ[2],8)}')
    print('     ')  
    print(f'LVLH base vector X (ECEF): {round(LVLH_baseX[0],8)}, {round(LVLH_baseX[1],8)}, {round(LVLH_baseX[2],8)}')
    print(f'LVLH base vector Y (ECEF): {round(LVLH_baseY[0],8)}, {round(LVLH_baseY[1],8)}, {round(LVLH_baseY[2],8)}')
    print(f'LVLH base vector Z (ECEF): {round(LVLH_baseZ[0],8)}, {round(LVLH_baseZ[1],8)}, {round(LVLH_baseZ[2],8)}')
    print('\n')

