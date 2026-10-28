# SnowStorm AI Design

Last updated: 2026-10-28  
Status: design draft for the map-only MVP. Implementation and technology choices remain unapproved and unverified.

## Purpose and document boundaries

This document explains the intended user experience, data flow, component responsibilities, and validation criteria for SnowStorm AI's first map. Its primary audience is the team implementing and reviewing the pilot.

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) defines the authoritative project scope and separates the map MVP from future simulation.
- [MAP_IMPLEMENTATION_PLAN.md](MAP_IMPLEMENTATION_PLAN.md) proposes delivery steps, file ownership, dependencies, and approval checkpoints.
- This design describes how the intended experience fits together. It does not approve architecture, dependencies, data retrieval, or deployment.

The inspected repository contains documentation and no application source, dependency manifest, tests, or prepared road dataset. Reconcile this draft with the colleague's map implementation before creating competing components.

## User goal and scope

A pilot user should be able to explore a small St. John's road network, search for several streets, see their complete relevant geometry highlighted, and inspect verified snow-clearing priority information.

The pilot covers approximately 5–10 reviewed streets. It includes pan and zoom, searchable multi-selection, street details, a priority legend, provenance, and explicit missing-data states.

Simulation, snowfall forecasts, snow-depth charts, time controls, plow routing, live conditions, accounts, and AI recommendations are outside this phase. Snow-clearing priority does not establish travel safety or actual clearing progress.

## Main user journey

1. Open the application and see the pilot map, dataset coverage, and priority legend.
2. Search the labelled street selector and select one or more streets.
3. See all relevant segments of each selected street highlighted.
4. Read matching street details, including verified priorities or an explicit unavailable or mixed state.
5. Remove streets individually or clear the selection. Highlights and details update together.

The searchable selector is the required selection path. Map-click selection is an optional later enhancement, subject to reliable library support and agreed scope.

## Interface structure

Use a single page with the map as the main visual area and a nearby selection and details panel. On narrow screens, stack controls, map, and details in a readable order.

```text
SnowStorm AI | St. John's pilot map
Pilot coverage and data limitations

Street search and selection | Interactive road map
Selected streets           | Priority legend
Street details             | Source and attribution

Simulation data unavailable
```

### Controls and details

- Label the selector “Select streets” and support searching, multiple selections, removal, and “Clear selection.”
- Show readable names while storing street IDs. Disambiguate duplicate names with reviewed location or identifier information.
- For each selected street, show its name, priority status, and available verification information. Include approximate length only after confirming measurement method and units.
- Show “Select streets to view details” when the selection is empty.
- Show “Simulation data unavailable” as explanatory text. Do not display inactive charts or controls that imply calculated results exist.

### Map styling and accessibility

- Distinguish verified priority categories with consistent styles and a labelled legend. Use a neutral style for unknown priorities.
- Show selected roads with a contrasting outline or increased line weight that preserves priority meaning.
- Repeat priority and selection information in text; colour and map interaction must not be the only ways to understand the data.
- Provide keyboard-operable selection, visible focus, clear labels, readable text, and sufficient contrast. Essential details must remain available outside hover tooltips.
- Avoid decorative motion and unnecessary panels. Keep attribution visible.

Exact colours, spacing, and mapping-library behavior remain implementation decisions to review against the working interface.

## Proposed components and data flow

The implementation plan suggests Python, Streamlit, Folium, and GeoJSON if no suitable teammate implementation already exists. These are proposals, not installed or approved dependencies. Preserve a working team stack if it meets the requirements.

The intended flow separates data preparation from ordinary UI interaction:

```text
Public road source -> reviewed local geometry -> validation and street index
City priority evidence -> reviewed priority records -----------|
                                                              v
Street selector -> canonical selected street IDs -> map and details
```

Data preparation retrieves and reviews geometry and priority evidence. Loading validates the local snapshot and builds a street-to-segments index. The page owns selection state; map rendering and details read the same validated data and selected IDs.

Normal selection changes should use the prepared local dataset rather than trigger fresh GIS extraction. External basemap tiles may still require network access.

These are logical responsibilities. Final modules and filenames should follow the colleague's implementation and avoid unnecessary abstraction.

## Proposed data contract

### Road segments and streets

A road segment is one source geometry. A selectable street groups one or more reviewed segments.

- Retain each segment's source identifier, source street name, geometry, and provenance.
- Assign or verify a stable pilot `street_id` and a human-readable display name.
- Maintain an explicit mapping from each selectable street to its relevant segments. Do not assume a name is unique or sufficient for grouping.
- Treat source object IDs as identifiers within the downloaded snapshot unless their long-term stability is established.
- Store GeoJSON geometry in WGS84 longitude/latitude. Adapt map-center and bounds arguments to the chosen library's coordinate order.
- Check geometry types, coordinate reference system, duplicate identifiers, missing names, and intended street extents before rendering.

