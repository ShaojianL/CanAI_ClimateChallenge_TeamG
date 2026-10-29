# Group G Implementation Plan

Project: Community Crisis Reporting Map
Team: Adam, Amanda, Farhan, Victoria, and Wilson
Updated: October 29, 2026
Baseline: PROJECT_CONTEXT.md version 3.1
Classification: CanAI hackathon business project
Delivery target: Eight-hour MVP
Status: Proposed implementation; ownership and technical decisions require team agreement.

This plan supersedes the previous snow-clearing map-only plan. The project context governs product direction. Creating this plan does not authorize application changes, new dependencies, schemas, permissions, external transfers, infrastructure, deployment, or publication. Applicable repository and individual approval requirements remain in force alongside team review.

## 1. Requested Outcome

Deliver a repeatable demonstration:

**Submit a synthetic report -> staff approve publication -> the assigned map segment updates -> a subscribed destination receives a relevant street update.**

Pending, rejected, and unresolved reports remain private. Approval permits publication; it does not verify the hazard, establish road safety, or imply municipal action. The prototype is independent of official municipal emergency systems and is not an emergency-reporting service.

## 2. Current-State Findings

- The existing Streamlit/Folium frontend provides street search, multi-street selection, highlighting, street details, and session-only City-data refresh.
- Saved geometry contains 156 features across eight streets, with 156 distinct OBJECTID values. Identifier stability and complete street membership still require review.
- Current colours describe snow-clearing priority, not recent hazard-report volume.
- Map interactions currently return no objects to Streamlit. Individual segment selection and details require implementation.
- Street choices currently depend on priority records. Reporting needs a reviewed street/segment registry independent of snow-clearing priority.
- Report persistence, intake, staff review, subscriptions, AI summaries, and delivery were not established in the inspected implementation.
- A standalone deterministic snow-simulation engine and tests exist, although its interface remains a placeholder. Preserve that work outside this MVP.
- README, DESIGN.md, development notes, and the previous implementation plan describe the deprecated scope.

These findings come from code and local-data inspection. No tests, browser acceptance checks, live City validation, or provider delivery checks were run during plan preparation.

## 3. Files Inspected

| Files | Planning relevance |
| --- | --- |
| documents/PROJECT_CONTEXT.md | Product baseline, lifecycle, privacy, acceptance, and open decisions |
| documents/IMPLEMENTATION_PLAN.md | Previous execution direction |
| documents/DESIGN.md and README.md | Existing interface guidance, setup, and limitations |
| app.py and requirements.txt | Entry point, navigation, and existing dependencies |
| components/map_tab.py and components/data_refresh.py | Map rendering, selection, and geometry refresh |
| components/simulation_tab.py and components/dev_note_tab.py | Existing navigation and deprecated messaging |
| services/street_data.py and scripts/fetch_pilot_streets.py | Loading, validation, source fetching, and saved-data output |
| services/simulation.py | Existing simulation logic outside the pivot |
| tests/test_app.py, tests/test_data_refresh.py, tests/test_simulation.py | Existing regression coverage |
| data/pilot_streets.geojson | Local feature counts and identifier uniqueness |

## 4. Scope

### In Scope

- Synthetic hazard submission and receipt acknowledgement.
- Private staff review, location resolution, redacted public wording, and explicit approval/rejection.
- Segment-level approved-report counts, recent-volume colours, details, and text alternatives.
- Grounded AI summaries with traceable inputs and deterministic fallback.
- Whole-street subscriptions, explicit consent, unsubscribe, real delivery, and retry tracking.
- Repeatable demo, focused tests, and team handover.

### Out of Scope

Snowfall simulation, plow workloads, routing, fleet allocation, dispatch, hazard prediction, validated severity ratings, new geographic boundaries, city-wide coverage, production municipal integration, and a full moderation platform. Production identity management is deferred; an appropriate minimal staff-access boundary is still required.

## 5. Assumptions and Open Questions

### Confirmed Facts

The product requires staff approval before public display or delivery. Reuse the current frontend and suitable saved geometries. Attempt free outbound SMS first; use email if free SMS is infeasible. Inbound SMS requires separate proof.

### Planning Assumptions

- Use synthetic reports and explicitly authorized test destinations.
- Start with a small reviewed pilot, expanding only if time permits.
- Prefer explicit street/segment selection if automated location resolution threatens the time budget.
- A labelled manual trigger may run the hourly notification workflow during the demo.
- Proposed defaults: previous 60 minutes by receipt time; grey 0, blue 1-4, orange 5-14, red 15+; hourly relevant updates.

