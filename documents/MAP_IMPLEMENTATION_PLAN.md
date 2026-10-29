# Implementation Plan

SnowStorm AI: map-only MVP (application title: Flurry)
Prepared: 2026-10-28
Status reviewed: 2026-10-28
Classification: CanAI Garage
Overall status: map functionality substantially implemented; data assurance and final acceptance remain open.

This document records observed implementation progress. It does not establish retrospective approval or authorize new dependencies, architecture changes, data refreshes, deployment, or publication.

## 1. Requested Outcome

Deliver a local map of 5–10 real St. John's streets with searchable multi-selection, all-segment highlighting, recorded municipal snow-clearing priorities, source information, and explicit unavailable states.

Finish the map phase before adding simulation, forecasts, or AI recommendations. The Simulation tab remains a placeholder.

## 2. Current-State Findings

Status legend:

- [x] **Done:** supported by inspected code, saved records, or executed automated checks. This does not imply browser acceptance or live-source verification.
- [ ] **In progress:** partly implemented or awaiting validation. This does not imply someone is actively assigned.
- [ ] **Not started:** no implementation or completion evidence was found in this review. Historical activities without records remain unverified.

| Phase | Status | Evidence and remaining work |
| --- | --- | --- |
| 0. Coordination and approval | In progress / records unverified | Existing implementation and pilot inspected; ownership agreement and prior approval records were not established by this review. |
| 1. Road geometry | In progress | Eight-street snapshot and fetcher exist; source completeness, grouping, provenance, and length units need validation. |
| 2. Priority verification | In progress | Section priorities, mixed values, and source links are saved; dated verification and conflict checks remain open. |
| 3. Map rendering | In progress | Rendering, legend, labels, and styling exist; source comparison, viewport behaviour, and tooltip escaping remain open. |
| 4. Selection and failure handling | In progress | Core selection and session-refresh behaviour pass focused tests; data-contract and edge-case gaps remain. |
| 5. Validation and handover | In progress | Five automated tests pass; browser acceptance, remaining data checks, and final handover are incomplete. |

The actual structure uses `components/`, `services/`, and JSON priority records. Earlier `src/` and CSV paths were proposals and should not be created merely to match the original plan.

## 3. Files Inspected

- `README.md`: setup, operation, sources, and limitations.
- `documents/PROJECT_CONTEXT.md`: current map-only scope and future simulator boundaries.
- `documents/MAP_IMPLEMENTATION_PLAN.md`: original requirements and acceptance criteria.
- `app.py`: Map, Simulation, and Dev note composition.
- `components/map_tab.py`: map rendering, searchable selection, details, and legend.
- `components/data_refresh.py`: session refresh, validation, and failure feedback.
- `components/simulation_tab.py`: explicit unavailable-data placeholder.
- `services/street_data.py`: local loading and geometry/attribute validation.
- `scripts/fetch_pilot_streets.py`: City requests, priority parsing, and saved-file output.
- `data/street_priorities.json`: eight pilot records, sections, source URLs, counts, and approximate lengths.
- `tests/test_app.py` and `tests/test_data_refresh.py`: regression coverage.
- `requirements.txt`: existing unpinned Streamlit, Folium, streamlit-folium, and requests dependencies.

The review ran local automated tests. It did not make live City requests or conduct a browser accessibility review. Saved geometry is exercised by the loader and map tests; complete extents and source identity were not independently verified.

## 4. Scope

### In scope

- Real pilot geometry, reviewed provenance, and recorded municipal priorities.
- Interactive map, searchable multi-selection, highlighting, details, and legend.
- Honest unknown/mixed states and controlled data-loading failures.
- Local operation, focused tests, manual acceptance, and handover.

### Outside the current phase

- Snowfall simulation, charts, time controls, forecasts, or AI recommendations.
- Plow routing, live tracking, city-wide ingestion, accounts, databases, deployment, or publication.
- Mandatory click-to-select. The map is currently display-only; the sidebar is the selection control.

## 5. Confirmed Facts and Open Questions

- [x] **Done:** the pilot list is WATER ST, DUCKWORTH ST, GOWER ST, MILITARY RD, KENMOUNT RD, PRINCE PHILIP DR, SIGNAL HILL RD, and FRESHWATER RD.
- [x] **Done:** the application loads saved data and supports session-only refresh.
- [x] **Done:** mixed priorities are recorded by published section; the map colours the whole street with a mixed-priority colour.
- [ ] **In progress:** confirm complete intended geometry, unique source segment IDs, and the suitability of grouping by street name.
- [ ] **Not started:** record extraction and priority-verification dates; do not infer them from this document's review date.
- [ ] **Not started:** verify the source `LENGTH` units and aggregation method before accepting displayed metre values.
- [ ] **Not started / unverified:** reconcile contributor ownership, dependency approval, and architecture approval with existing team records. Code presence is not evidence of approval.

