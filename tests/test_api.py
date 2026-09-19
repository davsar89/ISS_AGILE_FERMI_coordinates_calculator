"""Public API, compatibility, and command-line integration checks."""
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from iss_coords import SatelliteCoordinates
from iss_coords.tle_data import DATA_DIR, SATELLITES
from satellite_coordinates import satellite_coordinates


class ApiChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sat = SatelliteCoordinates("ISS")
        cls.time = datetime(2019, 3, 24, tzinfo=timezone.utc)

    def test_one_propagation_quiet_result_and_compatibility(self):
        output = StringIO()
        with redirect_stdout(output), patch.object(self.sat, '_propagate', wraps=self.sat._propagate) as propagate:
            state = self.sat.at(self.time)
        self.assertEqual(propagate.call_count, 1)
        self.assertEqual(output.getvalue(), '')
        self.assertIs(satellite_coordinates, SatelliteCoordinates)
        payload = json.loads(json.dumps(state.to_dict(), allow_nan=False))
        self.assertEqual(payload['time_utc'], self.time.isoformat())
        self.assertAlmostEqual(state.tle_age_seconds, abs((self.time-state.tle_epoch_utc).total_seconds()), places=5)
        old = self.sat.get_satellite_coordinates(self.time)
        np.testing.assert_allclose(old[:3], [state.longitude_deg, state.latitude_deg, state.altitude_km])
        np.testing.assert_allclose(old[3]*old[4], state.velocity_ecef_km_s)
        np.testing.assert_allclose(self.sat.get_lvlh_frame(self.time), state.lvlh_ecef)

    def test_nearest_epoch_matches_scan(self):
        samples = np.linspace(self.sat.time_value[0]-86400, self.sat.time_value[-1]+86400, 100)
        for timestamp in samples:
            expected = int(np.argmin(np.abs(self.sat.time_value-timestamp)))
            actual, _ = self.sat.nearestDate(datetime.fromtimestamp(timestamp, timezone.utc))
            self.assertEqual(actual, expected)
        # Exact duplicate, equidistant, and endpoint choices retain argmin behavior.
        with patch.object(self.sat, 'time_value', np.array([0., 10., 10., 20.])):
            for timestamp in [-1, 0, 5, 10, 11, 15, 20, 21]:
                expected = int(np.argmin(abs(self.sat.time_value-timestamp)))
                self.assertEqual(self.sat.nearestDate(datetime.fromtimestamp(timestamp, timezone.utc))[0], expected)

    def test_external_unsorted_archive_and_missing_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/SATELLITES['ISS'][1]
            indices = [100, 0]
            path.write_text(''.join(self.sat.TLE_line_1[i]+'\n'+self.sat.TLE_line_2[i]+'\n' for i in indices))
            reader = SatelliteCoordinates('ISS', data_dir=directory)
            self.assertEqual(reader.coverage, (self.sat.datetimes[0], self.sat.datetimes[100]))
            self.assertEqual(reader.at(reader.coverage[0]).tle_age_seconds, 0)
            with self.assertRaisesRegex(ValueError, '14 days'):
                reader.at(reader.coverage[1]+timedelta(days=15))

    def test_cli_json_and_error_streams(self):
        command = [sys.executable, '-m', 'iss_coords', 'ISS']
        run = subprocess.run(command+[self.time.isoformat(), '--json', '--data-dir', str(DATA_DIR)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['satellite'], 'ISS')
        self.assertEqual(run.stderr, '')
        for date in ['not-a-time', '1900-01-01T00:00:00Z']:
            failed = subprocess.run(command+[date, '--json'], capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('Error:', failed.stderr)


if __name__ == '__main__':
    unittest.main()
