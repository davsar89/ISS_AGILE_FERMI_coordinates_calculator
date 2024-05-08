## Python script to retrieve GPS coordinates and ECEF velocity vectors of three satellites (International Space Station (ISS), Fermi (GLAST) and AGILE) at any time

* **Requires python >=3.6**
* `satellite_coordinates.py` : Python script containing a class to get ISS or Fermi or AGILE coordinates (longitude in degrees, latitude in degrees, altitude in kilometers) at a given time.
The method (function) of the class called `get_satellite_coordinates` takes as input a time (that uses the Python `datetime` object), and outputs longitude (deg), latitude (deg), altitude (km), and velocity unit vector of the requested satellite.
* See `test.py` for usage example
* Python library requirements are indicated in the file `requirements.txt`. Run `pip install -r requirements.txt` to install them.

* The datafiles containing the list of Two Line Elements (TLE) of each satellites are contained in the folder `/dataFiles`. Now data is up to 08/05/2024.
* Other satellites can easily be added and TLE can be updated to later times. TLE data can be downloaded at www.space-track.org (registration required).

* Examle output results:
```
## $ python get_Fermi_velocity_and_position_and_LVLH_frame.py 

Closest TLE has a delta time of: 42807 seconds
Satellite name: Fermi
Requested time: 2009-12-14 11:53:27.830000
Longitude (deg), Latitude (deg), Altitude (km): 31.5278, 25.4978, 541.8405
Magnitude of velocity: 7.1459 km/s
Velocity vector (ECEF, unit): -0.54403662, 0.83714255, 0.05671429
Position vector (ECEF, unit): -0.77031809, -0.47256655, -0.42812487
     
LVLH base vector X (ECEF): -0.54465699, 0.83676235, 0.05636962
LVLH base vector Y (ECEF): 0.33160038, 0.27660374, -0.90195985
LVLH base vector Z (ECEF): -0.77031809, -0.47256655, -0.42812487

## $ python get_ISS_velocity_and_position_and_LVLH_frame.py 

Closest TLE has a delta time of: 1913 seconds
Satellite name: ISS
Requested time: 2019-03-24 00:31:53.135444
Longitude (deg), Latitude (deg), Altitude (km): 55.34, 0.1005, 408.5944
Magnitude of velocity: 7.3713 km/s
Velocity vector (ECEF, unit): -0.4741659, 0.33092602, -0.81587662
Position vector (ECEF, unit): -0.56870392, -0.82254047, -0.00174317
     
LVLH base vector X (ECEF): -0.47480191, 0.33000677, -0.81587908
LVLH base vector Y (ECEF): 0.67166882, -0.46316597, -0.57821993
LVLH base vector Z (ECEF): -0.56870392, -0.82254047, -0.00174317

```
