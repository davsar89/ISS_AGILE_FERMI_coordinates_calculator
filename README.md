## python script to retrieve GPS coordinates of three satellites (International Space Station (ISS), Fermi (GLAST) and AGILE) at any time

* **Requires python >=3.6**
* `satellite_coordinates.py` : Python script containing a class to get ISS or Fermi or AGILE coordinates (longitude in degrees, latitude in degrees, altitude in kilometers) at a given time.
The method (function) of the class called `get_satellite_coordinates` takes as input a time (that uses the Python `datetime` object), and outputs longitude (deg), latitude (deg), altitude (km), and velocity unit vector of the requested satellite.
* See `test.py` for usage example
* Python library requirements are indicated in the file `requirements.txt`. Run `pip install -r requirements.txt` to install them.

* The datafiles containing the list of Two Line Elements (TLE) of each satellites are contained in the folder `/dataFiles`. Now data is up to 22/12/2019.
* Other satellites can easily be added. TLE data can be downloaded at www.space-track.org (registration required).


## A MATLAB script to do the same is also available
* See the `/MATLAB` folder. The script `test.m` shows example usage.

