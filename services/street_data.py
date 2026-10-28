"""Load and validate the local pilot street datasets."""

import json
import math
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PRIORITY_LEVELS = (1, 2, 3, 4)


class DataLoadError(ValueError):
    """A data failure that can be explained to the user."""


def read_json(filename):
    """Read a required local JSON file with friendly error messages."""
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
    """Check the road geometry and fields used by the interface."""
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
            type(priority) is not int or priority not in PRIORITY_LEVELS
        ):
            raise DataLoadError(f"{problem} has an invalid priority.")
        levels = info.get("priority_levels", [])
        if not isinstance(levels, list) or any(
            type(level) is not int or level not in PRIORITY_LEVELS for level in levels
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
            or section["priority"] not in PRIORITY_LEVELS
            for section in sections
        ):
            raise DataLoadError(f"{problem} has invalid section details.")


@st.cache_data
def load_data():
    """Load and validate the local street datasets before caching."""
    geojson = read_json("pilot_streets.geojson")
    priorities = read_json("street_priorities.json")
    validate_data(geojson, priorities)
    return geojson, priorities
