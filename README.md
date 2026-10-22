# API Log Intelligence & Failure Detection System

A Python portfolio project for analyzing API failures and latency, querying semi-structured logs, and flagging unusual behavior with Scikit-learn's Isolation Forest.

**Dataset:** The included 1,600 API log rows are synthetic demonstration data, not real production logs.

## Features
- Pandas-based log loading and cleaning.
- KPI reporting: request volume, failures, error rate, average and p95 latency.
- Endpoint/status-code aggregation and daily latency/failure trends.
- Isolation Forest anomaly detection for unusual latency and request patterns.
- Optional MongoDB storage, indexes, and aggregation pipeline.
- SQLite-backed structured reporting and SQL query examples.
- Streamlit dashboard with filters, tables, charts, and anomaly export.

## Stack
Python, Pandas, Scikit-learn, MongoDB/PyMongo (optional), SQLite, SQL, Streamlit.

## Quick start

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Start the dashboard:

```powershell
streamlit run app.py
```

Run tests:

```powershell
python -m pytest
```

## MongoDB (optional)
The CSV/SQLite project works without MongoDB. To enable MongoDB, set `MONGODB_URI` in your environment. The module creates indexes on `endpoint`, `status_code`, `timestamp`, and the compound `endpoint + timestamp` fields. It also provides an aggregation pipeline for request counts, failures, error rates, and average latency by endpoint. These functions are standalone helpers (`src/mongodb_store.py`) and are not called by `main.py` or the dashboard; import them to load the cleaned logs into a collection.

For example, in PowerShell for the current terminal session:

```powershell
$env:MONGODB_URI="your-mongodb-connection-string"
```

Never commit a real connection string or credentials to GitHub. `.env.example` is safe to publish.

## Outputs
`python main.py` creates:
- `reports/summary.json`
- `reports/endpoint_report.csv`
- `reports/status_report.csv`
- `reports/daily_trends.csv`
- `reports/detected_anomalies.csv`
- `reports/slow_endpoints_sql.csv`
- `reports/api_logs.sqlite`

## How Isolation Forest works here
The model uses response time, status code, request size, and response size to identify records that differ from the general pattern. It assigns `-1` to an anomaly and `1` to a normal observation. The number of flagged rows is driven by the `contamination` parameter (default 6%), so the model will always flag roughly that share of records. `status_code` is used as a numeric feature for simplicity. An anomaly is a review signal, not proof of a failure. Tune the contamination setting and validate against real, anonymized logs before using operationally.

## Project structure
```text
api-log-intelligence-isolation-forest/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── data/sample_api_logs.csv
├── src/
│   ├── data.py
│   ├── analysis.py
│   ├── anomaly_detection.py
│   ├── mongodb_store.py
│   └── sql_store.py
├── sql/schema_and_queries.sql
└── tests/test_data.py
```

## Limitations / next steps
- Dataset is synthetic; anomaly results are a demonstration, not production validation.
- Add alerting, time-window-specific anomaly scoring, and validation on real anonymized logs.
- For production MongoDB use, consider duplicate-safe writes, schema validation, access control, and monitoring.

## License
MIT. See [LICENSE](LICENSE).