## 6. Current Approach and Data Contract

Reuse the existing Python, Streamlit, Folium, and streamlit-folium implementation. No replacement frontend, new dependency, CSV migration, or directory restructuring is proposed by this status update.

```text
City road query ----------> pilot_streets.geojson ---+
City priority form -------> street_priorities.json -+--> validated loader
                                                    --> map + selection + details
Session refresh ----------> validation -------------> session dataset only
```

Current selection and priority joins use street names. The original plan preferred reviewed stable street IDs; duplicate-name ambiguity has not been resolved or tested. Preserve source identity and review the grouping before deciding whether an ID migration is necessary. Any such change requires its own exact proposal.

GeoJSON remains longitude/latitude; rendering converts points to latitude/longitude for Folium. Multipart sections are drawn separately. Session state holds the canonical `selected_streets` list. Approximate lengths currently sum the source `LENGTH` values and label them metres; the units remain unverified.

Priority records contain section text, priority levels, source links, segment counts, and approximate lengths. They lack dated verification metadata. Source links establish recorded provenance, not independent verification in this review.

## 7. Phased Implementation Checklist

### Phase 0: Coordinate ownership and approval

- [x] **Done:** inspect the current local implementation, stack, and pilot configuration.
- [ ] **In progress:** reconcile the implemented name-based contract with the original stable-ID proposal.
- [ ] **Not started / unverified:** confirm contributor file ownership and recorded approvals.
- [ ] **Not started:** establish a reproducible, tested dependency-version record; `requirements.txt` is unpinned. Dependency changes require approval.

### Phase 1: Retrieve and review real road geometry

- [x] **Done:** implement City queries requesting GeoJSON with `outSR=4326` and explicit request timeouts.
- [x] **Done:** save a pilot snapshot and load it locally.
- [x] **Done:** preserve separate multipart road sections and validate supported, nonempty geometry and coordinate ranges.
- [ ] **In progress:** review source fields, service limits, intended extents, grouping ambiguity, and reuse conditions. Historical metadata findings do not prove complete extraction.
- [ ] **Not started:** reconcile expected source IDs/counts, handle transfer limits with paging or ID batches, and detect duplicate IDs.
- [ ] **Not started:** escape apostrophes in query literals before accepting arbitrary street names. The current pilot is fixed.
- [ ] **Not started:** record extraction date, query, grouping decisions, and length units.
- [ ] **In progress:** protect saved snapshots. Session refresh validates before replacement; command-line output currently writes both saved files without the shared validation or an atomic replacement strategy.

Files: `scripts/fetch_pilot_streets.py`, `services/street_data.py`, `data/pilot_streets.geojson`. Data provenance documentation remains outstanding.

Completion: complete intended extents, unique source IDs, reviewed grouping, valid coordinates, recorded provenance, and safe snapshot replacement.

### Phase 2: Verify priorities

- [x] **Done:** implement City form lookup and save section descriptions, source URLs, priority levels, and mixed values.
- [x] **Done:** represent missing priorities explicitly; do not infer priorities from GIS road class.
- [ ] **In progress:** independently review published sections and their coverage against the pilot geometry and service-level definitions.
- [ ] **Not started:** record verification dates and scope notes for each reviewed priority.
- [ ] **Not started:** validate unmatched street records and contradictory priority/section information rather than silently accepting them.

Files: `data/street_priorities.json`, `scripts/fetch_pilot_streets.py`, `services/street_data.py`.

Completion: every displayed priority has reviewed, dated evidence; unknown or mixed scope remains explicit; mismatches and conflicts are reported.

### Phase 3: Render the pilot map

- [x] **Done:** implement cached local data loading and a Folium rendering function.
- [x] **Done:** render road parts with text tooltips, priority colours, neutral unknown styling, mixed styling, legend, and source information.
- [x] **Done:** fit bounds to selected streets and distinguish selection with thicker, more opaque lines.
- [ ] **In progress:** compare all pilot positions and extents with the authoritative source in a browser.
- [ ] **Not started:** validate initial pilot-wide bounds and viewport retention. The current map starts at a fixed centre and refits when streets are selected.
- [ ] **Not started:** explicitly escape external text in HTML tooltips/popups.

Files: `components/map_tab.py`, `services/street_data.py`, `app.py`.

Completion: correct pilot location and coverage, readable labels, honest priorities, safe tooltip content, and accepted viewport behaviour.