The implementation plan records projected source coordinates and candidate GIS fields. Confirm those details during extraction; this document does not independently verify the endpoint or its current schema.

### Priority evidence

The implementation plan proposes priority records containing `street_id`, optional `segment_id`, `priority`, `verification_status`, `source_url`, `verified_on`, and `notes`.

- Define whether each record applies to a whole street or a specific segment.
- Only label a priority official when supported by authoritative City evidence.
- Represent unverified priority as missing with an explicit unavailable status. Never substitute road class for snow-clearing priority.
- Preserve verified segment differences. Show mixed priorities when evidence establishes variation; disclose incomplete coverage separately.
- Reject conflicting records rather than silently choosing one.
- Retain source and verification dates so reviewers can distinguish evidence from assumptions.

Length is optional. Omit it or show “Length unavailable” until units and the calculation method are verified.

## Selection and update behavior

Maintain one canonical collection of selected street IDs. The selector, road highlights, selected count, and details must derive from it.

Selection persists across normal page rerenders within the active session. Persistence across browser restarts is outside the current requirements. If a dataset change invalidates selected IDs, report the mismatch and reconcile selection explicitly rather than showing stale details.

If map-click selection is added later, resolve the clicked segment to its reviewed street ID and update the same collection. Avoid a separate map selection state that can diverge from the selector.

## Empty, loading, and failure states

- **Loading:** Display a clear loading message while preparing the view.
- **No selected streets:** Keep the map usable and explain how to view details.
- **No search matches:** Explain that the street may fall outside the pilot coverage.
- **Unknown priority:** Display “Priority unavailable” in details and neutral map styling.
- **Missing or invalid dataset:** Explain that road data could not be loaded. Do not present a blank map as a successful load.
- **Failed data refresh:** Preserve the previous reviewed snapshot; replace it only after the new data passes validation.
- **Unavailable basemap tiles:** Keep available street details and selection usable, and explain the background-map limitation.

Do not manufacture geometry, priority values, snow depths, or operational estimates to fill gaps.

## Provenance, privacy, and trust boundaries

Record geometry sources, retrieval dates, coordinate transformations, grouping decisions, priority evidence, and attribution in the prepared dataset documentation. Check reuse conditions before incorporating data.

The City GIS, City priority lookup, and possible OpenStreetMap fallback are investigation sources listed in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md). Their inclusion does not establish successful extraction or permission for every reuse. An OSM road classification cannot verify a City priority.

Treat external names and attributes as untrusted text and escape them in map popups or other HTML. Keep project materials local; publication and uploads require separate authorization. Basemap requests may disclose the viewed area to a tile provider, and a local geometry snapshot does not provide a fully offline map.

No AI service is needed for this phase. Any future AI recommendation feature requires its own grounding, evaluation, uncertainty handling, and human review design.

## Acceptance and validation

Before calling the map MVP complete, verify:

- The agreed 5–10 real streets appear in the correct locations with their intended segments.
- Search, multi-selection, individual removal, and clearing work; highlights and details remain synchronized across normal rerenders.
- Duplicate names remain distinguishable, and no selected street silently loses segments.
- Every official priority has evidence. Missing, conflicting, incomplete, and mixed records receive the documented treatment.
- Malformed geometry, duplicate IDs, absent selection IDs, and conflicting joins are covered by focused data-logic tests.
- Missing files, empty datasets, failed refreshes, and tile outages produce understandable states.
- Keyboard selection, focus, contrast, narrow-screen layout, text alternatives, and attribution are manually reviewed.
- The interface makes no unsupported claim about road safety, snow depth, or clearing completion.

Record actual test and manual-review results when implementation exists. No application tests or interface checks have been performed for this document.

## Open decisions and maintenance

Resolve the teammate's current stack and file ownership, pilot street list and extents, grouping identifiers, priority coverage, dependency versions, and optional length method before implementation. Exact visual tokens and optional click-selection behavior also remain open.

Keep simulation separate from map selection and rendering. A later phase can introduce time-indexed results keyed to reviewed road IDs, but must first define units, temporal meaning, segment aggregation, and uncertainty. Do not build those contracts prematurely.

Update this document when a design decision is approved or verified behavior changes. Keep delivery sequencing in the implementation plan and scope authority in the project context. The team should confirm a maintainer for shared design documentation.
