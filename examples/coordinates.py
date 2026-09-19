"""Reuse an archive reader to query any supported datetime."""
from datetime import datetime, timezone
from iss_coords import SatelliteCoordinates


def main():
    when = datetime(2019, 3, 24, 0, 31, 52, 335180, tzinfo=timezone.utc)
    for name in ("ISS", "Fermi", "AGILE"):
        satellite = SatelliteCoordinates(name)
        state = satellite.at(when)
        print(name, state.time_utc.isoformat())
        print("Longitude, latitude, altitude (deg, deg, km):",
              state.longitude_deg, state.latitude_deg, state.altitude_km)
        print("ECEF velocity (km/s):", state.velocity_ecef_km_s)
        print("LVLH X/Y/Z (ECEF rows):", state.lvlh_ecef)


if __name__ == "__main__":
    main()
