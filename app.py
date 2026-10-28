"""SnowStorm AI — Map MVP (single-page Streamlit app).

Interactive map of a small pilot set of real St. John's streets with
verified municipal snow-clearing priorities, searchable multi-street
selection, and a reserved area for future simulation output.

Run:  .venv/bin/streamlit run app.py
"""

import json
import math
from pathlib import Path

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

from scripts.fetch_pilot_streets import fetch_pilot_data

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


class DataLoadError(ValueError):
    """
    This program identifies data failures that can be explained to the user.

    Parameters:
        message: A description of the data problem and how to resolve it.
    Returns:
        A DataLoadError exception instance.
    """


def read_json(filename):
    """
    This program reads a required local JSON file with friendly error messages.

    Parameters:
        filename: The name of a file inside the data directory.
    Returns:
        The parsed JSON content.
    """
    path = DATA_DIR / filename
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DataLoadError(
            f"Required file '{filename}' is missing. Restore it in the data folder."
        ) from exc
    except UnicodeError as exc:
        raise DataLoadError(f"'{filename}' must be a UTF-8 text file.") from exc
    except OSError as exc:
        raise DataLoadError(
            f"Cannot read '{filename}'. Check that it is accessible and readable."
        ) from exc

    if not text.strip():
        raise DataLoadError(f"'{filename}' is empty. Restore a valid copy.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            f"'{filename}' contains invalid JSON near line {exc.lineno}. "
            "Correct it or restore a valid copy."
        ) from exc


def validate_data(geojson, priorities):
    """
    This program checks the road geometry and fields used by the interface.

    Parameters:
        geojson: Parsed road FeatureCollection.
        priorities: Parsed street priority dictionary.
    Returns:
        None. Raises DataLoadError when required data is unusable.
    """
    if (
        not isinstance(geojson, dict)
        or geojson.get("type") != "FeatureCollection"
        or not isinstance(geojson.get("features"), list)
        or not geojson["features"]
    ):
        raise DataLoadError(
            "'pilot_streets.geojson' must contain a nonempty FeatureCollection."
        )

    for index, feature in enumerate(geojson["features"], start=1):
        problem = f"'pilot_streets.geojson' feature {index}"
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise DataLoadError(f"{problem} must be a GeoJSON Feature.")
        properties = feature.get("properties")
        if (
            not isinstance(properties, dict)
            or not isinstance(properties.get("STREETNAME"), str)
            or not properties["STREETNAME"].strip()
        ):
            raise DataLoadError(f"{problem} needs a nonempty STREETNAME.")
        geometry = feature.get("geometry")
        if not isinstance(geometry, dict) or geometry.get("type") not in (
            "LineString", "MultiLineString"
        ):
            raise DataLoadError(f"{problem} must use LineString or MultiLineString.")

        # Normalize the nesting without joining separate road sections
        coordinates = geometry.get("coordinates")
        parts = [coordinates] if geometry["type"] == "LineString" else coordinates
        if not isinstance(parts, list) or not parts:
            raise DataLoadError(f"{problem} has no usable road parts.")
        for part in parts:
            if not isinstance(part, list) or len(part) < 2:
                raise DataLoadError(f"{problem} needs at least two points per part.")
            for point in part:
                if (
                    not isinstance(point, list)
                    or len(point) < 2
                    or any(
                        type(value) not in (int, float) or not math.isfinite(value)
                        for value in point
                    )
                    or not -180 <= point[0] <= 180
                    or not -90 <= point[1] <= 90
                ):
                    raise DataLoadError(f"{problem} contains invalid coordinates.")

    if not isinstance(priorities, dict) or not priorities:
        raise DataLoadError(
            "'street_priorities.json' must contain a nonempty street dictionary."
        )
    for name, info in priorities.items():
        problem = f"'street_priorities.json' entry '{name}'"
        if not name.strip() or not isinstance(info, dict):
            raise DataLoadError(f"{problem} needs a street name and detail object.")

        # Missing priority values remain valid and use the existing unknown label
        priority = info.get("priority")
        if priority is not None and priority != "mixed" and (
            type(priority) is not int or priority not in PRIORITY_COLORS
        ):
            raise DataLoadError(f"{problem} has an invalid priority.")
        levels = info.get("priority_levels", [])
        if not isinstance(levels, list) or any(
            type(level) is not int or level not in PRIORITY_COLORS for level in levels
        ):
            raise DataLoadError(f"{problem} has invalid priority_levels.")
        for field in ("approx_length_m", "segments"):
            value = info.get(field)
            if value is not None and (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or value < 0
            ):
                raise DataLoadError(f"{problem} needs a nonnegative numeric {field}.")
        sections = info.get("sections", [])
        if not isinstance(sections, list) or any(
            not isinstance(section, dict)
            or not isinstance(section.get("section"), str)
            or type(section.get("priority")) is not int
            or section["priority"] not in PRIORITY_COLORS
            for section in sections
        ):
            raise DataLoadError(f"{problem} has invalid section details.")


