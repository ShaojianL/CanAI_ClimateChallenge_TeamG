"""Regression checks for the tab layout and extracted map functionality."""

import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import folium
from streamlit.testing.v1 import AppTest

from components.map_tab import (
    NO_REPORTS_COLOR, REPORT_COLORS, build_map, street_color,
)
from services.mock_reports import generate_mock_reports
from services.street_data import DataLoadError, load_data, validate_data

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def test_simulation_results_and_invalid_inputs(self):
        """Check hand-calculated output, retained results, and invalid submissions."""
        app = AppTest.from_file(str(APP_PATH)).run()
        app.button(key="FormSubmitter:street_simulation-Run simulation").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(
            app.tabs[1].dataframe[0].value["remaining_cm"].tolist(), [2, 4, 6]
        )
        app.run()
        self.assertEqual(len(app.tabs[1].dataframe), 1)
        for invalid in ("", "5,,3", "abc", "-1", "nan", "inf"):
            app.text_area[0].set_value(invalid)
            app.button(key="FormSubmitter:street_simulation-Run simulation").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.tabs[1].error), 1)
            self.assertEqual(len(app.tabs[1].dataframe), 0)
        app.text_area[0].set_value("5, 0")
        app.number_input[0].set_value(2.0)
        app.number_input[1].set_value(6.0)
        app.button(key="FormSubmitter:street_simulation-Run simulation").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(
            app.tabs[1].dataframe[0].value["remaining_cm"].tolist(), [2, 0]
        )

    def test_tabs_selection_and_sources(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [tab.label for tab in app.tabs], ["Map", "Simulation", "Dev note"]
        )
        self.assertIn("Run simulation", app.tabs[1].info[0].value)
        notes = "\n".join(item.value for item in app.tabs[2].markdown)
        self.assertIn("Map component progress", app.tabs[2].subheader[0].value)
        self.assertIn("Eight is our MVP scope, not a City data limit.", notes)
        self.assertIn("five-hour hackathon", notes)
        links = "\n".join(item.value for item in app.tabs[0].markdown)
        self.assertIn(
            "https://apps.stjohns.ca/snowclearing/StreetPriority.aspx", links
        )
        self.assertIn(
            "https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0",
            links,
        )

        app.tabs[0].multiselect[0].set_value(["WATER ST", "MILITARY RD"]).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [item.label for item in app.tabs[0].expander], ["WATER ST", "MILITARY RD"]
        )
        app.tabs[0].multiselect[0].set_value([]).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs[0].expander), 0)

    def test_map_data_failure_does_not_block_simulation(self):
        with patch(
            "components.map_tab.load_data",
            side_effect=DataLoadError("Missing pilot data"),
        ):
            app = AppTest.from_file(str(APP_PATH)).run()
        self.assertFalse(app.exception)
        self.assertIn("Missing pilot data", app.tabs[0].error[0].value)
        self.assertIn("Run simulation", app.tabs[1].info[0].value)
        self.assertEqual(app.tabs[2].header[0].value, "Dev note")

    def test_map_highlights_every_selected_segment(self):
        geojson, priorities = load_data()
        counts = Counter(report["street_name"] for report in generate_mock_reports())
        road_map = build_map(geojson, counts, ["WATER ST"])
        self.assertFalse(
            any(
                isinstance(child, folium.CircleMarker)
                for child in road_map._children.values()
            )
        )
        lines = [
            child for child in road_map._children.values()
            if isinstance(child, folium.PolyLine)
        ]
        expected_parts = sum(
            1 if feature["geometry"]["type"] == "LineString"
            else len(feature["geometry"]["coordinates"])
            for feature in geojson["features"]
        )
        self.assertEqual(len(lines), expected_parts)
        selected_count = sum(
            1 if feature["geometry"]["type"] == "LineString"
            else len(feature["geometry"]["coordinates"])
            for feature in geojson["features"]
            if feature["properties"]["STREETNAME"] == "WATER ST"
        )
        highlighted = [line for line in lines if line.options["weight"] == 8]
        self.assertEqual(len(highlighted), selected_count)
        self.assertTrue(all(line.options["opacity"] == 1.0 for line in highlighted))
        self.assertEqual(
            {line.options["color"] for line in lines},
            {NO_REPORTS_COLOR, *REPORT_COLORS},
        )
        for line in lines:
            tooltip = next(
                child.text for child in line._children.values()
                if isinstance(child, folium.Tooltip)
            )
            name, _ = tooltip.split(" — ")
            self.assertIn(f"{counts[name]} mock reports", tooltip)
            self.assertEqual(line.options["color"], street_color(counts[name]))

    def test_report_colour_thresholds(self):
        for count, expected in (
            (0, NO_REPORTS_COLOR), (1, REPORT_COLORS[0]), (9, REPORT_COLORS[0]),
            (10, REPORT_COLORS[1]), (29, REPORT_COLORS[1]),
            (30, REPORT_COLORS[2]), (65, REPORT_COLORS[2]),
        ):
            with self.subTest(count=count):
                self.assertEqual(street_color(count), expected)

    def test_mock_report_kpis_and_selected_details(self):
        expected_cards = [
            ("200", "Total reports"),
            ("200", "Distinct reporters"),
            ("7 / 8", "Pilot roads with reports"),
            ("65", "Most reported road: WATER ST"),
        ]
        with patch("components.map_tab.theme.render_kpi_row") as render_kpis:
            app = AppTest.from_file(str(APP_PATH)).run()
            self.assertFalse(app.exception)
            self.assertEqual(
                [(value, label) for value, label, _ in render_kpis.call_args.args[0]],
                expected_cards,
            )
            app.tabs[0].multiselect[0].set_value(["WATER ST", "SIGNAL HILL RD"]).run()
            self.assertFalse(app.exception)
            self.assertEqual(
                [(value, label) for value, label, _ in render_kpis.call_args.args[0]],
                expected_cards,
            )
        details = "\n".join(item.value for item in app.tabs[0].markdown)
        self.assertIn("Mock reports: 65", details)
        self.assertIn("Mock reports: 0", details)
        self.assertIn("Mock data preview", app.tabs[0].info[0].value)

    def test_invalid_geometry_is_rejected(self):
        with self.assertRaises(DataLoadError):
            validate_data({"type": "FeatureCollection", "features": []}, {})


if __name__ == "__main__":
    unittest.main()
