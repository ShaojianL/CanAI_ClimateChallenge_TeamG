"""Regression checks for the tab layout and extracted map functionality."""

import unittest
from pathlib import Path
from unittest.mock import patch

import folium
from streamlit.testing.v1 import AppTest

from components.map_tab import build_map, street_color, UNKNOWN_COLOR, MIXED_COLOR
from services.street_data import DataLoadError, load_data, validate_data

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def test_tabs_selection_and_sources(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [tab.label for tab in app.tabs], ["Map", "Simulation", "Dev note"]
        )
        self.assertIn("No simulation data exists yet.", app.tabs[1].info[0].value)
        notes = "\n".join(item.value for item in app.tabs[2].markdown)
        self.assertIn("Map component progress", app.tabs[2].subheader[0].value)
        self.assertIn("Eight is our MVP scope, not a City data limit.", notes)
        self.assertIn("five-hour hackathon", notes)
        links = "\n".join(item.value for item in app.sidebar.markdown)
        self.assertIn(
            "https://apps.stjohns.ca/snowclearing/StreetPriority.aspx", links
        )
        self.assertIn(
            "https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0",
            links,
        )

        app.sidebar.multiselect[0].set_value(["WATER ST", "MILITARY RD"]).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [item.label for item in app.tabs[0].expander], ["WATER ST", "MILITARY RD"]
        )
        app.sidebar.multiselect[0].set_value([]).run()
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
        self.assertIn("No simulation data exists yet.", app.tabs[1].info[0].value)
        self.assertEqual(app.tabs[2].header[0].value, "Dev note")

    def test_map_highlights_every_selected_segment(self):
        geojson, priorities = load_data()
        road_map = build_map(geojson, priorities, ["WATER ST"])
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
        self.assertEqual(street_color({}), UNKNOWN_COLOR)
        self.assertEqual(street_color({"priority": "mixed"}), MIXED_COLOR)

    def test_invalid_geometry_is_rejected(self):
        with self.assertRaises(DataLoadError):
            validate_data({"type": "FeatureCollection", "features": []}, {})


if __name__ == "__main__":
    unittest.main()
