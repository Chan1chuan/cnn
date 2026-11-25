import unittest
from io import StringIO

from energy_window import measure_window, read_samples


class EnergyWindowTests(unittest.TestCase):
    def test_interpolated_boundaries_across_segments(self):
        points = [(0, 20), (1, 40), (2, 60), (3, 20)]
        result = measure_window(points, 0.5, 2.5)
        self.assertEqual(result["energy_mj"], 92.5)
        self.assertEqual(result["average_power_mw"], 46.25)
        self.assertEqual(result["duration_s"], 2)

    def test_window_wholly_inside_one_segment(self):
        result = measure_window([(0, 0), (4, 8)], 1, 3)
        self.assertEqual(result["energy_mj"], 8)

    def test_nonuniform_sampling_and_signed_power(self):
        result = measure_window([(0, -2), (1, 0), (4, 2)], 0, 4)
        self.assertEqual(result["energy_mj"], 2)

    def test_rejects_repeated_or_decreasing_time(self):
        for times in [(0, 1, 1), (0, 2, 1)]:
            with self.subTest(times=times), self.assertRaisesRegex(ValueError, "increasing"):
                measure_window(zip(times, [1, 1, 1]), 0, 1)

    def test_rejects_outside_or_empty_window(self):
        for start, end in [(-1, 1), (1, 3), (1, 1), (2, 0)]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                measure_window([(0, 1), (2, 3)], start, end)

    def test_rejects_nonfinite_samples(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            measure_window([(0, 1), (1, float("nan"))], 0, 1)

    def test_csv_can_include_extra_columns(self):
        result = read_samples(StringIO("power_mw,marker,time_s\n5,1,0\n7,0,2\n"))
        self.assertEqual(result, [(0, 5), (2, 7)])

    def test_csv_rejects_ambiguous_headers_and_missing_values(self):
        for contents in ["time_s,time_s,power_mw\n", "time_s,power_mw\n3\n"]:
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                read_samples(StringIO(contents))


if __name__ == "__main__":
    unittest.main()
