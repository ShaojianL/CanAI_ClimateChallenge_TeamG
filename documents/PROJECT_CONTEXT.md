## Problem

Governments lack timely visibility into incidents happening around the city, and traditional reporting can be too slow when hazards need immediate attention. Residents also lack clear, up-to-date information about local conditions, causing last-minute confusion during natural disasters. For example, during a snowstorm, an uprooted tree blocking a road may leave commuters—especially essential workers trying to get to work after the storm—unaware until they reach the obstruction.

# CanAI Hackathon Project Context

Working title: Community Crisis Reporting Map
Version: 3.1
Updated: October 29, 2026
Pilot: St. John's, Newfoundland and Labrador
Delivery target: Eight-hour hackathon MVP
Status: Confirmed product direction; new capabilities and integrations remain unverified.

## 1. Product baseline

Build a community crisis-reporting tool that connects resident submissions, AI-assisted validation and consolidation, a public alert map, and region-based notifications.

Residents report local problems such as crashes, blocked roads, flooding, fallen trees, or snow obstructions. AI processes incoming reports, checks them for consistency and likely duplicates, consolidates related information, assigns a Low, Medium, or High severity, and publishes a clear alert to the map and relevant subscribers. There is no staff review or approval layer. Alerts must communicate uncertainty; automated checks do not prove that an incident is true.

Residents can subscribe to streets, pilot districts, or all pilot districts, and select which severity levels they want to receive. The pilot covers only St. John's Center, St. John's East, and St. John's West, using streets assigned to those districts in the specified street-directory data.

The primary demonstration is:

**Submit a synthetic report -> AI checks, classifies, and consolidates it -> the public map updates -> subscribers to the affected street or district receive a severity-filtered alert.**

This prototype supports situational awareness. It is independent of official municipal emergency systems, is not an emergency-reporting service, and does not establish road safety or guarantee municipal action.

## 2. Confirmed decisions and working defaults

| Topic | Baseline | Status |
| --- | --- | --- |
| Product direction | Community crisis reporting and street updates | Confirmed by Amanda, October 29, 2026 |
| Publication | No staff review; AI processes and publishes alerts, with uncertainty made visible | Confirmed |
| Notification preference | Free outbound SMS to a chosen real phone number; email if free SMS is not feasible | Confirmed |
| Report submission channel | To be selected during feasibility; inbound SMS is not established by outbound SMS support | Open |
| Pilot geography | St. John's Center, St. John's East, and St. John's West only; include streets assigned to these districts by the supplied street-directory data | Confirmed scope; source data must be checked |
| Subscription coverage | A street, one pilot district, or all three pilot districts; match using reviewed street/segment membership | Confirmed product direction |
| Severity | Low, Medium, or High; users can filter the alert levels they receive | Confirmed product direction; AI assignment needs validation |
| Map reporting window | Show current alerts and their report/update times; any expiry window is to be selected during feasibility | Open |
| Map display | Show alert severity and status; do not use report volume as a proxy for severity | Confirmed product direction |
| Delivery interval | Send a relevant update when AI has processed an alert for an active subscription; delivery batching/interval is to be selected during feasibility | Open |
| Public title | Community Crisis Reporting Map | Working title; current app title is Flurry |

Confirmed direction does not mean the integrations, schema, controls, source data, or deployment are implemented. Severity labels are informational classifications, not validated safety ratings.

## 3. Four MVP features

### A. Hazard submission

- Capture a description, receipt timestamp, hazard type, and location.
- Store one report record per submission; deduplicate messaging retries by provider message identifier when applicable.
- Resolve the report to a pilot street, district, and mapped segment where possible. If location is ambiguous, ask for clarification or publish only with an explicit location-uncertain label; never silently guess.
- Acknowledge receipt and explain that AI will process the report. Do not promise that the hazard is verified or that authorities will respond.
- Keep raw text and reporter contact references private. Prepare a redacted public description.