### Open Questions

| Decision | Priority | Required evidence or resolution |
| --- | --- | --- |
| Intake channel | Blocking before intake integration | Prove inbound SMS separately or agree on app entry |
| Persistence and staff access | Blocking before shared use | Approved schema, storage behaviour, and enforced access boundary |
| SMS/email provider | Blocking before real delivery | Actual delivery; cost, Canadian support, recipient restrictions, and trial limits |
| Street grouping | Blocking before report/subscription integration | Reviewed identifiers and complete membership for chosen pilot streets |
| AI service and processing boundary | Blocking before external AI calls | Approved provider, payload scope, credentials, and permitted transfer |
| Hosting and scheduling | Important but non-blocking for local demo | Persistent storage support and hourly execution, or labelled manual trigger |
| Final defaults and notification age limit | Important but non-blocking for initial logic | Team decision on thresholds, interval, boundary semantics, and old-report wording |

## 6. Recommended Approach

Keep app.py focused on navigation, feature UI in components/, and shared logic in services/. Avoid a frontend rewrite.

For a local single-process demo, propose standard-library SQLite persistence to avoid a new database dependency. This remains an architecture/schema proposal requiring approval. Confirm hosting and persistence needs before adopting it for shared deployment.

Create internal street and segment identifiers with reviewed source references. Do not use street-name text alone for joins or assume STREET_ID identifies an entire street. Freeze reviewed geometry during the demo; defer geometry migration and reject incompatible refreshes.

Enforce one publication rule across counts, summaries, and notifications: the report is approved, has a valid resolved segment, and has reviewed public wording. Enforce authorization in review actions, not only by hiding navigation.

Map eligibility uses receipt time. Notification eligibility uses publication time and per-subscription delivered-report membership so late approvals are not skipped. Advance delivery tracking only on confirmed success. Recheck active subscription status before sending. Define ambiguous provider-timeout handling rather than blindly retrying and promising exactly-once delivery.

AI receives only approved, redacted descriptions, report identifiers, locations, times, verification labels, and application-calculated counts. Treat report text as data. Retain input identifiers, label AI output, and invalidate summaries when inputs change or age out. Use a labelled deterministic summary when AI fails.

Provide a keyboard-accessible segment selector even if map-click selection cannot be completed reliably. Counts describe reports, not unique residents, verified incidents, severity, or safety.

## 7. Phased Implementation Plan

Time boxes are targets, not commitments or completion records. Each workstream needs one named owner agreed by the team.

| Phase / time | Objective and tasks | Likely files | Dependencies | Validation and completion evidence |
| --- | --- | --- | --- | --- |
| 0:00-0:30 Feasibility | Verify messaging/intake; review pilot mapping; select storage, staff access, and AI approach; prepare exact approval proposals | Decision notes in this plan; proposed contracts | Authorized tests and team decisions | Evidence-backed choices, restrictions, owners, and fallback paths recorded |
| 0:30-1:30 Registry and lifecycle | Implement registry, persistence, report states, UTC timestamps, and deduplication | services/report_store.py, services/reporting.py, data/street_registry.json | Approved schema/storage | One submission stored once against a valid segment; restart retains records; invalid transitions rejected |
| 1:30-3:00 Intake and review | Implement intake, pending acknowledgement, private queue, redacted wording, approve/reject, and access checks | components/report_tab.py, components/review_tab.py, app.py | Lifecycle and approved access mechanism | Pending/rejected/unresolved reports stay private; unauthorized actions fail; explicit approval publishes only the intended report |
| 3:00-4:15 Public map | Implement segment selection, counts, thresholds, age-out, details, stale/error states, and reporting legend; remove deprecated priority/depot messaging from reporting view | components/map_tab.py, services/street_data.py, components/data_refresh.py | Reviewed registry and publication rule | Only assigned segment changes; thresholds and expiry work; keyboard/text path available |
| 4:15-5:15 Summaries | Implement deterministic fallback, approved AI adapter, provenance, labels, and invalidation | services/summaries.py | Approved redacted inputs and AI integration | Mixed hazards summarized faithfully; unsupported claims rejected or replaced; AI failure leaves intake/counts working |
| 5:15-6:15 Subscriptions and delivery | Implement whole-street consent, private destination storage, unsubscribe, attempts, retries, and shared manual/hourly workflow | components/subscriptions_tab.py, services/notifications.py | Registry, published reports, approved provider | Relevant real message arrives; unrelated streets excluded; failures remain eligible; unsubscribe suppresses delivery |
| 6:15-7:15 Integration and failure checks | Exercise full journey, privacy boundaries, timing edges, retries, and access controls | tests/test_app.py and new reporting tests | Integrated core workflow | Automated checks and recorded manual acceptance demonstrate required boundaries |
| 7:15-8:00 Documentation and demo | Reconcile setup/design/development notes; record limitations, commands, owners, and demo steps | README.md, documents/DESIGN.md, this plan, components/dev_note_tab.py | Actual implementation and validation evidence | Another team member repeats the synthetic demonstration and understands limitations |