### Phase 4: Selection, details, and failure handling

- [x] **Done:** provide searchable multi-selection with a stable widget key and shared session state.
- [x] **Done:** highlight every mapped part of selected streets and render matching detail panels.
- [x] **Done:** support empty and multiple selections; automated checks exercise selecting two streets and clearing selection.
- [x] **Done:** preserve valid selection through successful refresh and keep session data after mocked request/validation failures.
- [x] **Done:** show controlled local-data errors without blocking other tabs.
- [x] **Done:** show source links, unavailable attributes, and an explicit simulation placeholder.
- [ ] **In progress:** removal of absent street names is implemented, but no clear notice is shown; changed-dataset behaviour needs focused validation.
- [ ] **Not started:** resolve name-based grouping/selection ambiguity against the stable-ID requirement.
- [ ] **Not started:** validate displayed length units or propose withholding unverified lengths.
- [ ] **Not started:** verify individual removal, normal browser rerenders, and usability when basemap tiles fail.
- [ ] **In progress:** basic malformed-data validation exists; conflict, duplicate-ID, and geometry/priority join checks remain incomplete.

Files: `components/map_tab.py`, `components/data_refresh.py`, `services/street_data.py`, `tests/`.

Completion: selection, highlights, and details stay synchronized; invalid/conflicting inputs are handled; failures preserve valid data; displayed measurements are supported.

### Phase 5: Validate and hand over

- [x] **Done:** run all five existing automated tests on 2026-10-28; all pass.
- [x] **Done:** document local setup, sources, refresh semantics, colour meanings, and key limitations in README.
- [x] **Done:** update this implementation plan to reflect observed status.
- [ ] **In progress:** expand meaningful data-validation coverage for the remaining gaps below.
- [ ] **Not started:** complete and record browser acceptance, keyboard accessibility, contrast, narrow-screen layout, and attribution checks.
- [ ] **Not started:** reconcile stale project-context status and README test-coverage statements.
- [ ] **Not started:** complete dated provenance, validated run instructions, and final handover/acceptance records.

Files: `tests/test_app.py`, `tests/test_data_refresh.py`, `README.md`, `documents/PROJECT_CONTEXT.md`; location of additional provenance notes remains to be agreed.

Completion: acceptance criteria pass or Amanda explicitly accepts documented limitations.

## 8. File Status and Remaining Work

| File | Current state | Remaining work |
| --- | --- | --- |
| `requirements.txt` | Exists; unpinned | Review reproducibility and approvals before any dependency changes. |
| `app.py` | Implemented | No entry-point restructuring required. |
| `components/map_tab.py` | Implemented | Viewport, tooltip escaping, selection notices, and manual acceptance. |
| `components/data_refresh.py` | Implemented; mocked regression coverage | Retain validation and preservation behaviour as checks improve. |
| `services/street_data.py` | Implemented | Duplicate IDs, joins, consistency, and contract validation. |
| `scripts/fetch_pilot_streets.py` | Implemented | Completeness, provenance, source errors, query escaping, and safe saved-file replacement. |
| `data/pilot_streets.geojson` | Saved snapshot exists | Review identities, grouping, and complete intended extents. |
| `data/street_priorities.json` | Eight records exist | Dated verification, scope, and validated lengths. |
| `tests/test_app.py` | Four tests pass | Add relevant data and selection edge cases. |
| `tests/test_data_refresh.py` | One test passes with multiple failure subcases | Add changed-dataset cases where needed. |
| `README.md` | Operational documentation exists | Correct stale refresh-test coverage and record final validation. |
| `documents/PROJECT_CONTEXT.md` | Scope authority exists | Reconcile outdated implementation-status language. |
| `documents/MAP_IMPLEMENTATION_PLAN.md` | Updated in this task | Maintain evidence-based progress markers. |

These are remaining work areas, not authorization to modify every listed file.

## 9. Testing and Validation

Executed during the progress review on 2026-10-28:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Result: **5 tests passed**. Coverage includes tab composition, multiple-street selection and clearing, selected-part highlighting, empty geometry rejection, isolated map-load failure, and mocked refresh success/failure with session-data preservation. Python reported a temporary-directory cleanup `PermissionError` after the successful test summary; the process exit code was 0. This cleanup issue remains unresolved.

Remaining automated checks:

- [ ] **Not started:** duplicate source IDs and duplicate-name separation.
- [ ] **In progress:** malformed geometry and missing/mixed priorities; existing coverage is limited.
- [ ] **Not started:** inconsistent section priorities, conflicting joins, and unmatched geometry/priority records.
- [ ] **Not started:** changed snapshots containing absent selections and expected user notices.
- [ ] **Not started:** truncated source responses and safe command-line snapshot writes.

