# python script to retrieve International Space Station (ISS) or Fermi satellite (GLAST) coordinates at any time

- `satellite_coordinates.py` : Python script containing a class to get ISS or Fermi coordinates (longitude in degrees, latitude in degrees, altitude in kilometers) at a given time.
The method (function) of the class called `get_satellite_coordinates` takes input time that uses the Python `datetime` object.

- See `test.py` for usage example

- the datafiles with the Two Line Elements (TLE) data of ISS and Fermi are contained in the folder `/dataFiles`. Now up to 19/02/2019.

- Other satellites can easily be added. TLE data can be downloaded at www.space-track.org (registration required).

- Python lirbary requirements are indicated `requirements.txt` . Run `pip install -r requirements.txt` to install them.
