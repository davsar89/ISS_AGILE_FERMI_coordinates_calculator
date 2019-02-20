import datetime
from satellite_coordinates import satellite_coordinates

if __name__ == "__main__":


    iss_coordinates = satellite_coordinates(name='ISS')
    fermi_coordinates = satellite_coordinates(name='Fermi')
    agile_coordinates = satellite_coordinates(name='AGILE')

    input_datetime = datetime.datetime(year=2018, month=9, day=16, hour=13, minute=14, second=45)
    lon, lat, alt = iss_coordinates.get_satellite_coordinates(input_datetime)
    print('Satellite name : ', iss_coordinates.name)
    print('Requested time : ', input_datetime)
    print('Longitude (deg), Latitude (deg), Altitude (km) : ', lon, lat, alt)
    print('\n')

    input_datetime = datetime.datetime(year=2019, month=2, day=6, hour=3, minute=49, second=22)
    lon, lat, alt = iss_coordinates.get_satellite_coordinates(input_datetime)
    print('Satellite name : ', iss_coordinates.name)
    print('Requested time : ', input_datetime)
    print('Longitude (deg), Latitude (deg), Altitude (km) : ', lon, lat, alt)
    print('\n')

    input_datetime = datetime.datetime(year=2019, month=2, day=6, hour=3, minute=49, second=22)
    lon, lat, alt = fermi_coordinates.get_satellite_coordinates(input_datetime)
    print('Satellite name : ', fermi_coordinates.name)
    print('Requested time : ', input_datetime)
    print('Longitude (deg), Latitude (deg), Altitude (km) : ', lon, lat, alt)
    print('\n')

    input_datetime = datetime.datetime(year=2018, month=3, day=4, hour=2, minute=43, second=25)
    lon, lat, alt = agile_coordinates.get_satellite_coordinates(input_datetime)
    print('Satellite name : ', agile_coordinates.name)
    print('Requested time : ', input_datetime)
    print('Longitude (deg), Latitude (deg), Altitude (km) : ', lon, lat, alt)
    print('\n')