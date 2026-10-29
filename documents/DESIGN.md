# St. John's Snow Planning Simulator
Version: 2.0
Project Type: Hackathon MVP
Audience: AI Coding Tools (Cursor, Windsurf, Lovable, Bolt, Claude Code)
Design System: Government of Canada
Accessibility Target: WCAG 2.2 AA

## Product Summary

A planning-first simulation tool that allows municipal planners to explore a pilot road network, compare snowfall scenarios, simulate snow-clearing workload, and generate an AI-prepared planning brief.

### Core Principles
- Planning, not prediction
- Transparent assumptions
- Source transparency
- Graceful degradation
- Accessible by default

## Information Architecture

### Main Navigation
1. Map Explorer
2. Scenario Builder
3. Preparedness Brief

## Page 1: Map Explorer

Purpose:
- Explore pilot streets
- Review priority information
- Inspect provenance and data quality

Features:
- Search streets
- Multi-select streets
- Interactive map
- Priority legend
- Street details panel
- Missing data states

## Page 2: Scenario Builder & Simulator

Purpose:
- Compare two snowfall scenarios using identical operational assumptions.

Inputs:
- Total snowfall
- Storm duration
- Start time
- Hourly snowfall profile
- Available plows
- Operating hours
- Productivity assumptions
- Clearing target

Outputs:
- Peak snow
- Time to clear
- Plow-hours
- Remaining snow
- Comparison visualizations

## Page 3: Preparedness Brief

Generated sections:
- Key Findings
- Assumptions
- Uncertainties
- Pressure Points
- Further Considerations
- Disclaimer

## Government of Canada Visual Style

### Design Attributes
- Calm
- Professional
- Evidence-based
- Accessible
- Transparent

### Colours
Primary Navy: #26374A
Action Blue: #2847A1
Success: #278400
Warning: #FFAA00
Error: #D3080C
Background: #F8F8F8
Surface: #FFFFFF
Border: #D4D4D4

### Typography
Font: Noto Sans
Fallback: Arial, sans-serif

Display: 36px / 700
Page Title: 32px / 700
Section Heading: 24px / 700
Body: 16px / 400

### Accessibility
- WCAG 2.2 AA
- Keyboard navigation
- Visible focus indicators
- Screen reader support
- 4.5:1 color contrast minimum
- Responsive layouts
- No information conveyed by colour alone

### Responsive Behaviour
Desktop: Three-column simulator
Tablet: Two-column layout
Mobile: Single-column layout

### Tone of Voice
Explore assumptions.
Compare impacts.
Support planning discussions.

Never imply forecasts, certainty, or operational recommendations.
