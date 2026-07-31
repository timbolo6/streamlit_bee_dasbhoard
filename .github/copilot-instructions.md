# Project Guidelines

## Overview

Streamlit multipage dashboard for beehive health monitoring, honey sales, and beekeeper event tracking. Deployed on Streamlit Community Cloud at `https://bee-health-monitoring.streamlit.app/`.

## Code Style

- **Procedural/functional** — no classes. All logic is top-level or in plain functions.
- `snake_case` for all names. Google-style docstrings where present.
- f-strings for formatting. pandas `.loc[]` accessor for assignments.
- German UI text in `honey_order.py`; English elsewhere.
- See [src/app/utils.py](src/app/utils.py) for the canonical utility function style.

## Architecture

```
streamlit_app.py          # Entry point, st.navigation() with top-positioned nav
src/app/
  bee_monitoring.py       # Sensor telemetry charts, Prophet forecasting, sidebar filters
  honey_order.py          # German-language honey order page with PayPal integration
  upload_events.py        # Upload beekeeper events + images to MongoDB
  honey_harvest.py        # Static honey harvest history log
  utils.py                # Shared helpers: MongoDB queries, data loading, forecasting
```

- Pages are registered via `st.Page("src/app/<file>.py")` in `streamlit_app.py` — **not** the legacy `pages/` folder convention.
- `sys.path.append` in `streamlit_app.py` enables `from app.utils import ...` across pages.
- Pre-trained Prophet models live in `src/data/models/prophet_model_{1,2}.pkl`, loaded via `joblib.load()`.

## Build and Test

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py
```

- **No test suite exists.** No pytest, no CI/CD.
- Requires `.streamlit/secrets.toml` with MongoDB connection string:
  ```toml
  [mongodb]
  uri = "mongodb+srv://..."
  ```

## Project Conventions

- **Caching**: Data-loading functions use `@st.cache_data(ttl=600)`. MongoDB client is **not** cached — a new `MongoClient` is created per function call.
- **Session state**: `st.session_state` is used in `bee_monitoring.py` for persisting filter selections (beehive, date range).
- **MongoDB pattern**: All DB access follows `MongoClient(st.secrets["mongodb"]["uri"], server_api=ServerApi('1'))` → `client["beehive_monitoring"]["<collection>"]`.
- **Collections**: `bee_sensor_telemetry`, `bee_sensor_telemetry_agg`, `bee_events`.
- **Beehive IDs** `"1"` and `"2"` are hardcoded in dropdowns and model filenames.
- **CSV data files**: `src/data/honey_stock.csv` (honey inventory), `src/data/events.csv`, `.streamlit/rapid_weight_changes_events.csv` (pre-computed).

## Known Issues

- [bee_monitoring.py line 118](src/app/bee_monitoring.py#L118): `aframe(...)` is a typo — should be `st.dataframe(...)`.
- Timezone mismatch: `start_date_input` localized to UTC vs `end_date_input` to `Europe/Berlin`.
- `unsafe_allow_html=True` used with dynamic HTML including JS event handlers — security concern.
- Two different honey stock CSVs exist with different schemas (`src/data/honey_stock.csv` vs `src/datahoney_stock.csv`).

## Integration Points

- **MongoDB Atlas**: Primary data store for sensor telemetry and beekeeper events. Connection string via Streamlit secrets.
- **PayPal**: Embedded HTML buttons in `honey_order.py` for honey purchases.
- **Prophet**: Offline-trained time-series models for weight forecasting, serialized as `.pkl`.
- **Plotly**: All interactive charts use `plotly.graph_objects`.
- **ipify API**: External IP fetched from `https://api64.ipify.org` (displayed in about section).
