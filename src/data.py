from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "sample_api_logs.csv"

def load_logs(path=DEFAULT_CSV):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)

def clean_logs(df):
    """Clean required fields and derive the failure target from HTTP status."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    required = ["timestamp","request_id","endpoint","http_method","status_code","response_time_ms",
                "request_size_bytes","response_size_bytes","client_id","environment","error_message"]
    for col in required:
        if col not in out.columns:
            out[col] = "" if col in ["timestamp","request_id","endpoint","http_method","client_id","environment","error_message"] else np.nan
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    for col in ["status_code","response_time_ms","request_size_bytes","response_size_bytes"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in ["request_id","endpoint","http_method","client_id","environment","error_message"]:
        out[col] = out[col].fillna("").astype(str).str.strip()
    out = out.dropna(subset=["timestamp","status_code","response_time_ms"])
    out = out[out["status_code"].between(100,599) & (out["response_time_ms"] >= 0)]
    out["status_code"] = out["status_code"].astype(int)
    out = out[(out["request_id"] != "") & (out["endpoint"] != "")]
    out = out.drop_duplicates(subset=["request_id"], keep="first")
    out["http_method"] = out["http_method"].str.upper()
    for col in ["request_size_bytes","response_size_bytes"]:
        out[col] = out[col].fillna(0).clip(lower=0).astype(int)
    out["is_failure"] = (out["status_code"] >= 400).astype(int)
    return out.reset_index(drop=True)