If the schedule slips, reduce automated location handling, map-click polish, and pilot coverage first. Preserve staff approval and the complete reporting-to-map-to-delivery journey. Simulation delivery is a documented limitation, not evidence of real messaging completion.

## 8. Proposed File Changes

New module names are provisional until technical decisions are approved.

| File | Action | Purpose | Risk |
| --- | --- | --- | --- |
| app.py | Modify | Reporting navigation and agreed working title | Medium |
| components/map_tab.py | Modify | Segment counts, selection, details, and recent-volume legend | Medium |
| components/data_refresh.py | Modify | Prevent incompatible geometry replacement | Medium |
| components/report_tab.py, components/review_tab.py, components/subscriptions_tab.py | Create | Intake, private review, consent, and unsubscribe UI | High: access and privacy |
| services/street_data.py | Modify | Geometry/registry loading independent of priority records | Medium |
| services/report_store.py, services/reporting.py | Create | Persistence, lifecycle, and shared publication rules | High: data integrity |
| services/summaries.py, services/notifications.py | Create | Grounded summaries and controlled delivery | High: external processing/delivery |
| data/street_registry.json | Create | Reviewed internal identifiers and source membership | Medium |
| tests/test_app.py and new reporting test modules | Modify/create | Verify new contracts and preserve relevant regressions | Low |
| README.md, documents/DESIGN.md, components/dev_note_tab.py | Modify | Reconcile product, setup, and limitations | Low |
| documents/IMPLEMENTATION_PLAN.md | Modify | Replace old plan with shared Group G implementation plan | Low; documentation only |
| .gitignore | Modify if needed | Exclude approved runtime database and local secret files | Low |
| requirements.txt | No change initially | Add dependencies only when justified and approved | Approval required if changed |
| Simulation module and tests; original geometry/priority snapshots | No change required | Preserve existing work outside MVP | Low |

The approved persistence proposal must specify runtime database location, access, backup/reset, and retention. Credentials must stay outside source control.

## 9. Testing and Validation

Use injected clocks and mocked provider responses for deterministic automated tests. Required cases:

- Duplicate intake/provider retry persists once without inflating counts.
- Pending, rejected, and unresolved reports never appear publicly or enter updates.
- Public users cannot read raw text/contact data or perform review actions.
- Count boundaries: 0, 1, 4, 5, 14, 15; exact window boundary; future/invalid timestamps; age-out.
- Approval leaves verification unchanged and affects only the assigned segment.
- Late approval remains notification-eligible even when absent from recent map counts.
- Whole-street membership includes other member segments and excludes unrelated streets.
- No newly eligible reports produces no message; repeated triggers do not resend known successes.
- Failures retain eligibility; unsubscribe before send suppresses attempts; ambiguous timeouts have documented behaviour.
- Public responses, logs, and AI inputs exclude private contacts and raw messages.
- Mixed hazards, conflicting reports, empty inputs, embedded instructions, and provider failure produce grounded output or labelled fallback.
- Geometry refresh cannot silently orphan stored reports or subscriptions.

Run the existing suite plus approved new tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Update tests tied to intentionally replaced tabs and priority colours while preserving meaningful regression checks. Do not weaken failing tests to obtain a pass.

Manually verify keyboard access, visible focus, readable contrast, narrow-screen layouts, map/text consistency, stale/loading/failure states, private staff isolation, and real delivery to an authorized destination. Display pilot times in America/St_Johns while storing UTC.

## 10. Risks and Controls

