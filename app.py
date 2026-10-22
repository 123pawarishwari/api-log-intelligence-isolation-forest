from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from src.data import load_logs, clean_logs
from src.analysis import kpis, endpoint_report, status_report, daily_trends
from src.anomaly_detection import detect_anomalies

st.set_page_config(page_title="API Log Intelligence",page_icon="📡",layout="wide")
st.title("API Log Intelligence & Failure Detection System")
st.caption("API failure, latency, and anomaly analysis. Included dataset is synthetic demonstration data.")

upload=st.sidebar.file_uploader("Upload API log CSV (optional)",type=["csv"])
try:
    logs=clean_logs(pd.read_csv(upload) if upload else load_logs())
except Exception as exc:
    st.error(f"Could not load logs: {exc}")
    st.stop()
if logs.empty:
    st.warning("No valid log records found.")
    st.stop()

st.sidebar.header("Filters")
eps=sorted(logs.endpoint.unique().tolist())
selected_eps=st.sidebar.multiselect("Endpoint",eps,default=eps)
statuses=sorted(logs.status_code.unique().tolist())
selected_status=st.sidebar.multiselect("Status code",statuses,default=statuses)
methods=sorted(logs.http_method.unique().tolist())
selected_methods=st.sidebar.multiselect("HTTP method",methods,default=methods)
data=logs[logs.endpoint.isin(selected_eps)&logs.status_code.isin(selected_status)&logs.http_method.isin(selected_methods)].copy()
if data.empty:
    st.info("No records match these filters.")
    st.stop()

metrics=kpis(data)
cards=st.columns(5)
for col,label,key,suffix in zip(cards,["Total Requests","Failed Requests","Success Requests","Error Rate","Avg Latency"],["total_requests","failed_requests","successful_requests","error_rate_pct","avg_latency_ms"],["","","","%"," ms"]):
    col.metric(label,f'{metrics[key]:,}{suffix}')

left,right=st.columns(2)
with left:
    st.subheader("HTTP Status Code Distribution")
    st.bar_chart(status_report(data).set_index("status_code")["request_count"])
with right:
    st.subheader("Endpoint Error Rate (%)")
    ep=endpoint_report(data).set_index("endpoint")
    st.bar_chart(ep["error_rate_pct"])

st.subheader("Latency and Failure Trends")
trends=daily_trends(data).set_index("day")
st.line_chart(trends[["requests","failures"]])
st.line_chart(trends[["avg_latency_ms"]])

st.subheader("Endpoint Performance Report")
st.dataframe(endpoint_report(data),use_container_width=True,hide_index=True)

if st.button("Run Isolation Forest anomaly detection"):
    with st.spinner("Detecting unusual API behavior..."):
        tagged,_=detect_anomalies(data)
    anomalies=tagged[tagged["anomaly_flag"]==-1].sort_values("anomaly_score")
    st.metric("Flagged anomalies",len(anomalies))
    st.dataframe(anomalies,use_container_width=True,hide_index=True)
    st.download_button("Download anomaly results",anomalies.to_csv(index=False).encode(), "api_anomalies.csv","text/csv")

st.subheader("Failed API Requests")
st.dataframe(data[data.is_failure==1].sort_values("timestamp",ascending=False),use_container_width=True,hide_index=True)
st.download_button("Download filtered logs",data.to_csv(index=False).encode(),"filtered_api_logs.csv","text/csv")
