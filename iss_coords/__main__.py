"""Query a satellite at an ISO 8601 time, with optional JSON output."""
import argparse
from datetime import datetime
import json
from pathlib import Path

from . import SatelliteCoordinates
from .tle_data import SATELLITES


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("satellite", choices=SATELLITES)
    parser.add_argument("time", help="ISO 8601 timestamp; a missing offset means UTC")
    parser.add_argument("--data-dir", type=Path, help="Use external TLE archives")
    parser.add_argument("--json", action="store_true", help="Write one JSON object to stdout")
    args = parser.parse_args(argv)
    try:
        time = datetime.fromisoformat(args.time.replace("Z", "+00:00"))
        result = SatelliteCoordinates(args.satellite, data_dir=args.data_dir).at(time)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    if args.json:
        print(json.dumps(result.to_dict(), allow_nan=False))
    else:
        print(f"{result.satellite} at {result.time_utc.isoformat()}")
        print(f"Longitude: {result.longitude_deg:.6f} deg; latitude: {result.latitude_deg:.6f} deg; altitude: {result.altitude_km:.6f} km")
        print(f"ECEF velocity (km/s): {result.velocity_ecef_km_s.tolist()}")
        print(f"LVLH X/Y/Z (ECEF rows): {result.lvlh_ecef.tolist()}")
        print(f"TLE epoch: {result.tle_epoch_utc.isoformat()}; age: {result.tle_age_seconds:.3f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
