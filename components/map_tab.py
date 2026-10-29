"""Map tab: statistic cards, street controls, priority map, and source details."""

import folium
import streamlit as st
from streamlit_folium import st_folium

from components import data_refresh, theme
from services.street_data import DataLoadError, load_data

PRIORITY_COLORS = {
    1: "#d62728",  # red — major/minor arterials
    2: "#ff7f0e",  # orange — collector streets
    3: "#1f77b4",  # blue — minor streets and cul-de-sacs
    4: "#9467bd",  # purple — city-maintained private lanes
}
MIXED_COLOR = "#8c6d31"  # olive — different priorities on different sections
UNKNOWN_COLOR = "#7f7f7f"  # gray — priority unavailable

# ArcGIS PointAddress match for 25 Blackler Avenue; not a verified vehicle entrance.
DEPOT_LOCATION = (47.546909, -52.741242)
DEPOT_LABEL = "Assumed starting depot — 25 Blackler Avenue"
DEPOT_ASSUMPTION = (
    "All simulated plows start here. Actual dispatch locations are unverified."
)

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

    folium.CircleMarker(
        location=DEPOT_LOCATION,
        radius=12,
        color="#ffffff",
        weight=3,
        fill=True,
        fill_color="#172b4d",
        fill_opacity=1.0,
        tooltip=DEPOT_LABEL,
        popup=f"{DEPOT_LABEL}<br>{DEPOT_ASSUMPTION}",
    ).add_to(m)

    bounds = [DEPOT_LOCATION]
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

    if selected:
        m.fit_bounds([
            [min(b[0] for b in bounds), min(b[1] for b in bounds)],
            [max(b[0] for b in bounds), max(b[1] for b in bounds)],
        ])
    return m


def render():
    """
    This program displays statistic cards, street controls, the map, and details.

    Parameters:
        None.
    Returns:
        None. Renders the Streamlit interface.
    """
    # Stop before drawing a partial or misleading map when required data fails
    try:
        if "refreshed_data" in st.session_state:
            geojson, priorities = st.session_state["refreshed_data"]
        else:
            geojson, priorities = load_data()
    except DataLoadError as exc:
        st.error(f"Street data could not be loaded. {exc}")
        return
    street_names = sorted(priorities.keys())

    # Keep valid selections when the refreshed source changes its street list.
    if "selected_streets" in st.session_state:
        st.session_state["selected_streets"] = [
            name for name in st.session_state["selected_streets"]
            if name in street_names
        ]

    # Session state already holds this run's selection before widgets render,
    # so the statistic cards above the controls stay in step with it
    selected_count = len(st.session_state.get("selected_streets", []))
    priority_one = sum(
        1 for info in priorities.values() if info.get("priority") == 1
    )
    mixed = sum(
        1 for info in priorities.values() if info.get("priority") == "mixed"
    )
    theme.render_kpi_row([
        (len(street_names), "Pilot streets", theme.GC_ACCENT),
        (selected_count, "Streets selected", theme.GC_LINK),
        (priority_one, "Priority 1 arterials", theme.GC_ERROR_RED),
        (mixed, "Mixed-priority streets", theme.GC_WARNING),
    ])
    st.caption(
        "Planning context only. Priority colours do not represent current road "
        "conditions, travel safety, or simulated snow depth."
    )

    # ---- Left controls and legend beside the large map card ----
    controls_col, map_col = st.columns([1, 3], gap="medium")

    with controls_col:
        with st.container(border=True, key="card-controls"):
            st.subheader("Street controls")
            selected = st.multiselect(
                "Search and select streets",
                options=street_names,
                placeholder="Type a street name…",
                key="selected_streets",
            )
            data_refresh.render()

        with st.container(border=True, key="card-legend"):
            st.subheader("Legend")
            legend_rows = [(PRIORITY_COLORS[p], PRIORITY_LABELS[p]) for p in sorted(PRIORITY_COLORS)]
            legend_rows.append((MIXED_COLOR, "Mixed — varies by section"))
            legend_rows.append((UNKNOWN_COLOR, "Priority unavailable"))
            for color, label in legend_rows:
                st.markdown(
                    f"<span style='color:{color}'>▬▬</span> {label}",
                    unsafe_allow_html=True,
                )
            st.caption("Mixed priorities vary by section. Grey means priority unavailable.")

            st.subheader("Data sources")
            st.markdown(
                "- [City snow-clearing priority lookup form]"
                "(https://apps.stjohns.ca/snowclearing/StreetPriority.aspx)\n"
                "- [City road geometry (ArcGIS REST API)]"
                "(https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0)"
            )

    with map_col:
        with st.container(border=True, key="card-map"):
            st.subheader("Interactive pilot street map")
            st.caption(
                "Search and select streets in Street controls. Selected streets use "
                "thicker lines; their priority and section details are also available "
                "as text."
            )
            st.caption(f"Large dark dot: {DEPOT_LABEL}. {DEPOT_ASSUMPTION}")
            st_folium(
                build_map(geojson, priorities, selected),
                use_container_width=True,
                height=620,
                returned_objects=[],  # display-only: avoids reruns on map interaction
            )

    with st.container(border=True, key="card-selected"):
        st.subheader("Selected streets")
        st.caption(f"{len(selected)} of {len(street_names)} pilot streets selected")
        if not selected:
            st.info("Use Street controls to search and select streets.")
        for name in selected:
            info = priorities.get(name, {})
            with st.expander(name, expanded=True):
                st.markdown(f"**{priority_text(info)}**")
                if info.get("approx_length_m") is not None:
                    st.markdown(f"Approx. length: **{info['approx_length_m']:,} m**")
                else:
                    st.write("Length unavailable")
                if info.get("segments") is not None:
                    st.write(f"Segments: {info['segments']:,}")
                else:
                    st.write("Segment count unavailable")
                for s in info.get("sections", []):
                    st.write(f"Priority {s['priority']}: {s['section']}")
                source = info.get("priority_source")
                if (
                    isinstance(source, str)
                    and source == "https://apps.stjohns.ca/snowclearing/StreetPriority.aspx"
                ):
                    st.link_button("View recorded priority source", source)
                else:
                    st.caption("Priority source unavailable")

    with st.container(border=True, key="card-limitations"):
        st.subheader("Data sources and limitations")
        st.markdown(
            "**Road geometry:** [City of St. John's public ArcGIS road layer]"
            "(https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0). "
            "The map displays a pilot snapshot loaded from saved files or fetched "
            "using the refresh button in Street controls, not a live road-conditions "
            "feed."
        )
        st.markdown(
            "**Snow-clearing priorities:** source links recorded in the local street "
            "dataset appear with selected streets. Verification dates are not recorded. "
            "Mixed priorities are listed by section; the map uses one mixed-priority "
            "colour for the whole street."
        )
        st.write(
            "Missing attributes are labelled unavailable. Approximate lengths describe "
            "the prepared pilot geometry and may not cover an entire street. "
            "The basemap is provided by OpenStreetMap contributors."
        )
