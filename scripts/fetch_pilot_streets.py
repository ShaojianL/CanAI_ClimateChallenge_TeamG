"""Fetch pilot street geometries and verified snow-clearing priorities.

Phase A data preparation for the SnowStorm AI map MVP:

1. Queries the City of St. John's public ArcGIS road layer for the geometry
   of a small set of pilot streets (reprojected to WGS84 GeoJSON).
2. Looks up each street's official snow-clearing priority via the City's
   public StreetPriority.aspx lookup (the authoritative source).
3. Saves the combined, reviewed result to data/pilot_streets.geojson and
   data/street_priorities.json so the app never depends on live requests.

Run from the repo root:  .venv/bin/python scripts/fetch_pilot_streets.py
"""

import html
import json
import re
import time
from pathlib import Path

import requests

ARCGIS_QUERY_URL = (
    "https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0/query"
)
PRIORITY_LOOKUP_URL = "https://apps.stjohns.ca/snowclearing/StreetPriority.aspx"

# Small, manually reviewed pilot set (names as they appear in City data).
PILOT_STREETS = [
    "WATER ST",
    "DUCKWORTH ST",
    "GOWER ST",
    "MILITARY RD",
    "KENMOUNT RD",
    "PRINCE PHILIP DR",
    "SIGNAL HILL RD",
    "FRESHWATER RD",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HEADERS = {"User-Agent": "Mozilla/5.0 (SnowStormAI hackathon pilot; one-time fetch)"}


def fetch_street_segments(street_name: str) -> list[dict]:
    """Return GeoJSON features for every road segment of a street."""
    params = {
        "where": f"STREETNAME='{street_name}'",
        "outFields": "OBJECTID,STREETNAME,STREET_ID,STREETCLS,LENGTH",
        "outSR": "4326",
        "f": "geojson",
    }
    resp = requests.get(ARCGIS_QUERY_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("features"), list):
        raise ValueError("The road service returned an invalid feature collection.")
    features = payload["features"]
    if any(
        not isinstance(feature, dict)
        or not isinstance(feature.get("properties"), dict)
        for feature in features
    ):
        raise ValueError("The road service returned invalid street attributes.")
    return features


def _hidden_field(page: str, name: str) -> str:
    m = re.search(rf'name="{re.escape(name)}"[^>]*value="([^"]*)"', page)
    return m.group(1) if m else ""


def fetch_priority_page() -> tuple[str, dict[str, str]]:
    """Fetch the lookup page; return (page_html, street name -> dropdown value)."""
    resp = requests.get(PRIORITY_LOOKUP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    page = resp.text
    options = dict(re.findall(r'<option value="(\d+)">([^<]+)</option>', page))
    # invert: name -> value
    return page, {html.unescape(name).strip(): value for value, name in options.items()}


def lookup_priority(page: str, street_value: str) -> list[dict]:
    """Post the lookup form for one street; return official priority sections."""
    data = {
        "__EVENTTARGET": "ctl00$Content$ASPxPanel1$ddlStreets",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": _hidden_field(page, "__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": _hidden_field(page, "__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": _hidden_field(page, "__EVENTVALIDATION"),
        "ctl00$Content$ASPxPanel1$ddlStreets": street_value,
    }
    resp = requests.post(PRIORITY_LOOKUP_URL, data=data, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    cells = [
        re.sub(r"<[^>]+>", "", c).strip()
        for c in re.findall(r'<td class="dxgv[^"]*"[^>]*>(.*?)</td>', resp.text, re.S)
    ]
    cells = [html.unescape(c) for c in cells if c]
    sections = []
    # Cells alternate: section description, "Priority N"
    for name_cell, prio_cell in zip(cells[::2], cells[1::2]):
        m = re.search(r"Priority\s+(\d+)", prio_cell)
        if m:
            sections.append({"section": name_cell, "priority": int(m.group(1))})
    return sections


def fetch_pilot_data() -> tuple[dict, dict]:
    """Fetch the complete pilot dataset without changing saved files.

    Returns:
        Road GeoJSON and street priorities; absent priorities remain unknown.
    Raises:
        ValueError: A pilot street has no returned geometry.
        requests.RequestException: A City source cannot be reached.
    """
    print("Fetching City priority lookup page...")
    lookup_page, street_values = fetch_priority_page()

    all_features = []
    priorities = {}

    for street in PILOT_STREETS:
        print(f"\n== {street} ==")

        features = fetch_street_segments(street)
        if not features:
            raise ValueError(f"No road geometry returned for {street}.")
        total_len_m = sum(f["properties"].get("LENGTH") or 0 for f in features)
        print(f"  {len(features)} segments, approx {total_len_m:.0f} m total")
        all_features.extend(features)

        entry = {
            "segments": len(features),
            "approx_length_m": round(total_len_m),
            "sections": [],
            "priority_source": None,
        }
        value = street_values.get(street)
        if value is None:
            print("  WARNING: street not found in City priority lookup dropdown")
        else:
            sections = lookup_priority(lookup_page, value)
            if sections:
                entry["sections"] = sections
                entry["priority_source"] = PRIORITY_LOOKUP_URL
                for s in sections:
                    print(f"  Priority {s['priority']}: {s['section']}")
            else:
                print("  WARNING: lookup returned no priority rows")
            time.sleep(1)  # be polite to the City server

        levels = sorted({s["priority"] for s in entry["sections"]})
        if not levels:
            entry["priority"] = None  # explicitly unknown — never guess
        elif len(levels) == 1:
            entry["priority"] = levels[0]
        else:
            entry["priority"] = "mixed"
        entry["priority_levels"] = levels
        priorities[street] = entry

    return {"type": "FeatureCollection", "features": all_features}, priorities


def main() -> None:
    """Fetch the pilot streets and save them for local application startup."""
    geojson, priorities = fetch_pilot_data()
    DATA_DIR.mkdir(exist_ok=True)
    geojson_path = DATA_DIR / "pilot_streets.geojson"
    geojson_path.write_text(
        json.dumps(geojson, indent=1), encoding="utf-8"
    )
    priorities_path = DATA_DIR / "street_priorities.json"
    priorities_path.write_text(json.dumps(priorities, indent=2), encoding="utf-8")

    print(f"\nSaved {len(geojson['features'])} segments -> {geojson_path}")
    print(f"Saved priorities for {len(priorities)} streets -> {priorities_path}")


if __name__ == "__main__":
    main()
