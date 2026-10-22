from pathlib import Path
import sqlite3
import pandas as pd

def write_sqlite(df, db_path):
    path=Path(db_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path) as conn:
        df.to_sql("api_logs",conn,if_exists="replace",index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_status ON api_logs(status_code)")
    return path

def query_sql(db_path, sql):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql,conn)
