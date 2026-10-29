<div align="center">

# CanAI 2026 Fall Hackathon

### Team G

**Adam** &nbsp; &middot; &nbsp; **Amanda** &nbsp; &middot; &nbsp; **Farhan** &nbsp; &middot; &nbsp; **Victoria** &nbsp; &middot; &nbsp; **Wilson**

</div>

## Community Crisis Reporting Map

### Problem

Governments lack timely visibility into incidents happening around the city, and traditional reporting can be too slow when hazards need immediate attention. Residents also lack clear, up-to-date information about local conditions, causing last-minute confusion during natural disasters. During a snowstorm, for example, an uprooted tree blocking a road can leave commuters—especially essential workers—unaware until they reach the obstruction.

### Solution and pilot

The project is a crisis-reporting tool where residents can report hazards and view public, map-based alerts. AI is intended to validate and consolidate reports, assign an informational severity (Low, Medium, or High), and send relevant updates to subscribers. Residents will be able to subscribe to a street, a pilot district, or the whole pilot area, and filter alerts by severity. There is no staff review or approval layer. Alerts must communicate uncertainty; AI processing does not prove that an incident is true or guarantee municipal action.

The pilot is limited to streets in **St. John's Center, St. John's East, and St. John's West**, based on the district street-directory data. The supplied CSV must be validated against the existing road geometries before defining the in-scope street list. The product is for situational awareness, not an emergency-reporting service or a guarantee of road safety.

**Implementation status:** These reporting, AI, district-subscription, and notification capabilities are product direction, not features currently implemented in this repository. The current Streamlit app is a legacy SnowStorm AI prototype with a mock report-count map and a hypothetical snow-depth simulation. Report submission is not implemented. Use [project context](./documents/PROJECT_CONTEXT.md) as the source of truth for the current product scope.

## Existing application (legacy SnowStorm AI prototype)

The current app lets users explore eight configured pilot streets in St. John's, preview synthetic report counts, select multiple streets, and review recorded municipal snow-clearing priorities and their sources. Unknown priorities are labelled unavailable. These streets are not the three-district crisis-reporting pilot list.

The **Map** tab contains Map Explorer. The **Simulation** tab accepts hourly
snowfall (comma-separated centimetres), a manually entered street length, and
assumed clearing capacity (cm-km/hour). Select **Run simulation** to view a
remaining-snow graph and hourly results table. Map selections do not set simulation
inputs. Add zero-snowfall hours to model clearing after a storm.

**Current known assumptions:** The simulation starts with zero snow, assumes
uniform snow along the street and constant clearing capacity, adds snowfall
before clearing each hour, and does not carry unused capacity forward. It excludes
individual plows, routing, traffic, melting, drifting, compaction, and equipment
failures. Results are simulated estimates, not observed conditions or road-safety
assessments. The simulation ends after the last supplied hour.

The **Dev note** tab briefly summarizes legacy map progress and explains its eight-street scope.

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
Search for streets in the Map tab's **Street controls** card, select several, and
review their highlighted geometries and details.

### Project layout

