<div align="center">

# CanAI 2026 Fall Hackathon

### Team G

**Adam** &nbsp; &middot; &nbsp; **Amanda** &nbsp; &middot; &nbsp; **Farhan** &nbsp; &middot; &nbsp; **Victoria** &nbsp; &middot; &nbsp; **Wilson**

</div>

## SnowStorm AI — Map MVP

Interactive map of pilot St. John's streets with officially verified snow-clearing priorities. See [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) for scope.

### Quickstart

```bash
python3 -m venv .venv                      # once
.venv/bin/pip install -r requirements.txt  # once
.venv/bin/streamlit run app.py             # open http://localhost:8501
```

### Project layout

- `app.py` — single-page Streamlit app (map, street search/selection, legend, details)
- `scripts/fetch_pilot_streets.py` — one-time data prep: road geometry from the City's public ArcGIS layer + priorities verified via the City's [street priority lookup](https://apps.stjohns.ca/snowclearing/StreetPriority.aspx)
- `data/pilot_streets.geojson` — prepared road segments (WGS84)
- `data/street_priorities.json` — verified priorities per pilot street, incl. section-level detail

The app reads only the local `data/` files; rerun the fetch script to refresh or add pilot streets.

