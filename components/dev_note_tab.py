"""Brief development progress and map pilot scope."""

import streamlit as st


def render():
    st.header("Dev note")
    st.caption("Team: please read and update these notes as work progresses.")
    st.subheader("Map component progress")
    st.markdown(
        "- Interactive OpenStreetMap basemap with City road geometry.\n"
        "- Search and multi-select eight pilot streets; highlight their segments "
        "and show published clearing priorities and street details.\n"
        "- City source links and session data refresh are available in the sidebar.\n"
        "- Simulation is still a placeholder; no live snow depth or clearing-time "
        "predictions are available."
    )
    st.subheader("Why only eight pilot streets?")
    st.markdown(
        "The City's [street-priority lookup]"
        "(https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) has more streets. "
        "**Eight is our MVP scope, not a City data limit.** The project context "
        "recommended 5–10 streets; eight keeps geometry grouping and priority "
        "checks manageable within a five-hour hackathon.\n\n"
        "Search and refresh currently cover only this configured pilot set. "
        "Broader coverage needs additional geometry, politely paced per-street "
        "lookup requests, and checks for unmatched names and priority sections. "
        "Mixed-priority streets currently use one mixed color for the whole "
        "street; section boundaries are not yet matched to road segments."
    )
