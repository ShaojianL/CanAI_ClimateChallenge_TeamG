"""Single-page Streamlit entry point and tab layout.

Run: .venv/bin/streamlit run app.py
"""

import streamlit as st

from components import map_tab, simulation_tab


def main():
    st.set_page_config(page_title="Flurry", layout="wide")
    st.title("Flurry")

    map_view, simulation_view = st.tabs(["Map", "Simulation"])
    with map_view:
        map_tab.render()
    with simulation_view:
        simulation_tab.render()


if __name__ == "__main__":
    main()