- `app.py` — single-page Streamlit entry point with Map, Simulation, and Dev note tabs
- `components/map_tab.py` — mock report-count map and KPIs, session data refresh, street search/selection, source links, and details
- `services/mock_reports.py` — deterministic fixture of 200 reports from 200 fictional people
- `scripts/generate_mock_reports.py` — command-line JSON export of the same mock reports
- `components/simulation_tab.py` — legacy hypothetical snow-depth simulation UI
- `components/dev_note_tab.py` — brief map progress, pilot scope rationale, and limitations
- `services/street_data.py` — cached local data loading and validation, shared independently of the tabs
- `scripts/fetch_pilot_streets.py` — shared City-source fetching logic and command-line preparation of saved data files
- `data/pilot_streets.geojson` — prepared road segments (WGS84)
- `data/street_priorities.json` — verified priorities per pilot street, incl. section-level detail
- `components/theme.py` — shared navigation bar, card, and statistic styling for the `documents/ui_design/` mockup, using the [Canada.ca design-system colours and typography](https://design.canada.ca/styles/colours.html)
- `.streamlit/config.toml` — application colours and typography theme
- `tests/test_app.py` — tab layout, street selection, map highlighting, and data-validation regression checks
- `documents/` — project context, design guidance, and implementation plan

Keep feature-specific UI in `components/` and shared data logic in `services/` rather than adding them to `app.py`.
Map data failures are shown within the Map tab without preventing other tabs from rendering.

### Fetch or refresh street data

The app starts from local `data/` files. Use **Fetch / refresh data** in the Map
tab's Street controls card
to retrieve the eight pilot streets from the City's public geometry and priority
sources for the current session. Requests may take several minutes. Successful
responses are validated before replacing the session dataset; failures keep the
current dataset. Missing priorities remain explicitly unavailable. Saved files are
unchanged, and valid street selections are preserved.

The button shows a spinner while requests run and a success message when the
session dataset is updated. A new session starts from the saved files again.

If refresh fails, an error in the Street controls card identifies a timeout,
connection failure,
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

The map is explicitly labelled **Mock data preview**. Each of 200 fictional people
submits one report. The shared fixture is regenerated identically on every run:

| Pilot road | Mock reports |
|---|---:|
| WATER ST | 65 |
| DUCKWORTH ST | 50 |
| KENMOUNT RD | 35 |
| MILITARY RD | 25 |
| PRINCE PHILIP DR | 15 |
| FRESHWATER RD | 7 |
| GOWER ST | 3 |
| SIGNAL HILL RD | 0 |

Road colours use **light red for 1–9**, **medium red for 10–29**, and **dark red
for 30+ reports**. Gray means zero reports, not a clear road. Counts apply to whole
streets, not individual geometry segments. Selection changes line thickness, not
the colour scale. These are reporting-activity counts, not snow severity, measured
impact, live observations, or safety assessments.

The four KPI cards show total reports, distinct reporters, pilot roads with
reports, and the most-reported road with its count. They always summarize the
entire mock dataset, regardless of street selection. Refresh updates City geometry
and priority metadata, not report counts.

Print the synthetic records as JSON from the repository root (no new packages):

```bash
.venv/bin/python -m scripts.generate_mock_reports
```

The script prints JSON to standard output; the UI uses the same generator directly
and does not require saving or importing its output. Records have synthetic report
and reporter IDs and no real personal information or fabricated observation times.

Selected streets show mock counts, recorded priority-source links and explicit unavailable
labels for missing attributes. Verification dates are not recorded in the current
dataset. The source and limitations panel explains pilot coverage, mock data, and
mixed priorities. Clearing priorities remain available as metadata, not map colours.

The map does not show a starting depot. The current simulation does not assume a
dispatch location or calculate routes.

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

Both the in-app refresh button and [command-line fetch script](./scripts/fetch_pilot_streets.py) use these sources:

| Data | Source | Retrieval method |
|---|---|---|
| Street geometry, names, and segment attributes | [City of St. John's ArcGIS Roads layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Queries the public REST `/query` endpoint by street name and requests WGS84 GeoJSON (`outSR=4326`). |
| Snow-clearing priorities and section descriptions | [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Loads the lookup page, submits its ASP.NET form for each pilot street, and parses the returned HTML table. This is website form automation, not a documented priority API. |

The app starts from [saved road geometry](./data/pilot_streets.geojson) and [saved priorities](./data/street_priorities.json). Clicking the in-app refresh button queries the City services and updates only the current session. Selecting streets does not query those services. Neither dataset is a live road-condition or clearing-progress feed. The priority parser depends on the City's page markup and may need updating if that page changes.

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
using them. Unlike the command-line script, the in-app refresh button validates the
returned geometry and priority data before updating the session. Restart the app
after updating saved files to clear its cached local dataset.

**The app is not fully offline:** the browser loads OpenStreetMap basemap tiles and mapping assets online, and the Lato heading font from Google Fonts. No Google Maps service, paid mapping API, or API key is configured. Keep the map attribution visible and follow the [OpenStreetMap tile usage policy](https://operations.osmfoundation.org/policies/tiles/); public tile access is not an unlimited hosting service.

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
