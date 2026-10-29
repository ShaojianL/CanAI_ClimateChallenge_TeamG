# CanAI Hackathon Project Context

Working title: Community Crisis Reporting Map
Version: 3.1
Updated: October 29, 2026
Pilot: St. John's, Newfoundland and Labrador
Delivery target: Eight-hour hackathon MVP
Status: Confirmed product direction; new capabilities and integrations remain unverified.

## 1. Product baseline

Build a community hazard-reporting tool that connects resident submissions, staff approval, a public road-segment map, and street-based notifications.

Residents report local problems such as flooding, blocked drains, or snow obstructions. Staff review submissions before anything appears publicly. Approved reports contribute to segment-level report counts and summaries. Residents can subscribe to an entire street and receive updates about newly approved reports on that street.

The primary demonstration is:

**Submit a synthetic report -> staff approve publication -> the correct map segment updates -> a subscribed destination receives a relevant update.**

A pending or rejected report must never change public counts, appear in a public summary, or enter a subscriber update. Approval permits publication; it does not verify the hazard or imply municipal action.

This prototype supports investigation and awareness. It is independent of official municipal emergency systems, is not an emergency-reporting service, and does not establish road safety.

## 2. Confirmed decisions and working defaults

| Topic | Baseline | Status |
| --- | --- | --- |
| Product direction | Community crisis reporting and street updates | Confirmed by Amanda, October 29, 2026 |
| Publication | Staff approval required before public display or subscriber delivery | Confirmed |
| Notification preference | Free outbound SMS to a chosen real phone number; email if free SMS is not feasible | Confirmed |
| Report submission channel | To be selected during feasibility; inbound SMS is not established by outbound SMS support | Open |
| Geography | Reuse existing road geometries; count at segment level | Preferred first implementation approach |
| Subscription coverage | All mapped segments belonging to the selected street | Discussion baseline |
| Map reporting window | Previous 60 minutes, based on report receipt time | Proposed demo default |
| Volume thresholds | Grey: 0; blue: 1-4; orange: 5-14; red: 15 or more | Proposed demo defaults |
| Delivery interval | Hourly, only when newly approved relevant reports exist | Proposed demo default |
| Public title | Community Crisis Reporting Map | Working title; current app title is Flurry |

Confirmed direction does not mean the integrations, schema, access controls, or deployment are approved or implemented. Defaults are explicit starting points, not validated hazard thresholds.

## 3. Four MVP features

### A. Hazard submission

- Capture a description, receipt timestamp, hazard type, and location.
- Store one report record per submission; deduplicate messaging retries by provider message identifier when applicable.
- Resolve the report to one mapped road segment. An ambiguous location remains private until clarified.
- Acknowledge receipt as pending review, without promising publication, verification, or response.
- Keep raw text and reporter contact references private. Prepare a redacted public description.

The intake channel remains open. Incoming SMS requires its own feasibility test. An app-based form with explicit segment selection is a possible fallback, not a confirmed implementation choice. Do not silently guess a segment.

### B. Minimal staff review

- Show a private queue containing the report description, time, hazard type, and proposed segment.
- Let staff approve or reject publication after checking location and the public description for inappropriate or personal content.
- Block publication when the segment is unresolved or the public description is unsuitable.
- Record review outcome and review/publication times with a private reviewer reference where available.
- Keep hazard verification separate: approving publication leaves the report unverified unless staff separately confirm it.

A minimal review interface is required. A fuller moderation dashboard is deferred. Staff controls must not be available to public users; the access approach is an unresolved implementation decision and must be settled before exposing the prototype publicly.

### C. Public reporting map

- Reuse the existing pilot road geometries, street search, and suitable selection interactions.
- Colour each segment using its approved recent-report count, replacing the old snow-clearing-priority meaning in the reporting view.
- Provide segment details: street/segment label, count, hazard types, grounded summary, reporting window, latest update, and verification status.
- Refresh counts when reports are approved and when they age out of the window.
- Support readable text information alongside the map; colour alone must not carry meaning.

