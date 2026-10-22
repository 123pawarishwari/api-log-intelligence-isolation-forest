import pandas as pd

def kpis(df):
    total = len(df)
    failures = int(df["is_failure"].sum()) if total else 0
    return {
        "total_requests": total,
        "failed_requests": failures,
        "successful_requests": total - failures,
        "error_rate_pct": round(100 * failures / total, 2) if total else 0.0,
        "avg_latency_ms": round(float(df["response_time_ms"].mean()), 2) if total else 0.0,
        "p95_latency_ms": round(float(df["response_time_ms"].quantile(.95)), 2) if total else 0.0
    }

def endpoint_report(df):
    if df.empty:
        return pd.DataFrame()
    result = df.groupby("endpoint").agg(
        requests=("request_id","count"),
        failures=("is_failure","sum"),
        avg_latency_ms=("response_time_ms","mean"),
        p95_latency_ms=("response_time_ms", lambda s: s.quantile(.95))
    ).reset_index()
    result["error_rate_pct"] = (100*result["failures"]/result["requests"]).round(2)
    return result.round({"avg_latency_ms":2,"p95_latency_ms":2}).sort_values(["failures","avg_latency_ms"], ascending=False)

def status_report(df):
    return df.groupby("status_code").size().rename("request_count").reset_index().sort_values("request_count",ascending=False)

def daily_trends(df):
    x=df.copy()
    x["day"]=pd.to_datetime(x["timestamp"]).dt.date
    return x.groupby("day").agg(requests=("request_id","count"),failures=("is_failure","sum"),
                                avg_latency_ms=("response_time_ms","mean")).reset_index()
