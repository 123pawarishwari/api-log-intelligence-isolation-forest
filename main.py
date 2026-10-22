import json
from src.data import load_logs, clean_logs, ROOT
from src.analysis import kpis, endpoint_report, status_report, daily_trends
from src.anomaly_detection import detect_anomalies
from src.sql_store import write_sqlite, query_sql

def main():
    raw=load_logs()
    logs=clean_logs(raw)
    tagged, model=detect_anomalies(logs)
    reports=ROOT/"reports"
    reports.mkdir(exist_ok=True)
    (reports/"summary.json").write_text(json.dumps(kpis(logs),indent=2),encoding="utf-8")
    endpoint_report(logs).to_csv(reports/"endpoint_report.csv",index=False)
    status_report(logs).to_csv(reports/"status_report.csv",index=False)
    daily_trends(logs).to_csv(reports/"daily_trends.csv",index=False)
    tagged[tagged["anomaly_flag"]==-1].to_csv(reports/"detected_anomalies.csv",index=False)
    db=write_sqlite(logs,reports/"api_logs.sqlite")
    slow=query_sql(db,"SELECT endpoint, COUNT(*) AS slow_requests, ROUND(AVG(response_time_ms),2) AS avg_latency_ms FROM api_logs WHERE response_time_ms >= 1000 GROUP BY endpoint ORDER BY slow_requests DESC")
    slow.to_csv(reports/"slow_endpoints_sql.csv",index=False)
    print("Analysis complete.")
    print(json.dumps(kpis(logs),indent=2))
    print(f"Detected anomalies: {int((tagged['anomaly_flag']==-1).sum())}")
    print(f"Reports: {reports}")
    print("MongoDB is optional; set MONGODB_URI to enable MongoDB storage and aggregation.")

if __name__=="__main__":
    main()