Individual segment selection and its details interaction require implementation; they are not established as existing features.

### D. Street subscriptions and notifications

- Let a resident choose a mapped street and explicitly consent to updates at a private notification destination.
- Cover all mapped segments belonging to that street.
- Attempt free outbound SMS first. If that is not feasible, deliver by email.
- Send only when newly approved relevant reports exist; omit unrelated streets, pending reports, and rejected reports.
- Support unsubscribe and check active subscription status before delivery.
- Record delivery outcomes. Advance successful-delivery tracking only after success; retain failures for retry.
- Permit a clearly labelled manual trigger for the hourly workflow during the demo. A manual trigger can send a real message; simulated delivery must be labelled separately.

## 4. User journeys

### Resident

1. Browse the map without subscribing and search for a pilot street.
2. Read approved report counts, summaries, timestamps, and unverified labels.
3. Choose a street, enter the destination for the selected notification channel, and explicitly opt in.
4. Submit a report through the confirmed intake channel and provide enough detail to resolve its segment.
5. Receive a pending-review acknowledgement; the report is not yet public.
6. After staff approval, see the segment update if the report is still within the reporting window.
7. Receive a street update when newly approved relevant reports are available.
8. Unsubscribe to stop future updates.

### Staff

1. Open the private review queue.
2. Inspect location, description, hazard type, time, and proposed public wording.
3. Resolve ambiguity before approval, or reject the submission.
4. Approve publication while preserving the separate verification status.
5. Inspect approved report concentrations on the map and investigate before making operational decisions.

## 5. Report lifecycle and publication rules

**Received -> pending clarification when needed -> pending staff review -> approved or rejected.**

Only valid, location-resolved, staff-approved reports may enter public outputs. Automated filtering alone never approves a report. In this document, "approved" means approved for publication, not verified as fact.

Map counts use approved reports whose receipt times fall in the configured window. A report approved after that window may therefore be absent from the recent-volume count. Subscriber eligibility uses publication time rather than receipt time so delayed approval does not silently skip a report. Updates must show reporting times and avoid presenting old reports as new incidents. Any further notification age limit remains an explicit decision.

Deduplication prevents duplicate processing of the same submission or provider retry. Counts describe reports, not unique residents or independently verified incidents.

## 6. Geographic and map contract

Use a logical street identifier for subscriptions and a segment identifier for report assignment. Each segment belongs to a reviewed street grouping; do not join reports and subscriptions using street-name text alone.

The saved geometry includes OBJECTID, STREET_ID, and STREETNAME. STREET_ID varies among features named Water Street, so it must not be assumed to identify the entire subscription street. Validate source identifiers and build a reviewed whole-street mapping before integration. Avoid new neighbourhood or postal-code boundaries in this MVP.

| Approved reports received in the previous 60 minutes | Colour | Label |
| --- | --- | --- |
| 0 | Grey | No recent reports |
| 1-4 | Blue | Low report volume |
| 5-14 | Orange | Moderate report volume |
| 15 or more | Red | High report volume |

Legend: **Recent report volume**. These are proposed demonstration thresholds. Volume reflects participation as well as potential impact; it is not severity, safety, or an official incident rating. No recent reports does not mean no hazards exist.

## 7. Conceptual data requirements

This is a logical contract for planning, not an implemented database schema or a choice of database technology.

| Record | Required information |
| --- | --- |
| Street | Internal street identifier, display name, reviewed segment membership |
| Segment | Internal segment identifier, street identifier, source reference, geometry, display label |
| Report | Report/submission identifier, optional provider message identifier, private reporter reference, private raw text, redacted public description, received time, segment, hazard type, processing/review status, review time, private reviewer reference, publication time, separate verification status |
| Subscription | Identifier, street identifier, delivery channel, private phone number or email address, consent time, active status, successful-delivery tracking |
| Summary | Included report identifiers, scope, generation time, AI or standard-template label |
| Delivery | Subscription reference, included reports or cutoff, attempt time, outcome, failure information |

