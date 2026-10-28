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

The app starts from local `data/` files. Use **Fetch / refresh data** in the sidebar
to retrieve the eight pilot streets from the City's public geometry and priority
sources for the current session. Requests may take several minutes. Successful
responses are validated before replacing the session dataset; failures keep the
current dataset. Missing priorities remain explicitly unavailable. Saved files are
unchanged, and valid street selections are preserved.

Rerun the fetch script separately to update the saved startup dataset. Refreshing
does not add streets outside the configured pilot set or provide live road conditions.

### Map Explorer presentation

The theme in `.streamlit/config.toml` follows the colours and typography in
`DESIGN.md`. Noto Sans is used when installed, with Arial and sans-serif fallbacks;
no external font download is configured. Map and street details appear side by
side on wider screens and stack on narrow screens using Streamlit's native layout.

Selected streets show recorded priority-source links and explicit unavailable
labels for missing attributes. Verification dates are not recorded in the current
dataset. The source and limitations panel explains pilot coverage, mixed priorities,
and the distinction between clearing priorities and current road conditions.

