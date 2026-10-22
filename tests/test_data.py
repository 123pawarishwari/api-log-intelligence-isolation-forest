import pandas as pd
from src.data import clean_logs
from src.anomaly_detection import detect_anomalies

def test_clean_logs_deduplicates_and_derives_failure():
    frame=pd.DataFrame([
        {"timestamp":"2026-01-01T00:00:00","request_id":"a","endpoint":"/api/x","http_method":"get","status_code":500,"response_time_ms":30},
        {"timestamp":"2026-01-01T00:01:00","request_id":"a","endpoint":"/api/x","http_method":"get","status_code":200,"response_time_ms":20},
    ])
    result=clean_logs(frame)
    assert len(result)==1
    assert result.iloc[0]["is_failure"]==1
    assert result.iloc[0]["http_method"]=="GET"

def test_isolation_forest_returns_labels():
    frame=pd.DataFrame({
        "response_time_ms":[100+i for i in range(40)],
        "status_code":[200]*39+[500],
        "request_size_bytes":[100]*40,
        "response_size_bytes":[500]*40,
    })
    frame["request_id"]=[str(i) for i in range(40)]
    result, model=detect_anomalies(frame)
    assert "anomaly_flag" in result.columns
    assert set(result["anomaly_flag"].unique()).issubset({-1,1})
