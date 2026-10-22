import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

FEATURES = ["response_time_ms", "status_code", "request_size_bytes", "response_size_bytes"]

def detect_anomalies(df, contamination=0.06):
    """Flag unusual requests using Isolation Forest; -1 means anomaly, 1 means normal."""
    if len(df) < 20:
        out=df.copy()
        out["anomaly_flag"] = 1
        out["anomaly_label"] = "Not enough data"
        return out, None
    out=df.copy()
    model=Pipeline([
        ("scale", StandardScaler()),
        ("isolation_forest", IsolationForest(
            n_estimators=150, contamination=contamination, random_state=42
        ))
    ])
    model.fit(out[FEATURES].fillna(0))
    predictions=model.predict(out[FEATURES].fillna(0))
    scores=model.decision_function(out[FEATURES].fillna(0))
    out["anomaly_flag"] = predictions
    out["anomaly_label"] = out["anomaly_flag"].map({-1:"Anomaly",1:"Normal"})
    out["anomaly_score"] = scores.round(5)
    return out, model
