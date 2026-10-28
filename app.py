"""Single-page Streamlit entry point and tab layout.

Run: .venv/bin/streamlit run app.py
"""

import streamlit as st

from components import dev_note_tab, map_tab, simulation_tab


def main():
    st.set_page_config(page_title="Flurry", layout="wide")
    st.title("Flurry")

    map_view, simulation_view, dev_note_view = st.tabs(["Map", "Simulation", "Dev note"])
    with map_view:
        map_tab.render()
    with simulation_view:
        simulation_tab.render()
    with dev_note_view:
        dev_note_tab.render()


if __name__ == "__main__":
    main()
