-- The Python pipeline creates this table automatically in reports/api_logs.sqlite.
-- Error rates by endpoint
SELECT endpoint, COUNT(*) AS requests, SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS failures,
       ROUND(100.0 * SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) / COUNT(*), 2) AS error_rate_pct
FROM api_logs GROUP BY endpoint ORDER BY error_rate_pct DESC;

-- Failures by HTTP status code
SELECT status_code, COUNT(*) AS request_count
FROM api_logs WHERE status_code >= 400 GROUP BY status_code ORDER BY request_count DESC;

-- Average and p95 latency are calculated in Python; SQL average latency by endpoint:
SELECT endpoint, ROUND(AVG(response_time_ms),2) AS avg_latency_ms
FROM api_logs GROUP BY endpoint ORDER BY avg_latency_ms DESC;

-- Slow requests
SELECT timestamp, endpoint, http_method, status_code, response_time_ms
FROM api_logs WHERE response_time_ms >= 1000 ORDER BY response_time_ms DESC;

-- Daily trends
SELECT substr(timestamp,1,10) AS day, COUNT(*) AS requests,
       SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS failures
FROM api_logs GROUP BY day ORDER BY day;