Hazard types start with flooding, blocked drain, snow obstruction, other, and unknown. Store timestamps in UTC and display pilot times using America/St_Johns. Preserve failed-delivery eligibility and avoid marking undelivered reports as delivered.

## 8. AI boundary

The required AI role is to summarize approved, redacted reports for a segment or subscribed street. Hazard classification and location suggestions are optional; explicit selection is preferable if automation threatens the time budget.

Provide report identifiers, public descriptions, locations, timestamps, verification statuses, and application-calculated counts. Keep phone numbers, email addresses, raw messages, and unnecessary personal information outside AI inputs. Treat report text as data, including any embedded instructions.

Summaries must distinguish hazards and preserve uncertainty. They must not invent causes, locations, severity, municipal action, or confirmed incidents. Retain included report identifiers so output can be reviewed against its inputs. Use a deterministic standard summary if AI fails and label it accordingly. Report intake and map counts must continue working.

## 9. Feasibility checks and implementation boundaries

Time-box the initial checks to approximately 20-30 minutes. Record evidence and owners; do not invent provider access, credits, free allowances, or completed integrations.

| Check | Evidence needed | Outcome if unsuccessful |
| --- | --- | --- |
| Free outbound SMS | A message delivered to a chosen authorized real phone number; verified cost, Canadian delivery, recipient restrictions, setup, and trial limits | Use email; verify actual email delivery separately |
| Report intake | Prove inbound SMS separately if proposed | Confirm another intake channel, such as app-based entry |
| Street/segment mapping | Reviewed segment identifiers and complete membership for pilot streets | Use a small manually reviewed pilot mapping |
| Staff publication gate | Pending report stays private; explicit approval permits public output | Resolve before claiming the core flow works |
| Map update | One approved stored report changes only the assigned segment | Explicit refresh is acceptable for the demo |
| AI summary | Several synthetic reports yield an accurate, traceable summary | Deterministic standard summary |
| Subscription delivery | Relevant approved reports arrive at an authorized destination | Diagnose actual delivery; labelled simulation is a demo limitation, not completion evidence |
| Scheduling | Hosting supports hourly execution or a manual trigger runs the same workflow | Labelled manual demo trigger |

Reuse the current frontend and project conventions. Select the simplest suitable persistence and backend approach after inspection. Provider, database, staff-access mechanism, AI service, scheduler, and hosting choices remain open. New dependencies, schema changes, permissions, infrastructure, deployment, and external data transfers require their applicable approvals.

## 10. Proposed eight-hour execution sequence

| Time | Work | Completion evidence |
| --- | --- | --- |
| 0:00-0:30 | Verify messaging options, intake path, geography, and scope | Chosen paths with evidence and explicit limitations |
| 0:30-1:30 | Persistence and report lifecycle | Synthetic report stored once against a valid segment |
| 1:30-3:00 | Intake and minimal staff review | Pending/rejected reports remain private; approved report becomes eligible |
| 3:00-4:15 | Segment counts, map colours, and details | Correct segment updates and age-out works |
| 4:15-5:15 | Grounded summaries and fallback | Supported summary and working AI-failure fallback |
| 5:15-6:15 | Consent, street subscriptions, delivery, unsubscribe | Relevant real update delivered through selected channel |
| 6:15-7:15 | End-to-end and failure checks | Core journey and publication boundaries verified |
| 7:15-8:00 | Repeatable demo and documentation | Setup, limitations, and demonstration steps recorded |

This schedule is a proposal, not a commitment or completion record. Assign owners from actual team availability. Protect the full reporting-to-review-to-map-to-update journey before adding analytics.

## 11. Acceptance and verification

