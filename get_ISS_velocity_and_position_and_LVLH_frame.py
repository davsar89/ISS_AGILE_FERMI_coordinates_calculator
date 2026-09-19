import datetime
from satellite_coordinates import satellite_coordinates

if __name__ == "__main__":

    iss_coordinates = satellite_coordinates(name='ISS')

    # 2019-Mar-24 00:31:53.135444
    # 0.157454678525265    55.3015430661528

    input_datetime = datetime.datetime(year=2019, month=3, day=24, hour=0, minute=31, second=53, microsecond=135444)

    lon, lat, alt, v_vec, v_km_s = iss_coordinates.get_satellite_coordinates(input_datetime)

    LVLH_baseX, LVLH_baseY, LVLH_baseZ = iss_coordinates.get_lvlh_frame(input_datetime)

    print(f'Satellite name: {iss_coordinates.name}')
    print(f'Requested time: {input_datetime}')
    print(f'Longitude (deg), Latitude (deg), Altitude (km): {round(lon,4)}, {round(lat,4)}, {round(alt,4)}')
    print(f'Magnitude of velocity: {v_km_s:.4f} km/s')
    print(f'Velocity vector (ECEF, unit): {round(v_vec[0],8)}, {round(v_vec[1],8)}, {round(v_vec[2],8)}')
    print(f'Nadir vector (ECEF, unit): {round(LVLH_baseZ[0],8)}, {round(LVLH_baseZ[1],8)}, {round(LVLH_baseZ[2],8)}')
    print('     ')  
    print(f'LVLH base vector X (ECEF): {round(LVLH_baseX[0],8)}, {round(LVLH_baseX[1],8)}, {round(LVLH_baseX[2],8)}')
    print(f'LVLH base vector Y (ECEF): {round(LVLH_baseY[0],8)}, {round(LVLH_baseY[1],8)}, {round(LVLH_baseY[2],8)}')
    print(f'LVLH base vector Z (ECEF): {round(LVLH_baseZ[0],8)}, {round(LVLH_baseZ[1],8)}, {round(LVLH_baseZ[2],8)}')
    print('\n')