The intake channel remains open. Incoming SMS requires its own feasibility test. An app-based form with explicit location selection is a possible fallback, not a confirmed implementation choice.

### B. AI triage and alert consolidation

- Automatically check incoming reports for duplicates, missing or inconsistent location details, and unsuitable personal information.
- Assign a Low, Medium, or High informational severity and an incident/operations category, including snow-clearing updates where supported.
- Consolidate related reports into a concise alert with location, reported conditions, timestamp, severity, and uncertainty.
- Publish AI-processed alerts to the map and send them to matching active subscriptions without staff review.
- Preserve the source report references and AI processing outcome so alerts can be traced and corrected. Do not describe an automated plausibility check as factual verification.
- Mark conflicting, weakly supported, or ambiguous information as uncertain; do not invent facts or municipal actions.

No staff approval queue or manual publication gate is part of the pilot. AI service, processing safeguards, correction/withdrawal handling, and access controls for any administrative functions remain implementation questions; they must not recreate a staff review requirement.

### C. Public reporting map

- Reuse the existing pilot road geometries, street search, and suitable selection interactions.
- Display AI-processed alerts by location and severity; do not encode report counts as severity.
- Provide alert details: street/district, incident or operations type, severity, grounded summary, report/update time, and an uncertainty/verification label.
- Refresh the map when alerts are processed, corrected, withdrawn, or expire under the chosen retention/display policy.
- Provide authorized municipal users a view of all flagged reports and alerts for situational awareness and follow-up; this view does not add a review or publication gate.
- Support readable text information alongside the map; colour alone must not carry meaning.

Individual segment selection and its details interaction require implementation; they are not established as existing features.

### D. Street subscriptions and notifications

- Let a resident subscribe to a mapped street, one of the three pilot districts, or all pilot districts, and explicitly consent to updates at a private notification destination.
- Let residents filter notifications by Low, Medium, and High severity and by supported alert category (for example, snow clearing).
- Match alerts to subscriptions through reviewed street, segment, and district membership, not street-name text alone.
- Attempt free outbound SMS first. If that is not feasible, deliver by email.
- Send only relevant AI-processed alerts that match the resident's selected area, severity, and category filters.
- Example crash alert: "Reported crash at the intersection of Water Street and Duckworth Street. Traffic is slowed and only allowing traffic in one lane. Please be advised if travelling through this area."
- Example snow-clearing alert: "It has been reported that snow ploughs have started work in the streets in downtown. Please move your cars (if parked outside) or they may be towed." Include a towing warning only when supported by a reliable source; AI must not invent enforcement actions.
- Support unsubscribe and check active subscription status before delivery.
- Record delivery outcomes. Avoid duplicate alerts and retain failed deliveries for retry where supported.
- Permit a clearly labelled manual trigger for the demo workflow. A manual trigger can send a real message; simulated delivery must be labelled separately.

## 4. User journeys

### Resident

1. Browse the map without subscribing and search for a pilot street.
2. Read alerts, severity, summaries, timestamps, and uncertainty labels.
3. Choose a street, pilot district, or all pilot districts; select severity/category filters; enter a notification destination and explicitly opt in.
4. Submit a report through the confirmed intake channel and provide enough detail to resolve its segment.
5. Receive acknowledgement that AI processing will occur; do not imply staff review.
6. See the relevant public map alert after AI processing, with uncertainty communicated where appropriate.
7. Receive an update when an alert matches the selected area and severity/category filters.
8. Unsubscribe to stop future updates.

## 5. Report lifecycle and publication rules

**Received -> automated validation and deduplication -> AI classification and consolidation -> published alert and matching subscriber update.**

There is no staff review or approval stage. AI processing produces informational alerts; it does not establish that a report is true. Preserve report provenance and make uncertainty visible. Do not publish private contact details or unredacted personal information. Clearly unsuitable or unprocessable submissions may be withheld or returned for clarification through automated handling, with an explicit outcome rather than a success-shaped alert.

