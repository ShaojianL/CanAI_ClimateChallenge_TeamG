"""Session-only street refresh controls, accessible styling, and user feedback."""

import requests
import streamlit as st

from scripts.fetch_pilot_streets import fetch_pilot_data
from services.street_data import validate_data


def render():
    """Render refresh controls in the current container and retain data on failure.

    Successful responses are validated before replacing the session dataset.
    Saved startup files are never changed.
    """
    st.html("""
        <style>
        .st-key-refresh_data button {
            min-height: 44px;
            border: 2px solid #2847A1;
        }
        .st-key-refresh_data button:hover {
            background-color: #2847A1;
            border-color: #2847A1;
            color: #FFFFFF;
        }
        .st-key-refresh_data button:focus-visible {
            outline: 3px solid #26374A;
            outline-offset: 3px;
        }
        </style>
    """)

    st.subheader("Street data")
    st.caption(
        "Fetch the eight pilot streets from the City's public sources. "
        "Refresh applies to this session; saved files remain unchanged. "
        "Requests may take several minutes."
    )
    if st.button("Fetch / refresh data", key="refresh_data", width="stretch"):
        try:
            with st.spinner("Fetching pilot streets and priorities from the City…"):
                refreshed_geojson, refreshed_priorities = fetch_pilot_data()
                validate_data(refreshed_geojson, refreshed_priorities)
            st.session_state["refreshed_data"] = (
                refreshed_geojson, refreshed_priorities
            )
            st.success("Street data refreshed for this session.")
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            if isinstance(exc, requests.Timeout):
                reason = "The City's data service timed out."
            elif isinstance(exc, requests.ConnectionError):
                reason = "Could not connect to the City's data service."
            elif isinstance(exc, requests.HTTPError):
                reason = "The City's data service returned an HTTP error."
                if exc.response is not None:
                    reason = (
                        "The City's data service returned HTTP "
                        f"{exc.response.status_code}."
                    )
            elif isinstance(exc, requests.RequestException):
                reason = "The request to the City's data service failed."
            else:
                reason = "The returned street data was incomplete or invalid."
            st.error(
                f"Refresh failed. {reason} The current dataset has been kept. "
                "Check your connection and try again later."
            )
    if "refreshed_data" in st.session_state:
        st.caption("Using data fetched during this session. Verification dates are not recorded.")
    else:
        st.caption("Using the saved local pilot dataset.")
