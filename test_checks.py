"""Run offline with: python -m unittest -v test_checks"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
from skyfield import api

from satellite_coordinates import satellite_coordinates
from tle_data import DATA_DIR, SATELLITES, parse_tles, tle_epoch
from update_TLE_data import atomic_write, update


class PhysicsChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.satellites = [satellite_coordinates(name) for name in SATELLITES]

    def test_epoch_fraction_and_year_pivot(self):
        for year, expected in [(56, 2056), (57, 1957), (70, 1970), (0, 2000)]:
            line = ' ' * 18 + f'{year:02d}001.50000000'
            self.assertEqual(tle_epoch(line), datetime(expected, 1, 1, 12, tzinfo=timezone.utc))
        for sat in self.satellites:
            first = sat.TLE_line_1[-1]
            second = sat.TLE_line_2[-1]
            reference = api.EarthSatellite(first, second, ts=sat.ts).epoch.utc_datetime()
            self.assertLess(abs((tle_epoch(first) - reference).total_seconds()), 1e-4)

    def test_real_states_geometry_velocity_and_timezone(self):
        for sat in self.satellites:
            # AGILE's final record is near decay; use a representative 2019 orbit.
            dates = [datetime(2019, 3, 24, tzinfo=timezone.utc)]
            if sat.name != 'AGILE':
                # Stay away from nearest-TLE selection boundaries: independent
                # orbit fits can be discontinuous even at almost identical epochs.
                dates.append(max(sat.datetimes) + timedelta(seconds=60))
            for date in dates:
                lon, lat, alt, direction, speed = sat.get_satellite_coordinates(date)
                self.assertTrue(100 < alt < 1000)
                self.assertTrue(6 < speed < 9)
                self.assertAlmostEqual(np.linalg.norm(direction), 1)
                xyz = np.array(sat.gps_to_ecef(lat, lon, alt * 1000))
                np.testing.assert_allclose(sat.ecef_to_gps(*xyz), [lon, lat, alt * 1000], atol=0.005)
                state = sat._propagate(date)
                reference = api.wgs84.geographic_position_of(state)
                np.testing.assert_allclose([lon, lat, alt], [reference.longitude.degrees,
                    reference.latitude.degrees, reference.elevation.km], atol=1e-6)
                # Earth-fixed velocity must equal the finite difference of ECEF position.
                positions = []
                for offset in [-0.5, 0.5]:
                    lo, la, al, _, _ = sat.get_satellite_coordinates(date + timedelta(seconds=offset))
                    positions.append(np.array(sat.gps_to_ecef(la, lo, al * 1000)))
                np.testing.assert_allclose((positions[1] - positions[0]) / 1000,
                                           direction * speed, atol=5e-5, rtol=0)
                shifted = date.astimezone(timezone(timedelta(hours=2)))
                np.testing.assert_allclose(sat.get_satellite_coordinates(shifted)[:3], [lon, lat, alt], atol=1e-9)
                frame = sat.get_lvlh_frame(date)
                np.testing.assert_allclose(frame @ frame.T, np.eye(3), atol=1e-12)
                self.assertAlmostEqual(np.linalg.det(frame), 1)
                np.testing.assert_allclose(frame[2], -xyz / np.linalg.norm(xyz), atol=1e-9)
                # Inertial angular momentum is normal to the LVLH orbital plane.
                from skyfield.framelib import itrs
                h = itrs.rotation_at(state.t) @ np.cross(state.xyz.km, state.velocity.km_per_s)
                np.testing.assert_allclose(frame[1], -h / np.linalg.norm(h), atol=1e-12)

    def test_stale_tle_rejected(self):
        for sat in self.satellites:
            with self.assertRaises(ValueError):
                sat.get_satellite_coordinates(max(sat.datetimes) + timedelta(days=15))


class DownloadChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.records = {}
        for name, (norad, filename) in SATELLITES.items():
            pairs = parse_tles((DATA_DIR / filename).read_text(), norad)
            self.records[name] = ['\n'.join(p) + '\n' for p in pairs[-2:]]
            (self.root / filename).write_text(self.records[name][0])

    def test_merge_cache_and_history_checkpoint(self):
        client = Mock()
        client.gp.return_value = ''.join(v[1] for v in self.records.values())
        update(client, self.root)
        for name, (norad, filename) in SATELLITES.items():
            self.assertEqual(len(parse_tles((self.root / filename).read_text(), norad)), 2)
        update(client, self.root)
        self.assertEqual(client.gp.call_count, 1)
        client.gp_history.return_value = ''
        update(client, self.root, history=True)
        first_query = client.gp_history.call_args_list[0].kwargs
        self.assertEqual(first_query['epoch'], '>' + tle_epoch(self.records['ISS'][0]).date().isoformat())
        self.assertIn('history', json.loads((self.root / 'last_update_TLE.json').read_text()))

    def test_invalid_download_and_failed_replace_preserve_data(self):
        filename = self.root / SATELLITES['ISS'][1]
        original = filename.read_bytes()
        client = Mock()
        client.gp.return_value = '<html>login failed</html>'
        with self.assertRaises(ValueError):
            update(client, self.root)
        self.assertEqual(filename.read_bytes(), original)
        with patch('update_TLE_data.os.replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                atomic_write(filename, 'replacement')
        self.assertEqual(filename.read_bytes(), original)
        self.assertFalse((self.root / 'last_update_TLE.json').exists())

    def test_invalid_tle(self):
        text = self.records['ISS'][0]
        with self.assertRaises(ValueError):
            parse_tles(text.splitlines()[0])
        with self.assertRaises(ValueError):
            parse_tles(text, 33053)
        with self.assertRaises(ValueError):
            parse_tles(text[:68] + str((int(text[68]) + 1) % 10) + text[69:])


if __name__ == '__main__':
    unittest.main()
