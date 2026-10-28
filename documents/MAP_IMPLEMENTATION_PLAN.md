# Implementation Plan

SnowStorm AI: map-only MVP  
Prepared: 2026-10-28  
Classification: CanAI Garage  
Status: proposed; this document authorizes no application implementation or dependency installation.

## 1. Requested Outcome

Build a local application showing 5–10 real St. John's streets. Users can search for and select several streets, see all their relevant segments highlighted, and inspect verified snow-clearing priorities or an explicit unknown state.

Deliver the map before adding simulation, forecasts, or AI recommendations.

## 2. Current-State Findings

- The repository contains `README.md`, `PROJECT_CONTEXT.md`, and `SnowStorm_AI_Map_Copilot_Context.md`.
- No application source, dependency manifest, tests, or local road dataset was present in the inspected working directory.
- `PROJECT_CONTEXT.md` establishes the map-only scope and takes precedence over the older simulator plan.
- Python, Streamlit, Folium, and GeoJSON are suggested technologies, not an existing installed application architecture.
- The City road-layer metadata retrieved through the browser identifies a polyline layer, projected coordinate reference EPSG:32181, and fields including `OBJECTID`, `STREETNAME`, `STREETPREF`, `STREETSUFF`, `STREETCODE`, and `LENGTH`. Metadata access does not establish a successful feature download, grouping rule, length units, or permission for every reuse.
- Official snow-clearing priorities must be verified separately; road class is insufficient evidence.
- The colleague is building the map. His unpublished code, branch, chosen streets, and technology decisions have not been inspected.

## 3. Files Inspected

| Source | Purpose |
| --- | --- |
| Repository root listing and tracked-file discovery | Establish available implementation and documentation |
| `PROJECT_CONTEXT.md` | Authoritative scope, data boundaries, and completion criteria |
| `SnowStorm_AI_Map_Copilot_Context.md` | Supporting map requirements |
| `README.md` | Existing project introduction |
| Amanda's supplied global instructions | Approval, privacy, and collaboration boundaries |
| Business-project profile and shared `PRODUCT_PRINCIPLES.md` | Applicable project standards |
| Amanda's Planner and developing-with-streamlit skills | Planning structure and implementation reference workflow |

External references checked during planning:

- [City road-layer metadata](https://map.stjohns.ca/mapsrv/rest/services/community/Basemap/MapServer/0?f=pjson).
- [Streamlit multiselect documentation](https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect).
- [streamlit-folium project](https://github.com/randyzwitch/streamlit-folium).

Verify documentation against the versions selected during implementation. No feature extraction or application validation has been performed for this plan.

## 4. Scope

### In Scope

- Small, reviewed public road dataset with provenance.
- Interactive road map with zoom, pan, labels, and attribution.
- Searchable multiple-street selection and synchronized highlighting/details.
- Verified priority labels, neutral unknown styling, and a legend.
- Clear loading, missing-data, and invalid-data messages.
- Local run instructions and focused validation.

### Out of Scope

- Snowfall simulation, charts, time controls, AI briefs, and safety predictions.
- Plow routing, live tracking, city-wide ingestion, accounts, databases, deployment, and publication.
- Mandatory map-click selection; add only after the searchable selection works reliably and its scope is approved.

## 5. Assumptions and Open Questions

### Confirmed Facts

The current objective is the map-only MVP. A small pilot and explicit unknown priorities are acceptable. The colleague owns map development.

### Assumptions

- The first deliverable runs locally in a browser.
- Public road information can be prepared as a local snapshot after checking reuse conditions.
- The team will choose one compact pilot area rather than disconnected streets across the entire city.
- Missing length or priority values may remain unavailable.

### Open Questions

| Question | Importance | Resolution |
| --- | --- | --- |
| Does the colleague already have code or a chosen stack? | Blocking before scaffolding | Inspect and reuse his work before creating competing files |
| Which 5–10 streets form the pilot? | Blocking before final extraction | Agree one list and identify street extents |
| Are proposed dependencies and architecture approved? | Blocking before installation/build | Review the exact manifest and implementation scope |
| Does street priority vary by segment? | Important but non-blocking | Preserve segment-specific evidence; show mixed/unavailable when necessary |
| Are approximate road lengths required for the first demo? | Optional clarification | Omit until measurement method and units are verified |

## 6. Recommended Approach

If no implementation already exists, propose Python + Streamlit + Folium with `streamlit-folium` for embedding. Streamlit supplies the searchable selector and details area; Folium renders line geometry. Confirm compatible versions before approval. Use standard-library JSON, CSV, HTTP, and unittest capabilities where sufficient; do not add Pandas or GeoPandas solely for this small dataset.

Prefer the colleague's existing working stack if it satisfies the requirements. A custom JavaScript frontend or backend service would add unnecessary setup for this pilot.

### Data flow

```text
City road query -> reviewed local GeoJSON -> validated street index
City priority verification -------------> reviewed priority CSV
                                               |
                           selected street IDs |
                                               v
                             map + details + legend
```

### Proposed data contract

Each road feature retains its source segment ID and geometry, plus a reviewed `street_id` and display name. Store GeoJSON coordinates as WGS84 longitude/latitude. Folium map centers and explicit bounds use latitude/longitude: do not reverse GeoJSON coordinates globally.

Use `OBJECTID` as source segment identity within the downloaded snapshot, not a promise of permanent identity. Inspect `STREETCODE` before deciding whether it supports grouping. Otherwise assign reviewed local street IDs and retain the mapping to source segments. Do not group solely by display name without reviewing ambiguity.

Priority CSV columns: `street_id`, optional `segment_id`, `priority`, `verification_status`, `source_url`, `verified_on`, and `notes`. Use empty priority plus an explicit unavailable status when unverified. Define whether a row applies to the whole street or one segment; conflicting rows must produce a validation error rather than silently overriding evidence.

Keep one canonical set of selected street IDs in Streamlit state. The selector, highlighted geometry, and details read from that set. Use human-readable labels for ID options and disambiguate duplicate names.

The UI shows a large map, a labelled searchable selector, selected-street details, a priority legend, and source/verification notes. Differentiate selection with a thicker contrasting outline so it remains distinguishable from priority colour. Display “Simulation data unavailable” as text; do not add nonfunctional time controls.

## 7. Phased Implementation Plan

### Phase 0 — Coordinate ownership and approve the build

- Inspect the colleague's branch/code and dependency choices.
- Agree pilot streets, file ownership, and one data contract.
- Present exact dependency versions and proposed file content for approval before implementation.
- Files: no application changes in this phase.
- Dependency: team agreement and Amanda's approval.
- Validation/completion: both contributors use the same street IDs and know which files they own.

### Phase 1 — Retrieve and review real road geometry

- Inspect layer metadata and query capabilities; confirm field names and service limits.
- Make a small sample query before requesting the pilot.
- Request GeoJSON with `outSR=4326`, relevant fields, and geometry. Construct parameters with URL encoding and escape apostrophes in any SQL string literals.
- Query object IDs/counts for the selected streets first; retrieve all corresponding segments using supported paging or ID batches. Check transfer-limit indicators and reconcile returned IDs to expected IDs.
- Preserve multipart geometry; reject empty or unsupported geometries. Review the map against the source for missing pieces and ambiguous street names.
- Save the reviewed snapshot and provenance. Use timeouts and explicit HTTP/ArcGIS error handling; never replace a valid snapshot with a failed or empty response.
- Files: `scripts/prepare_roads.py`, `data/roads.geojson`, `data/README.md`.
- Dependencies: approved stack, access/reuse checks, pilot list.
- Validation/completion: 5–10 reviewed streets, unique segment IDs, complete intended extents, valid WGS84 coordinates, and recorded extraction date/query.

### Phase 2 — Verify priorities in parallel

- Amanda checks the agreed streets in the [City lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx) and reviews [service-level definitions](https://www.stjohns.ca/resident-services/snow-clearing/service-levels-priority/).
- Record exact scope, source, date, and unavailable or mixed values. Do not assume bulk API access or derive priority from road class.
- Map developer continues with unknown priorities while verification proceeds.
- Files: `data/road_priorities.csv`; data-source notes coordinated with the map owner.
- Dependency: agreed IDs and pilot list; geometry preparation need not finish first.
- Validation/completion: every published priority is traceable; unmatched IDs and conflicts are reported.

### Phase 3 — Render one real street, then the pilot

- Build a local data loader and a Folium rendering function.
- Start with one reviewed street; check position and every segment before loading all pilot roads.
- Fit initial bounds to the pilot. Avoid resetting pan/zoom on every ordinary interaction where the selected embedding supports retaining viewport state.
- Style verified classes consistently and unknown values neutrally; include text labels and attribution.
- Escape external text used in HTML tooltips/popups.
- Files: `src/roads.py`, `src/map_view.py`, `app.py`, approved dependency manifest.
- Dependency: Phase 1 snapshot; Phase 2 optional until labels are verified.
- Validation/completion: pilot appears in St. John's with readable names and honest priority labels.

### Phase 4 — Add selection, details, and failure handling

- Populate `st.multiselect` with stable street IDs and formatted labels.
- Use a stable widget key; highlight every feature with a selected ID and update details from the same state.
- Support no selection, multiple selections, individual removal, and clearing all selections.
- Preserve selection through normal rerenders; discard IDs absent from a newly loaded snapshot with a clear notice.
- Show approximate lengths only if units and computation are validated. Never calculate kilometres by summing degree distances or assume an undocumented `LENGTH` unit.
- Show controlled messages for missing, malformed, empty, or conflicting input; keep search/details usable if basemap tiles fail.
- Files: `app.py`, `src/roads.py`, `src/map_view.py`.
- Dependency: Phase 3.
- Validation/completion: selection, highlights, and details stay synchronized without rerun loops.

### Phase 5 — Validate and hand over

- Run the checks below, record outcomes, and fix failures within approved scope.
- Amanda runs acceptance checks while the developer owns repairs.
- Document installation, local launch, provenance, limitations, and troubleshooting.
- Files: `tests/test_roads.py`, `README.md`, `data/README.md`.
- Dependency: Phases 2–4.
- Completion: acceptance criteria pass or remaining limitations are explicitly accepted.

## 8. Proposed File Changes

Paths are proposals to reconcile with the colleague's implementation before creating files.

| File | Action | Purpose | Risk |
| --- | --- | --- | --- |
| `requirements.txt` | Create after approval | Pin tested direct dependencies | Dependency/compatibility approval required |
| `app.py` | Create | Compose widgets, state, map, and details | UI behavior |
| `src/roads.py` | Create | Validate data, group segments, join verified attributes | Data integrity |
| `src/map_view.py` | Create | Render geometry and selection styles | Coordinate and display correctness |
| `scripts/prepare_roads.py` | Create | Explicit public-data retrieval/preparation | Incomplete extraction or source changes |
| `data/roads.geojson` | Create | Reviewed geometry snapshot | Source quality and reuse conditions |
| `data/road_priorities.csv` | Create | Independently verified priority evidence | Incorrect priority or scope |
| `data/README.md` | Create | Provenance, transformation, grouping, and units | Documentation accuracy |
| `tests/test_roads.py` | Create | Verify grouping, joins, and invalid inputs | Low |
| `README.md` | Modify after approval | Setup, operation, and limitations | Low |
| `PROJECT_CONTEXT.md` | No change required now | Remains scope authority | Update later only with verified implementation status |

## 9. Testing and Validation

Use standard-library `unittest` for meaningful data logic. Tests must verify multi-segment grouping, duplicate-name separation, missing priorities, segment-specific/mixed priorities, conflicting joins, malformed geometry, duplicate IDs, and selection containing absent IDs.

Proposed commands after implementation and dependency approval:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Manual acceptance procedure:

1. Open the app and compare street positions/extents to the authoritative map.
2. Search for a pilot street using the keyboard; select three streets.
3. Verify every segment highlights and details match the selected IDs.
4. Remove one street, clear all, and repeat after normal rerenders.
5. Verify unavailable and mixed priorities remain explicit in the map and details.
6. Test an empty/malformed dataset and failed GIS preparation; the previous reviewed snapshot must survive.
7. Test missing basemap tiles; document that cached road geometry does not guarantee offline basemap availability.
8. Check keyboard operation, visible labels, contrast, narrow-window layout, attribution, and colour-independent selected-state cues.

No application tests have been run: no implementation exists in the inspected workspace.

## 10. Risks and Controls

| Risk | Likelihood / impact | Control and fallback |
| --- | --- | --- |
| Overlapping teammate edits | Medium / high | Agree ownership first; integrate small reviewed changes without replacing his code |
| Truncated or incorrectly grouped roads | Medium / high | Reconcile source IDs/counts, inspect extents, and reduce pilot scope if ambiguous |
| Projected coordinates treated as degrees | Medium / high | Request EPSG:4326 and verify actual locations before styling |
| Unverified or conflicting priorities | Medium / high | Preserve provenance; show unavailable/mixed instead of guessing |
| Unsupported dependency combination | Medium / medium | Test and pin approved versions in an isolated environment |
| Map rerenders reset state or loop | Medium / medium | Selector is canonical; defer click selection and test rerenders |
| Source or tile outage | Medium / medium | Keep reviewed local roads, usable text details, and clear tile limitations |
| External content rendered as HTML | Low / medium | Escape source text; avoid rendering arbitrary HTML |

Keep project materials local. Runtime basemap providers receive network requests that may reveal the viewed area; disclose this behavior and preserve attribution. Do not upload project source or deploy the app without separate approval. No AI service is needed.

Rollback: retain the prior reviewed dataset and restore it if refresh validation fails. Keep implementation on a separate branch and reverse approved changes without deleting a colleague's work. Never overwrite a snapshot until validation succeeds.

## 11. Documentation Updates

Update README setup and launch commands only after they work. Record Python/package versions, data refresh procedure, extraction dates, source URLs, attribution/reuse checks, segment grouping decisions, priority verification dates, and any verified length method in `data/README.md`.

Document that priority is not road safety or live clearing status, the pilot is limited, basemap tiles need network access, and simulation is unavailable. Include troubleshooting for missing files, malformed data, no roads displayed, and failed tile loading.

## 12. Acceptance Criteria

- App launches locally with documented commands and approved dependencies.
- It displays 5–10 real, reviewed streets in St. John's with complete intended pilot geometry.
- Users search, select several streets, remove them individually, and clear selection.
- All relevant segments highlight, with matching details and persistent normal-rerender selection.
- Every official priority label has evidence; unknown and mixed values are explicit.
- No interface claims current road safety, actual snow depth, or clearing completion.
- Legend, readable labels, keyboard-accessible selection, and attribution are present.
- Invalid data produces understandable errors; failed refreshes preserve the last reviewed snapshot.
- Focused tests and manual acceptance results are recorded with honest limitations.

## 13. Recommended Execution Order

1. Confirm the colleague's current implementation and ownership.
2. Agree pilot streets and the street-ID contract.
3. Approve exact architecture, dependencies, and implementation changes.
4. Developer retrieves/reviews geometry; Amanda verifies priorities in parallel.
5. Developer renders one street, then all pilot streets.
6. Developer adds searchable selection and details, then integrates Amanda's verified priorities.
7. Amanda runs acceptance checks and drafts the demo explanation; developer fixes issues.
8. Finalize verified run instructions and review completion together.

The developer owns application, geometry, and dependency files. Amanda owns the priority-verification draft, acceptance checklist, and demo copy. Coordinate changes to shared documentation and final CSV integration through one owner. This division does not require either person to edit the other's in-progress files.

## 14. Approval Checkpoint

Planning is complete. No implementation changes have been made. Review and approve the plan before implementation begins.

After approval, begin Phase 0 by reconciling this proposal with the colleague's code and presenting the exact dependency manifest and first implementation patch. Saving this requested planning document does not approve the proposed build, data refresh, deployment, or publication.