Manual acceptance checklist (not performed in this review):

- [ ] **Not started:** launch with documented commands and compare positions/extents against the source.
- [ ] **Not started:** use the keyboard to search and select three streets; verify all parts and details.
- [ ] **Not started:** remove one selection, clear all, and repeat after rerenders; check viewport behaviour.
- [ ] **Not started:** verify mixed/unavailable labels and published section coverage.
- [ ] **Not started:** check malformed input, failed preparation, and preservation of saved snapshots.
- [ ] **Not started:** check blocked/missing tiles and continued access to text details.
- [ ] **Not started:** check keyboard focus, labels, contrast, narrow-screen stacking, attribution, and colour-independent selection cues.

## 10. Risks and Controls

- Incomplete or incorrectly grouped geometry: reconcile source counts/IDs and review extents before acceptance.
- Unsupported length labels: verify units and computation; propose withholding values if evidence is unavailable.
- Incorrect priority scope: retain published sections and mixed/unavailable labels; add dated human verification.
- Saved-data loss: validate complete replacements before writing; retain the previous valid snapshot. Session preservation does not establish command-line safety.
- Unpinned dependencies: record the tested environment and seek approval for any manifest changes.
- Viewport resets or inaccessible interaction: complete browser checks before readiness sign-off.
- Source markup changes: the priority fetcher automates an ASP.NET form rather than a documented priority API; parser behaviour needs source verification.
- External tooltip text: escape source content before HTML rendering.

Keep protected project material local. Basemap assets require network access; source access and tile attribution/reuse requirements still apply. No AI service is required for this phase. Deployment and publication remain separately controlled.

Rollback for future repairs: retain the prior valid dataset and make focused reversible code changes without overwriting teammate work. This documentation update changes no runtime behaviour or data.

## 11. Documentation Checklist

- [x] **Done:** README describes local startup, components/services layout, session refresh, sources, colours, and limitations.
- [x] **Done:** this plan reflects implementation and validation evidence.
- [ ] **Not started:** update project context's stale unverified-implementation statement.
- [ ] **Not started:** correct README's statement that refresh error paths lack tests; mocked coverage now exists, live-source validation remains open.
- [ ] **Not started:** record extraction dates, verified priority dates, grouping rationale, reuse checks, length method/units, and tested package versions.
- [ ] **Not started:** record browser acceptance outcomes, unresolved limitations, and handover decisions.

## 12. Acceptance Criteria

- [ ] **In progress:** documented local launch and approved dependencies; AppTest executes the app, but browser launch/approval records were not verified.
- [ ] **In progress:** eight real pilot streets are represented; complete reviewed geometry remains unverified.
- [ ] **In progress:** search, multi-selection, and clearing are implemented/tested; individual removal and keyboard/browser acceptance remain open.
- [x] **Done:** all mapped parts of selected streets highlight and matching details render in automated checks; successful mocked refresh preserves valid selection.
- [ ] **In progress:** priority source links and explicit unknown/mixed states exist; dated verification and scope assurance remain open.
- [x] **Done:** the interface distinguishes planning priorities from current road safety, snow depth, and clearing completion; simulation output is explicitly unavailable.
- [ ] **In progress:** legend, labels, attribution, and thicker selection lines exist; browser accessibility checks remain open.
- [ ] **In progress:** controlled load errors and failed session-refresh preservation are tested; conflict detection and safe saved-file replacement remain open.
- [ ] **In progress:** five automated tests pass; manual acceptance and accepted limitations are not yet recorded.

## 13. Recommended Execution Order

1. Validate pilot completeness, source identity, grouping, priority scope, and length units. Record evidence and dates.
2. Prepare exact, focused repairs for any confirmed gaps; obtain approval where required before applying them.
3. Add meaningful regression coverage for approved data/fetch/selection repairs and rerun the suite.
4. Complete browser, accessibility, viewport, and tile-failure acceptance checks.
5. Reconcile README and project context, record provenance and handover evidence, and review remaining limitations with Amanda.
6. Close the map MVP only after acceptance. Plan simulation separately if requested.

Confirm ownership before assigning the remaining work. Source assurance and manual acceptance may be coordinated separately, but final sign-off depends on both.

## 14. Approval and Next Action

This status update was requested by Amanda. Only this implementation-plan document is changed; no application, dependency, dataset, deployment, or publication change is authorized by the update.

**Next implementation work:** the data-assurance pass in step 1 above, followed by exact repair proposals where needed. Existing implementation is not being restarted at Phase 0. Missing historical approval or validation evidence remains open rather than being checked off retroactively.
