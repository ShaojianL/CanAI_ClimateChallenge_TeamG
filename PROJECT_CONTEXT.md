# SnowStorm AI Project Context

Last updated: 2026-10-28

## Project status and authority

Amanda selected SnowStorm AI as the CanAI Hackathon project. This file consolidates the existing project context and `SnowStorm_AI_Map_Copilot_Context.md` into one maintained reference.

**Current implementation focus: the map-only MVP.** Build a small, real St. John's road map with searchable multi-street selection, verified priority information where available, and clear handling of unknown data. Simulation, forecasting, and AI preparedness recommendations belong to a later phase.

The original `SnowStorm_AI_8_Hour_MVP_Plan.docx` informed the broader simulator plan retained below. Its eight-hour schedule and simulator completion criteria apply to that future scope, not the current map phase. Where the two scopes differ, follow the map-only requirements for current work. Proposed technologies and file layouts remain guidance, not approved dependency or architecture changes.

Implementation, data extraction, source access, and validation remain unverified. Consolidating these documents does not mark any feature complete or independently verify their sources.

## Current phase: map-only MVP

### Project overview

SnowStorm AI is a proposed decision-support tool for exploring how severe winter weather could affect snow-clearing operations in St. John's, Newfoundland and Labrador. The broader product may eventually simulate hourly snowfall, road-clearing progress, and preparedness options.

**Current focus: the map only.** Build a usable interactive view of a small, real St. John's road network. Users should be able to explore streets, understand their published snow-clearing priorities where verified, and select multiple streets for later snow-depth comparisons.

No snowstorm simulation, forecast model, or AI recommendation engine is being implemented in this phase.

### Desired user experience

Picture a single-page application with:

- A **large, interactive map** of St. John's displaying road geometries from a public data source.
- A **street search and multi-selection control** near the map (for example, in a sidebar).
- **Visual highlighting** of selected streets; selecting a street should highlight its relevant segments rather than just one piece of geometry.
- A **street information area** showing available attributes such as name, verified snow-clearing priority, and approximate length.
- A simple **road-priority legend** and an obvious indication when priority data is unknown.
- A reserved area for **future simulated snow-depth graphs and a time selector**. Until a simulation is connected, show a clear unavailable/coming-later state; do not invent values.

Map-based street selection is desirable, but a reliable searchable selector is the first priority. Add click-to-select only if it works consistently with the chosen mapping library.

### Scope and boundaries

#### In scope now

- Retrieve or load actual public road geometries for a manageable subset of St. John's streets.
- Render those streets on an interactive map with zoom and pan.
- Display street names and any verified road-clearing priorities.
- Support selecting and deselecting multiple streets.
- Highlight selected streets and show their details.
- Keep map data and selected-street state organized for future simulation integration.
- Handle missing or ambiguous source data clearly.

#### Out of scope now

- Predicting snowfall, actual road safety, or real-world clearing completion times.
- Snow accumulation or snowplow activity simulation.
- Snowplow routing, crew/resource optimization, or live dispatch.
- AI-generated preparedness recommendations.
- Real-time road-condition integrations, historical GPS reconstruction, or a production-grade government deployment.
- Building snow-depth charts before simulation output exists.

### Public data sources to investigate