@st.cache_data
def load_data():
    """
    This program loads and validates the local street datasets before caching.

    Parameters:
        None.
    Returns:
        A tuple containing the road GeoJSON and street priority dictionary.
    """
    geojson = read_json("pilot_streets.geojson")
    priorities = read_json("street_priorities.json")
    validate_data(geojson, priorities)
    return geojson, priorities


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


def main():
    """
    This program displays the street map, selection controls, and street details.

    Parameters:
        None.
    Returns:
        None. Renders the Streamlit interface.
    """
    st.set_page_config(page_title="Map Explorer | SnowStorm AI", layout="wide")

    st.title("Map Explorer")
    st.write(
        "Explore pilot streets in St. John's, review snow-clearing priorities, "
        "and inspect available source information."
    )
    st.caption(
        "Planning context only. Priority colours do not represent current road "
        "conditions, travel safety, or simulated snow depth."
    )

    with st.sidebar:
        st.header("SnowStorm AI")
        st.caption("St. John's pilot streets")
        st.subheader("Street data")
        st.caption(
            "Fetch the eight pilot streets from the City's public sources. "
            "Refresh applies to this session; saved files remain unchanged. "
            "Requests may take several minutes."
        )
        if st.button("Fetch / refresh data", width="stretch"):
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

    # Stop before drawing a partial or misleading map when required data fails
    try:
        if "refreshed_data" in st.session_state:
            geojson, priorities = st.session_state["refreshed_data"]
        else:
            geojson, priorities = load_data()
    except DataLoadError as exc:
        st.error(f"Street data could not be loaded. {exc}")
        st.stop()
    street_names = sorted(priorities.keys())

    # ---- Sidebar: search/selection, details, legend ----
    with st.sidebar:
        # Keep valid selections when the refreshed source changes its street list.
        if "selected_streets" in st.session_state:
            st.session_state["selected_streets"] = [
                name for name in st.session_state["selected_streets"]
                if name in street_names
            ]
        selected = st.multiselect(
            "Search and select streets",
            options=street_names,
            placeholder="Type a street name…",
            key="selected_streets",
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
        st.caption("Mixed priorities vary by section. Grey means priority unavailable.")

    # ---- Main area: map + details ----
    col_map, col_details = st.columns([2, 1], gap="large")

    with col_map:
        st.header("Pilot street map")
        st.caption(
            "Search and select streets in the sidebar. Selected streets use thicker "
            "lines; their priority and section details are also available as text."
        )
        st_folium(
            build_map(geojson, priorities, selected),
            use_container_width=True,
            height=600,
            returned_objects=[],  # display-only: avoids reruns on map interaction
        )

    with col_details:
        st.header("Selected streets")
        st.caption(f"{len(selected)} of {len(street_names)} pilot streets selected")
        if not selected:
            st.info("Use the sidebar to search and select streets.")
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

    with st.expander("Data sources and limitations", expanded=True):
        st.markdown(
            "**Road geometry:** [City of St. John's public ArcGIS road layer]"
            "(https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0). "
            "The map displays a pilot snapshot loaded from saved files or fetched "
            "using the sidebar refresh button, not a live road-conditions feed."
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

    # ---- Reserved area for future simulation output ----
    st.divider()
    st.header("Snow-depth simulation")
    st.info(
        "Simulated snow-depth graphs and a storm time selector will appear "
        "here in a later phase. No simulation data exists yet."
    )


if __name__ == "__main__":
    main()
