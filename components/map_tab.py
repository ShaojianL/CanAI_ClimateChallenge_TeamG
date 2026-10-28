"""Map tab: street selection, priority styling, and road details."""

import folium
import streamlit as st
from streamlit_folium import st_folium

from services.street_data import DataLoadError, load_data

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


def street_color(info: dict) -> str:
    """
    This program chooses the map color for a street's priority.

    Parameters:
        info: Available priority information for the street.
    Returns:
        The color for a known, mixed, or unavailable priority.
    """
    p = info.get("priority")
    if p == "mixed":
        return MIXED_COLOR
    if p in PRIORITY_COLORS:
        return PRIORITY_COLORS[p]
    return UNKNOWN_COLOR


def priority_text(info: dict) -> str:
    """
    This program describes a street's snow-clearing priority.

    Parameters:
        info: Available priority information for the street.
    Returns:
        A readable priority label, including mixed or unavailable states.
    """
    p = info.get("priority")
    if p == "mixed":
        levels = ", ".join(str(l) for l in info.get("priority_levels", []))
        return f"Mixed (priorities {levels} by section)"
    if p in PRIORITY_LABELS:
        return PRIORITY_LABELS[p]
    return "Priority unavailable"


def build_map(geojson: dict, priorities: dict, selected: list[str]) -> folium.Map:
    """
    This program draws all road parts and highlights the selected streets.

    Parameters:
        geojson: Validated road FeatureCollection.
        priorities: Validated priority information by street name.
        selected: Names of streets to highlight and include in map bounds.
    Returns:
        A Folium map containing the pilot roads.
    """
    m = folium.Map(location=[47.566, -52.72], zoom_start=13, tiles="OpenStreetMap")

    bounds = []
    for feature in geojson["features"]:
        name = feature["properties"].get("STREETNAME", "")
        info = priorities.get(name, {})
        is_selected = name in selected
        geometry = feature["geometry"]

        # Draw each part separately to avoid connecting disjoint road sections
        parts = (
            [geometry["coordinates"]]
            if geometry["type"] == "LineString"
            else geometry["coordinates"]
        )
        for part in parts:

            # GeoJSON uses longitude first, while Folium expects latitude first
            coords = [(point[1], point[0]) for point in part]
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


def render():
    """
    This program displays the street map, selection controls, and street details.

    Parameters:
        None.
    Returns:
        None. Renders the Streamlit interface.
    """
    # Stop before drawing a partial or misleading map when required data fails
    try:
        geojson, priorities = load_data()
    except DataLoadError as exc:
        st.error(f"Street data could not be loaded. {exc}")
        return
    street_names = sorted(priorities.keys())

    # ---- Sidebar: search/selection, details, legend ----
    with st.sidebar:
        st.caption("Map controls — St. John's pilot streets")

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
        st.subheader("Data sources")
        st.markdown(
            "- [City snow-clearing priority lookup form]"
            "(https://apps.stjohns.ca/snowclearing/StreetPriority.aspx)\n"
            "- [City road geometry (ArcGIS REST API)]"
            "(https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0)"
        )
        st.caption(
            "Road geometry and priorities are saved locally, not updated live."
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
