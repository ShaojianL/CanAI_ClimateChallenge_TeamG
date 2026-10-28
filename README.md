<div align="center">

# CanAI 2026 Fall Hackathon

### Team G

**Adam** &nbsp; &middot; &nbsp; **Amanda** &nbsp; &middot; &nbsp; **Farhan** &nbsp; &middot; &nbsp; **Victoria** &nbsp; &middot; &nbsp; **Wilson**

</div>

## SnowStorm AI — Map MVP

Interactive map of pilot St. John's streets with officially verified snow-clearing priorities. See [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) for scope.

### Quickstart

```bash
python3 -m venv .venv                      # once
.venv/bin/pip install -r requirements.txt  # once
.venv/bin/streamlit run app.py             # open http://localhost:8501
```

### Project layout

- `app.py` — single-page Streamlit app (map, street search/selection, legend, details)
- `scripts/fetch_pilot_streets.py` — one-time data prep: road geometry from the City's public ArcGIS layer + priorities verified via the City's [street priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx)
- `data/pilot_streets.geojson` — prepared road segments (WGS84)
- `data/street_priorities.json` — verified priorities per pilot street, incl. section-level detail

### Data sources and network access

The pilot road geometry and priority records are prepared once by [scripts/fetch_pilot_streets.py](./scripts/fetch_pilot_streets.py):

| Data | Source | Retrieval method |
|---|---|---|
| Street geometry, names, and segment attributes | [City of St. John's ArcGIS Roads layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Queries the public REST `/query` endpoint by street name and requests WGS84 GeoJSON (`outSR=4326`). |
| Snow-clearing priorities and section descriptions | [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Loads the lookup page, submits its ASP.NET form for each pilot street, and parses the returned HTML table. This is website form automation, not a documented priority API. |

Results are saved in [data/pilot_streets.geojson](./data/pilot_streets.geojson) and [data/street_priorities.json](./data/street_priorities.json). The app reads these local snapshots; selecting streets does not query the City services. They are not live road-condition or clearing-progress feeds. The priority parser depends on the City's page markup and may need updating if that page changes.

To refresh the snapshots, or after editing `PILOT_STREETS` in the fetch script, run:

```bash
.venv/bin/python scripts/fetch_pilot_streets.py
```

Refreshing requires internet access and overwrites both data files. Review the output and saved records before using them.

**The app is not fully offline:** the browser loads OpenStreetMap basemap tiles and mapping assets online. No Google Maps service, paid mapping API, or API key is configured. Keep the map attribution visible and follow the [OpenStreetMap tile usage policy](https://operations.osmfoundation.org/policies/tiles/); public tile access is not an unlimited hosting service.

### What the street colors mean

Colors represent municipal **snow-clearing priority**, not snow depth, weather, hazard severity, or live road conditions. The palette is chosen by this app, not an official City color scheme.

| Color | Meaning |
|---|---|
| Red | Priority 1: major and minor arterials |
| Orange | Priority 2: collector streets |
| Blue | Priority 3: minor streets and cul-de-sacs |
| Purple | Priority 4: private lanes maintained by the City |
| Olive/brown | Mixed priorities across published street sections |
| Gray | Priority unavailable |

Road features are matched to priority records by street name. Coloring currently applies to the **whole street**, not individual priority sections: Water Street has published Priority 1 and Priority 2 sections, so all its segments use the mixed color. Published section boundaries have not been matched to individual geometries. Even a single published priority may describe only part of a street; the whole-street color does not independently verify coverage of every segment. GIS road classification (`STREETCLS`) is not used to infer snow-clearing priority.

Selecting a street makes all its mapped segments thicker and more opaque without changing their priority color.