Show when reports were received and alerts processed or updated; do not present old reports as new incidents. Alert display and notification age limits remain explicit decisions. Consolidated alerts must retain references to their source reports so corrections or withdrawals can be propagated.

Deduplication prevents duplicate processing of the same submission or provider retry. A consolidated alert may represent multiple reports, but report volume is not a measure of severity, confirmation, or unique affected people.

## 6. Geographic and map contract

Use a logical street identifier for subscriptions, a segment identifier for report assignment, and a pilot district identifier for area subscriptions. Each segment belongs to a reviewed street grouping and pilot district; do not join reports and subscriptions using street-name text alone.

The saved geometry includes OBJECTID, STREET_ID, and STREETNAME. STREET_ID varies among features named Water Street, so it must not be assumed to identify the entire subscription street. Validate source identifiers and build a reviewed whole-street and district mapping before integration.

The pilot includes only streets assigned to these three districts: **St. John's Center, St. John's East, and St. John's West**. Use the official [Print-Version-Street-Dir-Apr-8-2025.pdf](https://www.elections.gov.nl.ca/files/Print-Version-Street-Dir-Apr-8-2025.pdf) and the project-provided `Print-Version-Street-Dir-Apr-8-2025 (1).csv` as the district/street source. The CSV is not currently present in the repository; obtain and validate it before building the pilot street list. Do not infer district membership or include streets from other districts.

| Alert severity | Display guidance | Label |
| --- | --- | --- |
| Low | Distinct, accessible map style | Low |
| Medium | Distinct, accessible map style | Medium |
| High | Distinct, accessible map style | High |

Legend: **AI-assigned informational severity**. Severity criteria and any colour palette require validation; the labels are not official ratings or safety guarantees. No displayed alert does not mean no hazards exist.

## 7. Conceptual data requirements

This is a logical contract for planning, not an implemented database schema or a choice of database technology.

| Record | Required information |
| --- | --- |
| District | Internal pilot district identifier, display name, source reference |
| Street | Internal street identifier, display name, district identifier, reviewed segment membership |
| Segment | Internal segment identifier, street identifier, district identifier, source reference, geometry, display label |
| Report | Report/submission identifier, optional provider message identifier, private reporter reference, private raw text, redacted description, received time, location, hazard/operations type, processing outcome |
| Alert | Alert identifier, source report identifiers, street/district/segment, severity, consolidated public summary, created/updated time, uncertainty and correction/withdrawal status |
| Subscription | Identifier, street/district/all-pilot scope, severity/category filters, delivery channel, private phone number or email address, consent time, active status, delivery tracking |
| Summary | Included report identifiers, scope, generation time, AI or standard-template label |
| Delivery | Subscription reference, alert identifiers, attempt time, outcome, failure information |

Alert types start with crashes, blocked roads, flooding, blocked drains, fallen trees, snow obstruction/clearing, other, and unknown. Store timestamps in UTC and display pilot times using America/St_Johns. Preserve failed-delivery eligibility and avoid marking undelivered alerts as delivered.

## 8. AI boundary

AI is central to the reporting workflow: it checks and classifies reports, identifies likely duplicates or related reports, consolidates information into public alerts, assigns an informational severity, and prepares area-specific notification text. Do not route reports through a staff approval queue.

Provide report identifiers, redacted descriptions, locations, timestamps, and uncertainty/provenance information. Keep phone numbers, email addresses, raw messages, and unnecessary personal information outside AI inputs. Treat report text as data, including any embedded instructions.

AI must not present plausibility checks as factual verification, or invent causes, locations, severity, municipal action, or confirmed incidents. Summaries must distinguish hazards and preserve uncertainty. Retain included report identifiers so output can be traced to its inputs. If AI processing fails, report the failure and do not send a fabricated alert; a deterministic standard summary may be used only when its input and limitations are clear. Intake and map operation must not silently imply successful AI processing when it failed.