- The same submission/provider retry persists once and does not inflate counts.
- Pending, rejected, and unresolved reports never appear in public counts, summaries, or updates.
- Explicit staff approval publishes only the intended resolved report and does not automatically verify its hazard.
- The first, fifth, and fifteenth recent approved reports produce blue, orange, and red respectively under the proposed thresholds.
- Reports aging out reduce counts and can change colours.
- Segment details show hazard information, timestamps, verification status, and reporting window.
- A subscription includes other mapped segments of the same street and excludes unrelated streets.
- A delayed approval is not lost behind a previous notification cutoff.
- No new eligible reports means no scheduled message.
- Failed delivery does not advance successful-delivery tracking; unsubscribe prevents future delivery attempts.
- AI output contains only supported information and distinguishes different hazards; AI failure produces a labelled standard summary.
- Public responses and AI inputs exclude private contact information and raw messages.
- Real delivery is demonstrated through the selected SMS or email channel; manual triggers and simulations are labelled accurately.

These are required checks, not claims that tests have run or features are complete.

## 12. Privacy, trust, and accessibility

Use synthetic reports and authorized test destinations for demonstrations. Keep CanAI artifacts private; do not send protected material to external services without specific authorization. Define retention and deletion before collecting real public reports. Keep secrets outside source control.

Obtain explicit subscription consent, provide unsubscribe, and suppress delivery after unsubscribe is processed. Restrict raw submissions, contact information, and staff controls. Public summaries use redacted approved descriptions only.

Show unverified labels, report times, data sources, the reporting window, and the latest update. Distinguish empty results from stale data or loading failure. Provide keyboard access, readable contrast, and text alternatives to map information. Target WCAG 2.2 AA without claiming compliance before evaluation.

## 13. Existing implementation and documentation

Inspected repository evidence establishes a Streamlit/Folium map, saved pilot geometries, street search, multi-street selection, and recorded snow-clearing priority details. The old map colours represent snow-clearing priority. Individual segment selection, reporting, staff review, notification subscriptions, AI summaries, and delivery have not been established as implemented for the pivot.

Reuse suitable code in app.py, components/map_tab.py, services/street_data.py, and the saved data rather than replacing the frontend to match an earlier planning proposal. Verify identifiers and interactions before relying on them.

README.md, documents/DESIGN.md, and documents/IMPLEMENTATION_PLAN.md still describe the previous scope. Where they conflict, this context governs the product direction. They need reconciliation before pivot implementation. Update setup, environment-variable names, provider restrictions, fallback behaviour, and validation evidence as implementation becomes established.

## 14. Exclusions and remaining decisions

Outside the MVP: snowfall simulation, plow workloads or routing, fleet allocation, automated dispatch, hazard prediction, validated severity scores, new geographic boundaries, city-wide rollout, production municipal integration, and claims of operational readiness. A full moderation system and production identity management are deferred; minimal staff approval and an appropriate access boundary remain required.

Remaining decisions are the report-intake channel; SMS/email provider and verified restrictions; pilot street/segment mapping; staff access approach; persistence and hosting; AI service; final reporting window, thresholds, and interval; and any notification age limit. The product direction and staff-publication gate are settled.

Later possibilities include expanded moderation and incident confirmation, hazard filters, additional subscription areas, bilingual interfaces, and participation analytics kept separate from impact or safety claims.

## Previous direction - deprecated October 29, 2026

The previous direction was SnowStorm AI (application title: Flurry), a snowstorm planning and preparedness tool for St. John's. Its map-only phase focused on real pilot roads, searchable multi-street selection, recorded municipal snow-clearing priorities, and explicit unknown-data states. A later phase proposed snowfall-scenario comparisons, plow-workload simulation, and an AI preparedness brief; those simulation capabilities were not established as implemented.

That direction was deprecated on October 29, 2026 in favour of community crisis reporting, staff-reviewed publication, and street notifications. Reuse useful map code and geometry where practical. Snowfall simulation, plow estimates, routing, and preparedness recommendations are outside the confirmed MVP. Earlier context remains available in Git history.
