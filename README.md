# CanAI 2026 Fall Hackathon: Team G

**Team:** Adam, Amanda, Farhan, Victoria, and Wilson

## Community Crisis Reporting Map

The project aims to help residents report local hazards and view timely, map-based
alerts in St. John's. Planned AI processing will check and consolidate reports,
assign an informational severity (Low, Medium, or High), and prepare relevant
subscriber updates without a staff approval stage.

**Current status:** The runnable app is **Flurry**, a legacy SnowStorm AI prototype
with an eight-street priority map and a hypothetical snow-depth simulation.
Reporting, AI processing, district subscriptions, and notifications are planned
capabilities, not implemented features.

The reporting pilot covers **St. John's Center, St. John's East, and St. John's
West**. The supplied district street-directory CSV must be validated against the
road geometries before defining the pilot street list. The existing eight map
streets are not that validated three-district list.

Alerts are intended for situational awareness. AI processing does not prove an
incident is true or guarantee municipal action or road safety. The product is not
an emergency-reporting service. See [project context](documents/PROJECT_CONTEXT.md)
for the governing scope and remaining decisions.

## Run locally

Prerequisites: Python with `venv` and `pip`, and internet access to install
dependencies and load basemap tiles. Run the commands from the repository root.
Virtual-environment activation is not required.

Windows PowerShell:

```powershell
.\setup.ps1
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The setup script creates `.venv` when needed and installs the existing
`requirements.txt`. It reuses an existing environment and stops if a command fails.
Use `.\setup.ps1 -WhatIf` to preview its actions without installing anything.
If PowerShell blocks scripts under your execution policy, use the manual commands:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.
Search for streets in the left sidebar, select several, and review their
highlighted geometries and details in the Map tab.

## Use the current prototype

The current app lets users explore eight configured pilot streets in St. John's, select multiple streets, and review recorded municipal snow-clearing priorities and their sources. Unknown priorities are labelled unavailable. These streets are not the three-district crisis-reporting pilot list.

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

### Street colours

Colours represent municipal **snow-clearing priority**, not snow depth, weather, hazard severity, or live road conditions. The palette is chosen by this app, not an official City colour scheme.

| Colour      | Meaning                                           |
| ----------- | ------------------------------------------------- |
| Red         | Priority 1: major and minor arterials             |
| Orange      | Priority 2: collector streets                     |
| Blue        | Priority 3: minor streets and cul-de-sacs         |
| Purple      | Priority 4: private lanes maintained by the City  |
| Olive/brown | Mixed priorities across published street sections |
| Grey        | Priority unavailable                              |

Road features are matched to priority records by street name. Colouring currently applies to the **whole street**, not individual priority sections: Water Street has published Priority 1 and Priority 2 sections, so all its segments use the mixed colour. Published section boundaries have not been matched to individual geometries. Even a single published priority may describe only part of a street; the whole-street colour does not independently verify coverage of every segment. GIS road classification (`STREETCLS`) is not used to infer snow-clearing priority.

Selecting a street makes all its mapped segments thicker and more opaque without changing their priority colour.

### Map display and depot assumption

The theme in `.streamlit/config.toml` follows the colours and typography in
`documents/DESIGN.md`. Noto Sans is used when installed, with Arial and sans-serif fallbacks;
no external font download is configured. Map and street details appear side by
side on wider screens and stack on narrow screens using Streamlit's native layout.

Selected streets show recorded priority-source links and explicit unavailable
labels for missing attributes. Verification dates are not recorded in the current
dataset. The source and limitations panel explains pilot coverage, mixed priorities,
and the distinction between clearing priorities and current road conditions.

A large dark dot marks the assumed starting depot at 25 Blackler Avenue
(47.546909, -52.741242). The address is listed in the
[City contact directory](https://www.stjohns.ca/contacts-directory/); coordinates
come from an ArcGIS PointAddress match checked on 2026-10-29, not a verified
vehicle entrance. All simulated plows are assumed to start here; actual dispatch
locations remain unverified. The marker is planning context only: the current
simulation does not use it or calculate routes.

## Refresh street data

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

### Data sources and saved files

Both the sidebar refresh and [command-line fetch script](./scripts/fetch_pilot_streets.py) use these sources:

| Data                                              | Source                                                                                                             | Retrieval method                                                                                                                                                           |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Street geometry, names, and segment attributes    | [City of St. John's ArcGIS Roads layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Queries the public REST `/query` endpoint by street name and requests WGS84 GeoJSON (`outSR=4326`).                                                                        |
| Snow-clearing priorities and section descriptions | [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx)                            | Loads the lookup page, submits its ASP.NET form for each pilot street, and parses the returned HTML table. This is website form automation, not a documented priority API. |

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

## Project layout

- `app.py`: single-page Streamlit entry point with Map, Simulation, and Dev note tabs
- `components/map_tab.py`: map rendering, session data refresh, street search/selection, priority legend, source links, and details
- `components/simulation_tab.py`: legacy hypothetical snow-depth simulation UI
- `services/simulation.py`: one-street snow-depth simulation engine
- `components/dev_note_tab.py`: brief map progress, pilot scope rationale, and limitations
- `services/street_data.py`: cached local data loading and validation, shared independently of the tabs
- `scripts/fetch_pilot_streets.py`: shared City-source fetching logic and command-line preparation of saved data files
- `data/pilot_streets.geojson`: prepared road segments (WGS84)
- `data/street_priorities.json`: recorded priorities per pilot street, including section-level detail
- `.streamlit/config.toml`: application colours, typography, and sidebar theme
- `tests/`: application, data-refresh, and simulation regression checks
- `documents/`: project context, design guidance, and implementation plan

Keep feature-specific UI in `components/` and shared data logic in `services/` rather than adding them to `app.py`.
Map data failures are shown within the Map tab without preventing other tabs from rendering.

## Validation

Run the regression checks from the repository root.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The checked-in tests cover tab rendering, simulation results and invalid inputs,
street selection and highlighting, source links, invalid geometry, map-load
failures, and mocked refresh success/failure behaviour. Live City requests and
browser accessibility still need manual checks. After UI changes, check
narrow-screen stacking, keyboard navigation, and refresh success/error messages.
