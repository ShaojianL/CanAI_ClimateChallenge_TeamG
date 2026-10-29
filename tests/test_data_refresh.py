"""Regression checks for refresh feedback and preservation of session data."""

import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from streamlit.testing.v1 import AppTest

from services.street_data import load_data

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class RefreshTests(unittest.TestCase):
    """Exercise refresh through the application using mocked City responses."""

    def test_success_preserves_selection_and_failure_keeps_data(self):
        """Accept valid data and keep it after network or validation failures."""
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertFalse(app.exception)
        app.tabs[0].multiselect[0].set_value(["WATER ST"]).run()
        dataset = load_data()
        with patch("components.data_refresh.fetch_pilot_data", return_value=dataset):
            app.button(key="refresh_data").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs[0].success), 1)
        self.assertEqual(app.session_state["refreshed_data"], dataset)
        self.assertEqual(app.session_state["selected_streets"], ["WATER ST"])

        response = requests.Response()
        response.status_code = 503
        failures = [
            (requests.Timeout(), "timed out"),
            (requests.ConnectionError(), "Could not connect"),
            (requests.HTTPError(response=response), "HTTP 503"),
            (requests.RequestException(), "request to the City's data service failed"),
            (ValueError(), "incomplete or invalid"),
        ]
        for error, message in failures:
            with self.subTest(error=type(error).__name__):
                with patch("components.data_refresh.fetch_pilot_data", side_effect=error):
                    app.button(key="refresh_data").click().run()
                self.assertFalse(app.exception)
                self.assertIn(message, app.tabs[0].error[0].value)
                self.assertEqual(app.session_state["refreshed_data"], dataset)
                self.assertEqual(app.session_state["selected_streets"], ["WATER ST"])

        with patch("components.data_refresh.fetch_pilot_data", return_value=({}, {})):
            app.button(key="refresh_data").click().run()
        self.assertFalse(app.exception)
        self.assertIn("incomplete or invalid", app.tabs[0].error[0].value)
        self.assertEqual(app.session_state["refreshed_data"], dataset)


if __name__ == "__main__":
    unittest.main()