| Risk | Likelihood | Impact | Mitigation | Fallback / rollback |
| --- | --- | --- | --- | --- |
| Free SMS unavailable or restricted | High | Medium | Time-box actual provider proof and restrictions | Verified email delivery |
| Wrong street grouping or unstable references | Medium | High | Review source IDs and membership; freeze snapshot | Reduce to manually reviewed pilot |
| Private data or staff actions exposed | Medium | High | Public projections, authorized actions, protected storage, redaction | Keep demo local and synthetic; disable unsafe shared access |
| Lost or duplicate delivery | Medium | High | Persist attempts and delivered membership; define timeout handling | Stop sender, inspect outcomes, retry eligible failures |
| Unsupported AI claims | Medium | High | Approved inputs, traceability, uncertainty labels, evaluation | Deterministic standard summary |
| Scope exceeds eight hours | High | High | Protect core journey; explicit selection and manual workflow trigger | Smaller pilot and documented limitations |
| Hosting cannot preserve chosen storage | Unknown | High | Validate persistence/concurrency before deployment | Local single-process demonstration |
| Public interprets volume as safety | Medium | High | Clear labels, timestamps, unverified status, no-report disclaimer | Revise wording before exposure |

Retain original geometry and simulation work. Keep changes reviewable and reversible. Disable external delivery before rollback; preserve relevant delivery outcomes so reverting code does not cause accidental resend.

## 11. Documentation Updates

Update README, DESIGN.md, development notes, and this plan to match actual behaviour. Record:

- Setup, launch/test commands, actual environment-variable names, and provider restrictions.
- Staff-access boundary, approved persistence location, and pilot registry provenance.
- Receipt/publication timing, thresholds, counts, stale states, and verification semantics.
- Consent, unsubscribe, retries, ambiguous delivery outcomes, and scheduler/manual-trigger limitations.
- AI processing boundary, allowed inputs, labels, provenance, and fallback.
- Synthetic demo/reset steps, validation evidence, known gaps, and team handover owners.

Define retention/deletion before collecting real public reports. Keep CanAI artifacts private; no protected content transfer without specific authorization.

## 12. Acceptance Criteria

- [ ] One synthetic report persists once and remains private pending review.
- [ ] Only authorized staff approval publishes a resolved report with suitable public wording.
- [ ] Pending, rejected, and unresolved reports never enter public counts, summaries, or messages.
- [ ] Approval updates only the correct segment and does not mark the hazard verified.
- [ ] Counts, thresholds, and age-out follow the agreed reporting window.
- [ ] Segment details show hazard types, count, times, window, verification status, and grounded summary.
- [ ] A street subscription covers all reviewed member segments and excludes unrelated streets.
- [ ] A relevant real SMS or email update reaches an authorized destination; no eligible reports means no message.
- [ ] Delayed approval remains eligible; failed delivery remains retryable; unsubscribe stops future attempts.
- [ ] AI output is supported by traceable redacted inputs; failure produces labelled standard output.
- [ ] Public outputs and AI payloads exclude private raw submissions and contacts.
- [ ] Keyboard/text alternatives and recorded manual accessibility checks support the core journey.
- [ ] Another team member can repeat the demonstration using the documented setup and limitations.

Unchecked criteria are requirements, not completion claims. Target WCAG 2.2 AA without claiming compliance before evaluation.

## 13. Recommended Execution Order and Team Ownership

Agree on feasibility and contracts -> approve technical scope -> registry/persistence -> intake/review -> public map -> summaries -> subscriptions/delivery -> integrated validation -> documentation/demo.

| Workstream | Responsibility | Owner |
| --- | --- | --- |
| Integration | Maintain contracts, sequence decisions, and assemble demo | Team to assign |
| Data and lifecycle | Registry, persistence, deduplication, and publication rules | Team to assign |
| Intake and review | Resident intake and private authorized staff workflow | Team to assign |
| Map and accessibility | Segment display, counts, readable details, and keyboard path | Team to assign |
| AI and notifications | Grounded summaries, fallback, consent, delivery, and retry | Team to assign |
| Validation and handover | Acceptance evidence, failure checks, setup, and demo repeatability | Team to assign |

Members may own multiple workstreams. Do not infer assignments from the team roster. After contracts are agreed, map presentation and provider adapters can proceed independently. Integration and release assessment depend on the shared publication contract and actual end-to-end evidence.

## 14. Team Review and Approval Checkpoint

Planning is complete. No application implementation changes have been made; this plan document is the only change. The Group G team should review scope, defaults, ownership, and acceptance criteria before implementation begins.

The next action is Phase 0: gather authorized feasibility evidence and prepare exact schema, persistence, staff-access, and provider proposals. Team agreement does not replace applicable repository, privacy, or individual approval requirements. Obtain approval for each defined implementation scope and external action before execution; record material deviations and review them again.