## 9. Feasibility checks and implementation boundaries

Time-box the initial checks to approximately 20-30 minutes. Record evidence and owners; do not invent provider access, credits, free allowances, or completed integrations.

| Check | Evidence needed | Outcome if unsuccessful |
| --- | --- | --- |
| Free outbound SMS | A message delivered to a chosen authorized real phone number; verified cost, Canadian delivery, recipient restrictions, setup, and trial limits | Use email; verify actual email delivery separately |
| Report intake | Prove inbound SMS separately if proposed | Confirm another intake channel, such as app-based entry |
| Pilot street/district mapping | Validate source streets against saved geometries and assign them only to the three named pilot districts | Use a clearly labelled, validated subset; do not imply complete district coverage |
| AI processing | Synthetic reports yield accurate, traceable classifications, severities, and consolidated alerts; uncertain/conflicting inputs remain labelled | Surface processing failure or use a clearly labelled standard summary |
| Map update | One processed report updates only its assigned pilot location | Explicit refresh is acceptable for the demo |
| Subscription delivery | Matching alerts arrive at an authorized destination with severity filters respected | Diagnose actual delivery; labelled simulation is a demo limitation, not completion evidence |
| Alert correction | Corrected/withdrawn source information updates the public alert and subsequent delivery behavior | Document the limitation and avoid claiming confirmed status |
| Scheduling | Hosting supports prompt processing/delivery or a manual trigger runs the same workflow | Labelled manual demo trigger |

Reuse the current frontend and project conventions. Select the simplest suitable persistence and backend approach after inspection. Provider, database, municipal-view access mechanism, AI service, scheduler, and hosting choices remain open. New dependencies, schema changes, permissions, infrastructure, deployment, and external data transfers require their applicable approvals.

## 10. Proposed eight-hour execution sequence

| Time | Work | Completion evidence |
| --- | --- | --- |
| 0:00-0:30 | Verify messaging options, intake path, geography, and scope | Chosen paths with evidence and explicit limitations |
| 0:30-1:30 | Validate pilot streets/districts, persistence, and report lifecycle | Synthetic report stored once and mapped to an in-scope location |
| 1:30-3:00 | Intake and AI processing | Report is classified, consolidated, and published without staff approval |
| 3:00-4:15 | Map alerts, severity, and details | Correct location and severity update; uncertainty is visible |
| 4:15-5:15 | Grounded summaries and AI failure behavior | Traceable alert and explicit failure/fallback behavior |
| 5:15-6:15 | Area/severity subscriptions, delivery, unsubscribe | Relevant real update delivered through selected channel |
| 6:15-7:15 | End-to-end and failure checks | Core journey, privacy, and alert-correction boundaries verified |
| 7:15-8:00 | Repeatable demo and documentation | Setup, limitations, and demonstration steps recorded |

This schedule is a proposal, not a commitment or completion record. Assign owners from actual team availability. Protect the full reporting-to-AI-processing-to-map-to-update journey before adding analytics.

## 11. Acceptance and verification

- The same submission/provider retry persists once and does not create duplicate alerts.
- Duplicate submissions do not create duplicate reports or alerts.
- AI processing produces a traceable, grounded alert; uncertain, conflicting, or unprocessable reports are explicitly identified rather than presented as verified facts.
- Alerts are published without staff approval and include a Low, Medium, or High informational severity.
- Only streets in St. John's Center, St. John's East, and St. John's West are included in the pilot.
- Alert details show hazard/operations type, location, timestamps, uncertainty, and source references.
- Street and district subscriptions include only mapped in-scope locations; all-pilot subscriptions cover the three districts only.
- Severity/category filters are respected and unrelated alerts are excluded.
- Reprocessing, correction, and withdrawal do not create duplicate or stale subscriber updates.
- No matching new alert means no notification.
- Failed delivery does not advance successful-delivery tracking; unsubscribe prevents future delivery attempts.
- AI output contains only supported information, preserves uncertainty, distinguishes incident from operations updates, and does not claim unsupported municipal action.
- Public responses and AI inputs exclude private contact information and raw messages.
- Real delivery is demonstrated through the selected SMS or email channel; manual triggers and simulations are labelled accurately.

