"""Verify the synthetic preview has exactly 200 different fictional reporters."""

import unittest
from collections import Counter

from services.mock_reports import MOCK_REPORT_COUNTS, generate_mock_reports
from services.street_data import load_data


class MockReportTests(unittest.TestCase):
    def test_exact_people_distribution_and_pilot_membership(self):
        reports = generate_mock_reports()
        self.assertEqual(len(reports), 200)
        self.assertEqual(len({r["reporter_id"] for r in reports}), 200)
        self.assertEqual(len({r["report_id"] for r in reports}), 200)
        self.assertTrue(all(r["source"] == "mock" for r in reports))
        counts = Counter(r["street_name"] for r in reports)
        self.assertEqual(
            counts, {name: count for name, count in MOCK_REPORT_COUNTS.items() if count}
        )
        _, priorities = load_data()
        self.assertEqual(set(MOCK_REPORT_COUNTS), set(priorities))
        self.assertEqual(generate_mock_reports(), reports)


if __name__ == "__main__":
    unittest.main()
