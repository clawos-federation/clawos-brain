# Metrics 真源接入说明（Grafana / Datadog）

脚本：`scripts/fetch_metrics_from_sources.py`
输出：`monitoring/latest_metrics.json`

## 方式 A：Grafana JSON 端点
设置环境变量：
- `METRICS_GRAFANA_URL`
- `METRICS_GRAFANA_BEARER`（可选）

## 方式 B：Datadog JSON 端点
设置环境变量：
- `METRICS_DATADOG_URL`
- `METRICS_DATADOG_API_KEY`（可选）

## 字段要求
端点返回 JSON 必须包含：
- `errorRatePercent`
- `p95LatencyDeltaPercent`
- `costDeltaPercent`
- `criticalSecurityAlert`
- `dataConsistencyIssue`
- `updatedAt`（建议）

## 本地联调
```bash
python3 scripts/fetch_metrics_from_sources.py
python3 scripts/sync_metrics.py
python3 scripts/auto_rollout.py
```