| Source | Why it is useful | Data-access caution |
|---|---|---|
| [City of St. John's ArcGIS road layer](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Street geometries, names, and possible street/segment identifiers for the map | Confirm the endpoint and relevant fields with a small live query before relying on them. A street may span many segments; check for incomplete or duplicated geometry. |
| [City of St. John's snow-clearing service levels](https://www.stjohns.ca/resident-services/snow-clearing/service-levels-priority/) | Public explanation of how municipal roads are prioritized for snow clearing | This is the policy context, not necessarily a downloadable street-by-street dataset. |
| [City street-priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Verify the actual priority of streets selected for the pilot | A public lookup is not proof of a bulk API. Manual verification for a small subset is acceptable. |
| [OpenStreetMap](https://www.openstreetmap.org/) | Potential backup for road geometry/basemap data | Source and attribution differ from the City's GIS; do not silently mix identifiers or treat OSM road classes as City snow-clearing priorities. |

**Important distinction:** A GIS field describing road *class* does not automatically establish the City's official *snow-clearing priority*. Only label priorities as official if they have been verified using an authoritative source. Otherwise, display “Priority unavailable.”

Public data might be available for viewing without providing an immediately usable bulk export. Test access before planning around automated extraction.

### Initial data concepts

Keep the internal representation simple and adaptable to the data actually retrieved.

- **Road segment:** A mapped piece of street geometry with a source identifier, street name, and optional attributes.
- **Street:** A logical grouping of one or more road segments that users can select together.
- **Priority:** An optional, verified municipal snow-clearing priority associated with a street or segment, with a note about its source.
- **Selection state:** The set of streets currently selected by the user.
- **Future snow state:** Optional simulation results tied to a road or segment and a time point; this does not exist yet.

Do not assume all features have names, that names uniquely identify streets, or that every segment has the same priority. Where grouping by street name is ambiguous, inspect identifiers and make a deliberate pilot-specific choice.

For the initial pilot, a small, manually reviewed collection of approximately **5–10 streets** is preferable to an unverified city-wide import.

### Suggested implementation approach

A lightweight Python application using **Streamlit** and a mapping library such as **Folium** is a reasonable starting point. GeoJSON works well for transferring geometries and keeping data separate from presentation. These are recommendations rather than hard requirements; use an alternative if it offers cleaner and more reliable map interaction.

#### Phase A — Verify and prepare the streets

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

#### Phase B — Draw the map

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

#### Phase C — Street selection and details

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

#### Phase D — Prepare for later simulation integration

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

### Suggested repository organization

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

### What to verify while building

- The selected streets are genuinely present in the downloaded St. John's GIS data.
- Coordinates and geometries render in the correct locations.
- Multi-segment streets are selected and highlighted consistently.
- Priority labels match the City's lookup or remain explicitly unavailable.
- Multi-street selection persists across normal UI rerenders.
- A missing GIS response or empty dataset produces a clear message; a verified local copy may be used if available.
- Nothing on the map suggests that simulated snow depth, clearing completion, or travel safety has been calculated yet.
- If using OpenStreetMap as a basemap, preserve its attribution.

### Definition of done for the map-only MVP

A user can open the application, inspect a **real, small St. John's street network**, search for and select several streets, see them highlighted, and read accurate available street details and snow-clearing priority information. The interface makes unknown data explicit and has a clear integration boundary for future hourly simulation results.

### How coding assistants should use this context

- Start by inspecting the existing project and reusing its patterns where possible.
- Prefer a small, working vertical slice over a broad or overly engineered build.
- Verify data availability instead of assuming undocumented endpoints, fields, or historical records exist.
- Use straightforward implementation choices and explain trade-offs when data or interactive map behavior is uncertain.
- Treat pseudocode and suggested structure as guidance, not mandatory source-code contracts.
- Keep the current feature focused on the map; do not implement the full SnowStorm AI simulator unless explicitly requested.

## Future phase: storm simulation and preparedness

The following preserves the broader product plan for later work. It does not expand the current map implementation scope. Its data, interpretation, and privacy safeguards also apply whenever relevant to the map.

### Broader product purpose

Build a winter storm simulation and preparedness planner for selected streets in St. John's, Newfoundland and Labrador.
Help public works and emergency-planning teams compare snowfall timing, street priorities, and assumed snow-clearing resources.
The minimum viable product (MVP) targets an eight-hour proof of concept.

Illustrative comparison: one 200 cm storm on Friday versus two 100 cm storms on Thursday and Saturday.
Six plows illustrate an assumed resource setting.
These values are examples, not observations or confirmed fleet availability.

### Core user flow

1. Select the pilot streets and review their sources.
2. Configure two hourly snowfall scenarios.
3. Enter assumed clearing resources, operating hours, productivity, and clearing target.
4. Run both simulations using clearly disclosed assumptions.
5. Compare hourly remaining snow, clearing progress, and plow-hours.
6. Review a preparedness brief grounded in the simulation results.

### Future simulator MVP scope

| Feature | Required behavior | Output |
| --- | --- | --- |
| Storm scenario builder | Accept user-defined snowfall totals, timing, and hourly profiles. | Two editable scenarios. |
| Plow workload simulator | Allocate available plow-hours in street priority order. | Hourly remaining snow, work used, and clearing progress. |
| AI preparedness brief | Interpret structured results and disclose assumptions. | A traceable comparison and preparedness suggestions. |

Use 5–10 verified streets for the pilot.
In the original eight-hour simulator plan, a map was optional when geometry preparation threatened the time budget. The current map phase below takes precedence for present work.
The app must support scenario changes without code edits.

### Non-negotiable interpretation rules

- Label every model estimate `SIMULATED`.
- Label every user-defined operational parameter `ASSUMED`.
- Distinguish sourced street information from assumptions and synthetic examples.
- Never present simulated clearing time as actual municipal recovery time.
- Never infer verified accessibility, road safety, or actual equipment availability.
- Never fabricate missing observations, source values, or historical validation results.
- Treat all mockup values, road colours, and forecast curves as synthetic design placeholders.
- Keep assumptions and data provenance visible in the interface.

### Data contract

| Input | Required fields | Requirements |
| --- | --- | --- |
| `roads.csv` | `road_id`, `road_name`, `length_km`, `priority` | Verify lengths from GIS and priorities through public sources. |
| `scenario_a.csv` | `hour`, `snowfall_cm` | User-defined hourly profile for the first scenario. |
| `scenario_b.csv` | `hour`, `snowfall_cm` | User-defined hourly profile for the second scenario. |
| UI settings | `plows`, `plow_speed_or_rate`, `operating_hours`, `clearing_target` | Disclose every operational value as an assumption. |

The example scenario profiles each total 200 cm.
Users must retain control over exact duration and hourly intensity.
Record source URLs, download dates, verification status, and transformations in the README.
Do not interpret missing snowfall observations as zero snowfall.

### Source inventory

These statuses come from the baseline plan.
This context file does not independently verify current source access.

| Source | Intended use | Baseline status |
| --- | --- | --- |
| [ECCC Historical Climate Data](https://climate.meteo.gc.ca/) | Historical weather context and sample storm selection. | Station coverage and complete hourly snowfall remain unverified. |
| [City roads GIS](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0) | Street names, geometry, and lengths. | Plan reports GeoJSON support; pilot extraction needs testing. |
| [City service levels and priority](https://www.stjohns.ca/resident-services/snow-clearing/service-levels-priority/) | Published priority definitions and service context. | Plan lists P1 arterial, P2 collector, P3 local, and P4 city-maintained private lanes. |
| [Street Priority Lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) | Verify selected streets individually. | Public lookup reported; bulk download remains unverified. |
| [511NL Road Conditions API](https://511nl.ca/help/endpoint/winterroads) | Possible future external reference. | Developer key required; current provincial conditions, not municipal history. |
| [Where the Plow](https://plow.jackharrhy.dev/) | Possible historical plow coverage. | Export, coverage, and reuse conditions remain untested. |
| [City AVL tracker](https://map.stjohns.ca/avl/) | Possible live plow reference. | Archive export and fleet count remain unverified. |

Use manually entered snowfall profiles when complete observations are unavailable.
Skip GPS ingestion when sample access fails.
Use hand-selected verified streets if automated road extraction fails.
Historical municipal road conditions are unavailable for validation within the baseline plan.

### Simulation contract

Use an hourly, rule-based simulation.
For each hour:

1. Load the hour's snowfall and available operating time.
2. Add snowfall to every pilot road segment.
3. Assign available plow-hours in published priority order.
4. Limit clearing by equipment count, productivity, operating time, and road length.
5. Update remaining snow and record work performed.
6. Store hourly results for scenario comparison.

Conceptual update rule:

```text
remaining_next = max(0, remaining_current + hourly_snowfall - simulated_clearing)
```

Never allow negative remaining snow or work beyond available plow-hours.
Use consistent units when converting productivity into segment clearing depth.
Define the clearing target before reporting time to target.
Report an unmet target explicitly when the simulation ends before reaching it.

#### Decisions required before coding

- Select and verify the 5–10 pilot streets.
- Define productivity units and their relationship to road length and snow depth.
- Define the clearing target and network-level completion rule.
- Define operating schedules and treatment of partial plow-hours.
- Define ordering among streets with equal priority.
- Define the shared scenario timeline, timezone, and simulation end condition.
- Decide whether both scenarios share operational settings or expose differences explicitly.

The baseline plan does not fully specify these mechanics.
Document each choice before interpreting simulation outputs.

### AI brief contract

A large language model (LLM) drafts the preparedness brief from structured simulation results.
Provide both storm inputs, total plow-hours, hourly remaining snow, priority order, and documented assumptions.
The brief should explain workload differences, priority concentration, and influential resource assumptions.
Tie every numerical statement to a supplied result field.
Do not invent metrics or describe suggestions as official recommendations.

Use a fixed text template when the LLM API is unavailable.
Clearly label that fallback as non-AI output.
The simulation must remain usable without the LLM.

### Implementation stack

| Component | Technology |
| --- | --- |
| Simulation | Python |
| CSV preparation | Pandas |
| Interface | Streamlit |
| Hourly charts | Plotly |
| Storage | CSV |
| Preparedness brief | Accessible LLM API, with a non-AI fallback |

The MVP does not require a dedicated database, Docker stack, or production authentication.
The repository, API provider, deployment target, and team roles remain unspecified.

### Eight-hour delivery plan

| Elapsed time | Work | Deliverable |
| --- | --- | --- |
| 0:00–0:30 | Define pilot and simulation contract. | Inputs, clearing target, and assumptions. |
| 0:30–1:30 | Verify access and extract streets. | Small road dataset with provenance. |
| 1:30–2:15 | Verify priorities and prepare scenarios. | Complete road attributes and editable hourly profiles. |
| 2:15–4:45 | Implement accumulation and capacity-limited assignment. | Two scenarios running end to end. |
| 4:45–6:00 | Build controls and comparison charts. | Working local interface. |
| 6:00–7:00 | Add the preparedness brief. | Grounded LLM brief or labelled fallback. |
| 7:00–8:00 | Test and document. | Verified constraints and README. |

### Completion criteria

- Users run and compare two scenarios without changing code.
- Every hour respects available plow-hours and clearing capacity.
- Remaining snow never becomes negative.
- Outputs distinguish public street information from operational assumptions.
- Results include an hourly comparison and traceable preparedness summary.
- Charts and briefs avoid validated safety and actual recovery claims.
- The README records sources, assumptions, model choices, limitations, and run instructions.

Minimum checks cover zero snowfall, split storms, and constrained capacity.
Also verify priority allocation, operating-hour limits, and an unreachable clearing target.
Check that the fallback brief works when the LLM API fails.

### Explicit exclusions

- Trained machine-learning models.
- Real-time dispatch or detailed vehicle routing.
- City-wide coverage.
- Validated hazard forecasts or road-safety classifications.
- Claims about real plow availability.
- Unverified historical road-recovery results.
- Drifting snow, compaction, melting, freezing rain, traffic, and equipment failure.

### Working conventions

For the future simulator phase, keep the eight-hour scope central when evaluating new features. For current work, follow the map-only scope.
Resolve model definitions before expanding the interface.
Preserve the separation between simulation calculations and AI interpretation.
Update this file when scope, model contracts, source verification, or completion status changes.
Record implementation evidence before marking a feature complete.
Keep CanAI project discussions and artifacts private unless Amanda explicitly authorizes sharing.

### Future simulator next steps

1. Confirm pilot streets and complete the simulation contract decisions.
2. Test road extraction and verify priorities.
3. Prepare the two hourly profiles and operational assumptions.
4. Implement and verify the simulation before adding AI interpretation.
