# SnowStorm AI — Map MVP Context for GitHub Copilot

> **Purpose:** Project context for implementing the interactive map portion of SnowStorm AI. Use this as a guide to design and implement the feature incrementally. It describes user needs and intended behavior, **not** a rigid technical specification.

## Project overview

SnowStorm AI is a proposed decision-support tool for exploring how severe winter weather could affect snow-clearing operations in St. John's, Newfoundland and Labrador. The broader product may eventually simulate hourly snowfall, road-clearing progress, and preparedness options.

**Current focus: the map only.** Build a usable interactive view of a small, real St. John's road network. Users should be able to explore streets, understand their published snow-clearing priorities where verified, and select multiple streets for later snow-depth comparisons.

No snowstorm simulation, forecast model, or AI recommendation engine is being implemented in this phase.

## Desired user experience

Picture a single-page application with:

- A **large, interactive map** of St. John's displaying road geometries from a public data source.
- A **street search and multi-selection control** near the map (for example, in a sidebar).
- **Visual highlighting** of selected streets; selecting a street should highlight its relevant segments rather than just one piece of geometry.
- A **street information area** showing available attributes such as name, verified snow-clearing priority, and approximate length.
- A simple **road-priority legend** and an obvious indication when priority data is unknown.
- A reserved area for **future simulated snow-depth graphs and a time selector**. Until a simulation is connected, show a clear unavailable/coming-later state; do not invent values.

Map-based street selection is desirable, but a reliable searchable selector is the first priority. Add click-to-select only if it works consistently with the chosen mapping library.

## Scope and boundaries

### In scope now

- Retrieve or load actual public road geometries for a manageable subset of St. John's streets.
- Render those streets on an interactive map with zoom and pan.
- Display street names and any verified road-clearing priorities.
- Support selecting and deselecting multiple streets.
- Highlight selected streets and show their details.
- Keep map data and selected-street state organized for future simulation integration.
- Handle missing or ambiguous source data clearly.

### Out of scope now

- Predicting snowfall, actual road safety, or real-world clearing completion times.
- Snow accumulation or snowplow activity simulation.
- Snowplow routing, crew/resource optimization, or live dispatch.
- AI-generated preparedness recommendations.
- Real-time road-condition integrations, historical GPS reconstruction, or a production-grade government deployment.
- Building snow-depth charts before simulation output exists.

## Public data sources to investigate

