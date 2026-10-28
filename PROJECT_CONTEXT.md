# SnowStorm AI — Project Context

Last updated: 2026-10-28

## Project status and authority

Amanda selected SnowStorm AI as the CanAI Hackathon project.
The attached `SnowStorm_AI_8_Hour_MVP_Plan.docx` provides the baseline scope.
This file consolidates that plan for future project work.
Implementation, data extraction, and validation remain unverified.
Treat proposed implementation details below as planning choices until confirmed through implementation.

## Purpose

Build a winter storm simulation and preparedness planner for selected streets in St. John's, Newfoundland and Labrador.
Help public works and emergency-planning teams compare snowfall timing, street priorities, and assumed snow-clearing resources.
The minimum viable product (MVP) targets an eight-hour proof of concept.

Illustrative comparison: one 200 cm storm on Friday versus two 100 cm storms on Thursday and Saturday.
Six plows illustrate an assumed resource setting.
These values are examples, not observations or confirmed fleet availability.

## Core user flow

1. Select the pilot streets and review their sources.
2. Configure two hourly snowfall scenarios.
3. Enter assumed clearing resources, operating hours, productivity, and clearing target.
4. Run both simulations using clearly disclosed assumptions.
5. Compare hourly remaining snow, clearing progress, and plow-hours.
6. Review a preparedness brief grounded in the simulation results.

## MVP scope

| Feature | Required behavior | Output |
| --- | --- | --- |
| Storm scenario builder | Accept user-defined snowfall totals, timing, and hourly profiles. | Two editable scenarios. |
| Plow workload simulator | Allocate available plow-hours in street priority order. | Hourly remaining snow, work used, and clearing progress. |
| AI preparedness brief | Interpret structured results and disclose assumptions. | A traceable comparison and preparedness suggestions. |

Use 5–10 verified streets for the pilot.
A map is optional when geometry preparation threatens the time budget.
The app must support scenario changes without code edits.

## Non-negotiable interpretation rules

- Label every model estimate `SIMULATED`.
- Label every user-defined operational parameter `ASSUMED`.
- Distinguish sourced street information from assumptions and synthetic examples.
- Never present simulated clearing time as actual municipal recovery time.
- Never infer verified accessibility, road safety, or actual equipment availability.
- Never fabricate missing observations, source values, or historical validation results.
- Treat all mockup values, road colours, and forecast curves as synthetic design placeholders.
- Keep assumptions and data provenance visible in the interface.

## Data contract

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

## Source inventory

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

## Simulation contract

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

### Decisions required before coding

- Select and verify the 5–10 pilot streets.
- Define productivity units and their relationship to road length and snow depth.
- Define the clearing target and network-level completion rule.
- Define operating schedules and treatment of partial plow-hours.
- Define ordering among streets with equal priority.
- Define the shared scenario timeline, timezone, and simulation end condition.
- Decide whether both scenarios share operational settings or expose differences explicitly.

The baseline plan does not fully specify these mechanics.
Document each choice before interpreting simulation outputs.

## AI brief contract

A large language model (LLM) drafts the preparedness brief from structured simulation results.
Provide both storm inputs, total plow-hours, hourly remaining snow, priority order, and documented assumptions.
The brief should explain workload differences, priority concentration, and influential resource assumptions.
Tie every numerical statement to a supplied result field.
Do not invent metrics or describe suggestions as official recommendations.

Use a fixed text template when the LLM API is unavailable.
Clearly label that fallback as non-AI output.
The simulation must remain usable without the LLM.

## Implementation stack

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

## Eight-hour delivery plan

| Elapsed time | Work | Deliverable |
| --- | --- | --- |
| 0:00–0:30 | Define pilot and simulation contract. | Inputs, clearing target, and assumptions. |
| 0:30–1:30 | Verify access and extract streets. | Small road dataset with provenance. |
| 1:30–2:15 | Verify priorities and prepare scenarios. | Complete road attributes and editable hourly profiles. |
| 2:15–4:45 | Implement accumulation and capacity-limited assignment. | Two scenarios running end to end. |
| 4:45–6:00 | Build controls and comparison charts. | Working local interface. |
| 6:00–7:00 | Add the preparedness brief. | Grounded LLM brief or labelled fallback. |
| 7:00–8:00 | Test and document. | Verified constraints and README. |

## Completion criteria

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

## Explicit exclusions

- Trained machine-learning models.
- Real-time dispatch or detailed vehicle routing.
- City-wide coverage.
- Validated hazard forecasts or road-safety classifications.
- Claims about real plow availability.
- Unverified historical road-recovery results.
- Drifting snow, compaction, melting, freezing rain, traffic, and equipment failure.

## Working conventions

Keep the eight-hour scope central when evaluating new features.
Resolve model definitions before expanding the interface.
Preserve the separation between simulation calculations and AI interpretation.
Update this file when scope, model contracts, source verification, or completion status changes.
Record implementation evidence before marking a feature complete.
Keep CanAI project discussions and artifacts private unless Amanda explicitly authorizes sharing.

## Immediate next steps

1. Confirm pilot streets and complete the simulation contract decisions.
2. Test road extraction and verify priorities.
3. Prepare the two hourly profiles and operational assumptions.
4. Implement and verify the simulation before adding AI interpretation.
