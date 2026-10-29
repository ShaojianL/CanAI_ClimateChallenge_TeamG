"""Behaviour checks for the one-street simulation engine."""

import unittest

from services.simulation import simulate_street


class SimulationTests(unittest.TestCase):
    """Check hand-calculated results, model limits, and invalid inputs."""

    def test_agreed_example(self):
        """
        This function verifies that five cm snowfall minus three cm clearing
        leaves 2, 4, and 6 cm over three hours.
        """
        results = simulate_street([5, 5, 5], 1, 3)
        self.assertEqual([row["remaining_cm"] for row in results], [2, 4, 6])
        self.assertEqual([row["hour"] for row in results], [1, 2, 3])
        self.assertEqual([row["cleared_cm"] for row in results], [3, 3, 3])

    def test_zero_snowfall(self):
        """
        This function verifies that a dry street stays empty when clearing
        capacity is available.
        """
        self.assertEqual(simulate_street([0], 1, 3)[0]["remaining_cm"], 0)
        self.assertEqual(simulate_street([0], 1, 3)[0]["cleared_cm"], 0)

    def test_no_clearing(self):
        """
        This function verifies that snowfall accumulates unchanged when
        clearing capacity is zero.
        """
        results = simulate_street([2, 3], 1, 0)
        self.assertEqual([row["remaining_cm"] for row in results], [2, 5])

    def test_length_and_partial_clearing(self):
        """
        This function verifies that six cm-km of hourly capacity clears up to
        three cm per hour on a two km street without removing excess snow.
        """
        results = simulate_street([5, 0], 2, 6)
        self.assertEqual([row["remaining_cm"] for row in results], [2, 0])
        self.assertEqual([row["cleared_cm"] for row in results], [3, 2])

    def test_unused_capacity_is_not_saved(self):
        """
        This function verifies that unused capacity from a dry hour is not
        carried forward to a later hour.
        """
        results = simulate_street([0, 5], 1, 3)
        self.assertEqual(results[1]["remaining_cm"], 2)

    def test_empty_profile(self):
        """
        This function verifies that an empty snowfall profile produces no
        hourly results.
        """
        self.assertEqual(simulate_street([], 1, 3), [])

    def test_invalid_inputs(self):
        """
        This function verifies that invalid snowfall depths, street lengths,
        clearing capacities, and missing profiles are rejected.
        """
        for invalid in (-1, float("nan"), float("inf"), True, "3", None):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    simulate_street([invalid], 1, 3)
                with self.assertRaises(ValueError):
                    simulate_street([1], invalid, 3)
                with self.assertRaises(ValueError):
                    simulate_street([1], 1, invalid)
        with self.assertRaises(ValueError):
            simulate_street([1], 0, 3)
        with self.assertRaises(ValueError):
            simulate_street(None, 1, 3)

    def test_nonfinite_calculations(self):
        """
        This function verifies that extreme finite inputs are rejected when
        their calculations produce nonfinite values.
        """
        with self.assertRaises(ValueError):
            simulate_street([1e308, 1e308], 1, 0)
        with self.assertRaises(ValueError):
            simulate_street([1], 1e-308, 1e308)


if __name__ == "__main__":
    unittest.main()