| Source | Why it is useful | Data-access caution |
|---|---|---|
| [City of St. John's ArcGIS road layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Street geometries, names, and possible street/segment identifiers for the map | Confirm the endpoint and relevant fields with a small live query before relying on them. A street may span many segments; check for incomplete or duplicated geometry. |
| [City of St. John's snow-clearing service levels](https://www.stjohns.ca/resident-services/snow-clearing/service-levels-priority/) | Public explanation of how municipal roads are prioritized for snow clearing | This is the policy context, not necessarily a downloadable street-by-street dataset. |
| [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Verify the actual priority of streets selected for the pilot | A public lookup is not proof of a bulk API. Manual verification for a small subset is acceptable. |
| [OpenStreetMap](https://www.openstreetmap.org/) | Potential backup for road geometry/basemap data | Source and attribution differ from the City's GIS; do not silently mix identifiers or treat OSM road classes as City snow-clearing priorities. |

**Important distinction:** A GIS field describing road *class* does not automatically establish the City's official *snow-clearing priority*. Only label priorities as official if they have been verified using an authoritative source. Otherwise, display “Priority unavailable.”

Public data might be available for viewing without providing an immediately usable bulk export. Test access before planning around automated extraction.

## Initial data concepts

Keep the internal representation simple and adaptable to the data actually retrieved.

- **Road segment:** A mapped piece of street geometry with a source identifier, street name, and optional attributes.
- **Street:** A logical grouping of one or more road segments that users can select together.
- **Priority:** An optional, verified municipal snow-clearing priority associated with a street or segment, with a note about its source.
- **Selection state:** The set of streets currently selected by the user.
- **Future snow state:** Optional simulation results tied to a road or segment and a time point; this does not exist yet.

Do not assume all features have names, that names uniquely identify streets, or that every segment has the same priority. Where grouping by street name is ambiguous, inspect identifiers and make a deliberate pilot-specific choice.

For the initial pilot, a small, manually reviewed collection of approximately **5–10 streets** is preferable to an unverified city-wide import.

## Suggested implementation approach

A lightweight Python application using **Streamlit** and a mapping library such as **Folium** is a reasonable starting point. GeoJSON works well for transferring geometries and keeping data separate from presentation. These are recommendations rather than hard requirements; use an alternative if it offers cleaner and more reliable map interaction.

### Phase A — Verify and prepare the streets

1. Inspect the public road GIS endpoint and retrieve a small sample of named streets.
2. Check geometry, street names, identifiers, and coordinate conventions.
3. Group related road segments into selectable streets; review ambiguous cases.
4. Look up the priority for each pilot street using the City source. Record unknown values explicitly.
5. Save a locally usable copy of the prepared pilot roads so the UI does not depend on a fresh GIS request for every interaction.

**Conceptual pseudocode:**

```text
find a small area or list of candidate streets
retrieve real road features from a public source
inspect names, IDs, and geometries
for each candidate street:
    group its relevant road segments
    look up its official clearing priority if possible
    otherwise mark priority as unavailable
save reviewed street and segment information locally
```

### Phase B — Draw the map

1. Display a basemap centered on the pilot area.
2. Draw the retrieved road geometries.
3. Use a simple, documented colour scheme to distinguish **verified** priority classes; use a neutral style for unknown priorities.
4. Add hover or click details where practical.
5. Provide a legend and make data provenance visible.

```text
load prepared road geometries
create the interactive map
for each segment:
    choose style from verified priority or unknown status
    draw geometry with street name and available metadata
show legend and map
```

These colours represent road priority only—not hazard severity or snow depth.

### Phase C — Street selection and details

1. Populate a searchable street list from the prepared road data.
2. Support selecting multiple streets and removing them individually.
3. Highlight **all relevant segments** belonging to each selected street.
4. Show available details for selected streets; avoid filling missing fields with guessed values.
5. If straightforward, make selecting a road on the map update the same selection state.

```text
when selection changes:
    update selected street IDs
    find all segments belonging to those streets
    highlight their geometries
    refresh the street details panel

when a road segment is clicked (optional):
    resolve it to its selectable street
    update the same selected-street collection
```

Prefer stable IDs over names where the source makes that practical. Keep the experience understandable if different streets share a similar name.

### Phase D — Prepare for later simulation integration

Keep the map component conceptually separate from the simulation engine:

```text
map view receives:
    prepared roads
    selected streets
    optional selected time
    optional simulated snow states

if simulated snow states exist:
    allow time-based colouring and comparison
else:
    show the priority map and a clear “simulation data unavailable” message
```

Future behaviour may include a time slider, snow-depth colours, and line charts for selected streets. Do not create or hard-code synthetic snow results to make the present interface appear functional.

If a street has multiple segments, the later snow-depth comparison will need a documented aggregation method; that is a future design decision, not a requirement for this map MVP.

## Suggested repository organization

Use whatever conventions fit the repository. A possible small-project layout is:

```text
snowstorm-ai/
├── app.py                    # UI assembly and application state
├── data/
│   ├── roads.geojson         # Reviewed pilot road geometries
│   └── road_priorities.csv   # Verified priorities where available
├── src/
│   ├── roads_source.py       # Retrieving public road data
│   ├── prepare_roads.py      # Normalization and street grouping
│   ├── map_view.py           # Map rendering and styling
│   └── street_selection.py   # Selection and detail helpers
└── README.md                 # Setup, provenance, limitations
```

This is an organizational suggestion, not a prescribed file list or naming convention. Split or consolidate modules as needed.

## What to verify while building

- The selected streets are genuinely present in the downloaded St. John's GIS data.
- Coordinates and geometries render in the correct locations.
- Multi-segment streets are selected and highlighted consistently.
- Priority labels match the City's lookup or remain explicitly unavailable.
- Multi-street selection persists across normal UI rerenders.
- A missing GIS response or empty dataset produces a clear message; a verified local copy may be used if available.
- Nothing on the map suggests that simulated snow depth, clearing completion, or travel safety has been calculated yet.
- If using OpenStreetMap as a basemap, preserve its attribution.

## Definition of done for the map-only MVP

A user can open the application, inspect a **real, small St. John's street network**, search for and select several streets, see them highlighted, and read accurate available street details and snow-clearing priority information. The interface makes unknown data explicit and has a clear integration boundary for future hourly simulation results.

## How Copilot should use this context

- Start by inspecting the existing project and reusing its patterns where possible.
- Prefer a small, working vertical slice over a broad or overly engineered build.
- Verify data availability instead of assuming undocumented endpoints, fields, or historical records exist.
- Use straightforward implementation choices and explain trade-offs when data or interactive map behavior is uncertain.
- Treat pseudocode and suggested structure as guidance, not mandatory source-code contracts.
- Keep the current feature focused on the map; do not implement the full SnowStorm AI simulator unless explicitly requested.
