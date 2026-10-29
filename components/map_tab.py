"""Map tab: mock report counts, street controls, map, and source details."""

from collections import Counter

import folium
import streamlit as st
from streamlit_folium import st_folium

from components import data_refresh, theme
from services.mock_reports import generate_mock_reports
from services.street_data import DataLoadError, load_data

REPORT_COLORS = ("#fcae91", "#ef3b2c", "#99000d")
NO_REPORTS_COLOR = "#7f7f7f"

PRIORITY_LABELS = {
    1: "Priority 1 — major and minor arterials",
    2: "Priority 2 — collector streets",
    3: "Priority 3 — minor streets and cul-de-sacs",
    4: "Priority 4 — private lanes maintained by the city",
}


def street_color(report_count: int) -> str:
    """Choose one of three red shades by report count; zero is gray."""
    if report_count == 0:
        return NO_REPORTS_COLOR
    if report_count < 10:
        return REPORT_COLORS[0]
    if report_count < 30:
        return REPORT_COLORS[1]
    return REPORT_COLORS[2]


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


def build_map(
    geojson: dict, report_counts: dict[str, int], selected: list[str]
) -> folium.Map:
    """
    This program draws all road parts and highlights the selected streets.

    Parameters:
        geojson: Validated road FeatureCollection.
        report_counts: Number of mock reports by street name.
        selected: Names of streets to highlight and include in map bounds.
    Returns:
        A Folium map containing the pilot roads.
    """
    m = folium.Map(location=[47.566, -52.72], zoom_start=13, tiles="OpenStreetMap")

    bounds = []
    for feature in geojson["features"]:
        name = feature["properties"].get("STREETNAME", "")
        count = report_counts.get(name, 0)
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
                color=street_color(count),
                weight=8 if is_selected else 3,
                opacity=1.0,
                tooltip=f"{name} — {count} mock reports",
            ).add_to(m)

    if selected and bounds:
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

    reports = [
        report for report in generate_mock_reports()
        if report["street_name"] in priorities
    ]
    report_counts = Counter(report["street_name"] for report in reports)
    most_reported = max(street_names, key=lambda name: report_counts[name])
    st.info("Mock data preview: fictional people and reports, not live submissions.")
    theme.render_kpi_row([
        (str(len(reports)), "Total reports", theme.GC_ACCENT),
        (str(len({r["reporter_id"] for r in reports})), "Distinct reporters", theme.GC_ACCENT),
        (f"{len(report_counts)} / {len(street_names)}", "Pilot roads with reports", theme.GC_ACCENT),
        (str(report_counts[most_reported]), f"Most reported road: {most_reported}", REPORT_COLORS[2]),
    ])
    st.caption(
        "Counts cover the entire mock dataset, not just selected streets. "
        "Darker red means more reports, not worse snow or greater danger. "
        "Gray means no reports, not a clear road."
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
            legend_rows = [
                (REPORT_COLORS[0], "1–9 reports"),
                (REPORT_COLORS[1], "10–29 reports"),
                (REPORT_COLORS[2], "30+ reports"),
                (NO_REPORTS_COLOR, "0 reports — no information"),
            ]
            for color, label in legend_rows:
                st.markdown(
                    f"<span style='color:{color}'>▬▬</span> {label}",
                    unsafe_allow_html=True,
                )
            st.caption("Mock report counts per whole street, not snow severity.")

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
                "thicker lines. Hover for mock report counts; select streets for "
                "counts and recorded priority details as text."
            )
            st_folium(
                build_map(geojson, report_counts, selected),
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
                st.markdown(f"**Mock reports: {report_counts[name]}**")
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
            "Mixed priorities are listed by section; they do not determine map colours."
        )
        st.markdown(
            "**Mock reports:** 200 fictional people submit one report each across "
            "the configured pilot streets. Counts are deterministic UI fixtures, "
            "not measured impact, verified conditions, or a live reporting feed. "
            "A whole-street count is repeated on its geometry parts; it does not "
            "locate an incident on an individual segment."
        )
        st.write(
            "Missing attributes are labelled unavailable. Approximate lengths describe "
            "the prepared pilot geometry and may not cover an entire street. "
            "The basemap is provided by OpenStreetMap contributors."
        )