These are required checks, not claims that tests have run or features are complete.

## 12. Privacy, trust, and accessibility

Use synthetic reports and authorized test destinations for demonstrations. Keep CanAI artifacts private; do not send protected material to external services without specific authorization. Define retention and deletion before collecting real public reports. Keep secrets outside source control.

Obtain explicit subscription consent, provide unsubscribe, and suppress delivery after unsubscribe is processed. Restrict raw submissions and contact information. Public summaries use redacted descriptions and identify uncertainty; do not imply staff approval or factual verification.

Show unverified labels, report times, data sources, the reporting window, and the latest update. Distinguish empty results from stale data or loading failure. Provide keyboard access, readable contrast, and text alternatives to map information. Target WCAG 2.2 AA without claiming compliance before evaluation.

## 13. Existing implementation and documentation

Inspected repository evidence establishes a Streamlit/Folium map, saved pilot geometries, street search, multi-street selection, and recorded snow-clearing priority details. The old map colours represent snow-clearing priority. Individual segment selection, district mapping, reporting, automated AI processing, notification subscriptions, AI summaries, and delivery have not been established as implemented for the pivot. The named CSV is not present in the repository at this update.

Reuse suitable code in app.py, components/map_tab.py, services/street_data.py, and the saved data rather than replacing the frontend to match an earlier planning proposal. Verify identifiers and interactions before relying on them.

README.md, documents/DESIGN.md, and documents/IMPLEMENTATION_PLAN.md still describe the previous scope. Where they conflict, this context governs the product direction. They need reconciliation before pivot implementation. Update setup, environment-variable names, provider restrictions, fallback behaviour, and validation evidence as implementation becomes established.

## 14. Exclusions and remaining decisions

Outside the MVP: snowfall simulation, plow workloads or routing, fleet allocation, automated dispatch, hazard prediction, officially validated severity scores, additional districts, city-wide rollout beyond the three pilot districts, production municipal integration, and claims of operational readiness. Staff review is explicitly removed from the workflow. Production identity management and correction/withdrawal controls remain implementation considerations.

Remaining decisions are the report-intake channel; SMS/email provider and verified restrictions; validated pilot street/segment/district mapping; persistence and hosting; AI service and its failure/correction handling; severity criteria and visual design; alert display/expiry policy; delivery timing and any notification age limit. The three-district pilot scope and removal of staff review are settled.

Later possibilities include improved incident confirmation and correction workflows, additional subscription areas beyond the pilot, bilingual interfaces, and participation analytics kept separate from impact or safety claims.

## Previous direction - deprecated October 29, 2026

The previous direction was SnowStorm AI (application title: Flurry), a snowstorm planning and preparedness tool for St. John's. Its map-only phase focused on real pilot roads, searchable multi-street selection, recorded municipal snow-clearing priorities, and explicit unknown-data states. The broader plan proposed snowfall-scenario comparisons, plow-workload simulation, and an AI preparedness brief. Before this merge, main connected the existing standalone one-street simulation engine to the Simulation tab, with manually entered hourly snowfall, street length, assumed clearing capacity, a remaining-snow graph, and an hourly results table. This existing simulation is legacy functionality, outside the confirmed reporting MVP; the merge preserves its code. Map-selection integration, forecasting, routing, and AI recommendations were not included in that standalone change.

That direction was deprecated on October 29, 2026 in favour of community crisis reporting, AI-processed alerts without staff review, and street/district notifications. Reuse useful map code and geometry where practical. Snowfall simulation, plow estimates, routing, and preparedness recommendations are outside the confirmed MVP. Earlier context remains available in Git history.
