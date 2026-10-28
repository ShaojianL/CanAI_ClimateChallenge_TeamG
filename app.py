"""SnowStorm AI — Map MVP (single-page Streamlit app).

Interactive map of a small pilot set of real St. John's streets with
verified municipal snow-clearing priorities, searchable multi-street
selection, and a reserved area for future simulation output.

Run:  .venv/bin/streamlit run app.py
"""

import json
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

DATA_DIR = Path(__file__).resolve().parent / "data"

PRIORITY_COLORS = {
    1: "#d62728",  # red — major/minor arterials
    2: "#ff7f0e",  # orange — collector streets
    3: "#1f77b4",  # blue — minor streets and cul-de-sacs
    4: "#9467bd",  # purple — city-maintained private lanes
}
MIXED_COLOR = "#8c6d31"  # olive — different priorities on different sections
UNKNOWN_COLOR = "#7f7f7f"  # gray — priority unavailable

PRIORITY_LABELS = {
    1: "Priority 1 — major and minor arterials",
    2: "Priority 2 — collector streets",
    3: "Priority 3 — minor streets and cul-de-sacs",
    4: "Priority 4 — private lanes maintained by the city",
}


@st.cache_data
def load_data():
    geojson = json.loads((DATA_DIR / "pilot_streets.geojson").read_text())
    priorities = json.loads((DATA_DIR / "street_priorities.json").read_text())
    return geojson, priorities


def street_color(info: dict) -> str:
    p = info.get("priority")
    if p == "mixed":
        return MIXED_COLOR
    if p in PRIORITY_COLORS:
        return PRIORITY_COLORS[p]
    return UNKNOWN_COLOR


def priority_text(info: dict) -> str:
    p = info.get("priority")
    if p == "mixed":
        levels = ", ".join(str(l) for l in info.get("priority_levels", []))
        return f"Mixed (priorities {levels} by section)"
    if p in PRIORITY_LABELS:
        return PRIORITY_LABELS[p]
    return "Priority unavailable"


def build_map(geojson: dict, priorities: dict, selected: list[str]) -> folium.Map:
    m = folium.Map(location=[47.566, -52.72], zoom_start=13, tiles="OpenStreetMap")

    bounds = []
    for feature in geojson["features"]:
        name = feature["properties"].get("STREETNAME", "")
        info = priorities.get(name, {})
        is_selected = name in selected
        coords = [(lat, lon) for lon, lat in feature["geometry"]["coordinates"]]
        if is_selected:
            bounds.extend(coords)
        folium.PolyLine(
            coords,
            color=street_color(info),
            weight=8 if is_selected else 3,
            opacity=1.0 if is_selected else 0.55,
            tooltip=f"{name} — {priority_text(info)}",
        ).add_to(m)

    if bounds:
        m.fit_bounds([
            [min(b[0] for b in bounds), min(b[1] for b in bounds)],
            [max(b[0] for b in bounds), max(b[1] for b in bounds)],
        ])
    return m


def main():
    st.set_page_config(page_title="SnowStorm AI — Map MVP", layout="wide")

    geojson, priorities = load_data()
    street_names = sorted(priorities.keys())

    # ---- Sidebar: search/selection, details, legend ----
    with st.sidebar:
        st.title("🌨️ SnowStorm AI")
        st.caption("Map MVP — St. John's pilot streets")

        selected = st.multiselect(
            "Search and select streets",
            options=street_names,
            placeholder="Type a street name…",
        )

        st.subheader("Legend")
        legend_rows = [(PRIORITY_COLORS[p], PRIORITY_LABELS[p]) for p in sorted(PRIORITY_COLORS)]
        legend_rows.append((MIXED_COLOR, "Mixed — varies by section"))
        legend_rows.append((UNKNOWN_COLOR, "Priority unavailable"))
        for color, label in legend_rows:
            st.markdown(
                f"<span style='color:{color}'>▬▬</span> {label}",
                unsafe_allow_html=True,
            )
        st.caption(
            "Priorities verified via the City of St. John's "
            "[street priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx). "
            "Geometry from the City's public ArcGIS road layer."
        )

    # ---- Main area: map + details ----
    col_map, col_details = st.columns([3, 1])

    with col_map:
        st_folium(
            build_map(geojson, priorities, selected),
            use_container_width=True,
            height=600,
            returned_objects=[],  # display-only: avoids reruns on map interaction
        )

    with col_details:
        st.subheader("Selected streets")
        if not selected:
            st.info("Use the sidebar to search and select streets.")
        for name in selected:
            info = priorities.get(name, {})
            with st.expander(name, expanded=True):
                st.markdown(f"**{priority_text(info)}**")
                if info.get("approx_length_m"):
                    st.markdown(f"Approx. length: **{info['approx_length_m']:,} m**")
                st.markdown(f"Segments: {info.get('segments', '?')}")
                for s in info.get("sections", []):
                    st.caption(f"P{s['priority']}: {s['section']}")

    # ---- Reserved area for future simulation output ----
    st.divider()
    st.subheader("Snow-depth simulation")
    st.info(
        "⏳ Simulated snow-depth graphs and a storm time selector will appear "
        "here in a later phase. No simulation data exists yet."
    )


if __name__ == "__main__":
    main()
