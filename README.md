<div align="center">

# CanAI 2026 Fall Hackathon

### Team G

**Adam** &nbsp; &middot; &nbsp; **Amanda** &nbsp; &middot; &nbsp; **Farhan** &nbsp; &middot; &nbsp; **Victoria** &nbsp; &middot; &nbsp; **Wilson**

</div>

## SnowStorm AI — Map MVP

Explore eight pilot streets in St. John's, select multiple streets, and review recorded municipal snow-clearing priorities and their sources. Unknown priorities are labelled unavailable. See [project context](./documents/PROJECT_CONTEXT.md) for the current map-only scope.

The **Map** tab contains Map Explorer. The **Simulation** tab is a placeholder;
no snow-depth simulation or clearing-time prediction is currently implemented.
The **Dev note** tab briefly summarizes map progress and explains the eight-street pilot scope.

### Quickstart

Run these commands from the repository root with Python and internet access for
dependency installation. Basemap tiles also require internet access.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS / Linux:

```bash
python3 -m venv .venv                      # once
.venv/bin/pip install -r requirements.txt  # once
.venv/bin/streamlit run app.py             # open http://localhost:8501
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.
Search for streets in the left sidebar, select several, and review their
highlighted geometries and details in the Map tab.

### Project layout

- `app.py` — single-page Streamlit entry point with Map, Simulation, and Dev note tabs
- `components/map_tab.py` — map rendering, session data refresh, street search/selection, priority legend, source links, and details
- `components/simulation_tab.py` — future simulation tab; currently an unavailable-data placeholder
- `components/dev_note_tab.py` — brief map progress, pilot scope rationale, and limitations
- `services/street_data.py` — cached local data loading and validation, shared independently of the tabs
- `scripts/fetch_pilot_streets.py` — shared City-source fetching logic and command-line preparation of saved data files
- `data/pilot_streets.geojson` — prepared road segments (WGS84)
- `data/street_priorities.json` — verified priorities per pilot street, incl. section-level detail
- `.streamlit/config.toml` — application colours, typography, and sidebar theme
- `tests/test_app.py` — tab layout, street selection, map highlighting, and data-validation regression checks
- `documents/` — project context, design guidance, and implementation plan

Keep feature-specific UI in `components/` and shared data logic in `services/` rather than adding them to `app.py`.
Map data failures are shown within the Map tab without preventing other tabs from rendering.

### Fetch or refresh street data

The app starts from local `data/` files. Use **Fetch / refresh data** in the sidebar
to retrieve the eight pilot streets from the City's public geometry and priority
sources for the current session. Requests may take several minutes. Successful
responses are validated before replacing the session dataset; failures keep the
current dataset. Missing priorities remain explicitly unavailable. Saved files are
unchanged, and valid street selections are preserved.

The button shows a spinner while requests run and a success message when the
session dataset is updated. A new session starts from the saved files again.

If refresh fails, a sidebar error identifies a timeout, connection failure,
HTTP status when available, or incomplete/invalid data. The last available
dataset remains in use. Check your connection and retry later. If a saved file
is missing or invalid, the Map tab displays a loading error; the refresh button
remains available to try fetching a session dataset.

Rerun the fetch script separately to update the saved startup dataset. Refreshing
does not add streets outside the configured pilot set or provide live road conditions.

### Map Explorer presentation

The theme in `.streamlit/config.toml` follows the colours and typography in
`documents/DESIGN.md`. Noto Sans is used when installed, with Arial and sans-serif fallbacks;
no external font download is configured. Map and street details appear side by
side on wider screens and stack on narrow screens using Streamlit's native layout.

Selected streets show recorded priority-source links and explicit unavailable
labels for missing attributes. Verification dates are not recorded in the current
dataset. The source and limitations panel explains pilot coverage, mixed priorities,
and the distinction between clearing priorities and current road conditions.

### Validation

Run the tab and map regression checks from the repository root.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The checked-in tests cover both tabs, source links, multi-street selection,
highlighting all selected road segments, invalid geometry, and map-load failures.
Live City requests, refresh error paths, and browser accessibility are not covered
by this suite. After UI changes, manually check narrow-screen stacking, keyboard
navigation, and the refresh success/error messages.

### Data sources and network access

Both the sidebar refresh and [command-line fetch script](./scripts/fetch_pilot_streets.py) use these sources:

| Data | Source | Retrieval method |
|---|---|---|
| Street geometry, names, and segment attributes | [City of St. John's ArcGIS Roads layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Queries the public REST `/query` endpoint by street name and requests WGS84 GeoJSON (`outSR=4326`). |
| Snow-clearing priorities and section descriptions | [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Loads the lookup page, submits its ASP.NET form for each pilot street, and parses the returned HTML table. This is website form automation, not a documented priority API. |

The app starts from [saved road geometry](./data/pilot_streets.geojson) and [saved priorities](./data/street_priorities.json). Clicking the sidebar refresh button queries the City services and updates only the current session. Selecting streets does not query those services. Neither dataset is a live road-condition or clearing-progress feed. The priority parser depends on the City's page markup and may need updating if that page changes.

To update the saved startup files, or after editing `PILOT_STREETS` in the fetch
script, run one of these commands from the repository root.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts/fetch_pilot_streets.py
```

macOS / Linux:

```bash
.venv/bin/python scripts/fetch_pilot_streets.py
```

The command-line script requires internet access and overwrites both saved data
files after fetching the pilot set. Review its output and saved records before
using them. Unlike the command-line script, the sidebar button validates the
returned geometry and priority data before updating the session. Restart the app
after updating saved files to clear its cached local dataset.

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
