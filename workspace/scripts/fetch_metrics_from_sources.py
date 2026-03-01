#!/usr/bin/env python3
import json, os, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path


def load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

ROOT = Path('/Users/dongshenglu/openclaw-system/workspace')
out = ROOT / 'monitoring' / 'latest_metrics.json'
out.parent.mkdir(parents=True, exist_ok=True)
load_env_file(ROOT / 'monitoring' / 'metrics-source.env')
TZ8 = timezone(timedelta(hours=8))
now = datetime.now(TZ8).isoformat(timespec='seconds')

# Priority: Grafana -> Datadog

def write_payload(payload):
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'ok': True, 'source': payload.get('source'), 'path': str(out)}, ensure_ascii=False))

# 1) Grafana webhook/json endpoint mode
# env:
#   METRICS_GRAFANA_URL
#   METRICS_GRAFANA_BEARER (optional)
url = os.getenv('METRICS_GRAFANA_URL')
if url:
    req = urllib.request.Request(url)
    tok = os.getenv('METRICS_GRAFANA_BEARER')
    if tok:
        req.add_header('Authorization', f'Bearer {tok}')
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    source_name = 'local-file' if url.startswith('file://') else 'grafana'
    payload = {
        'errorRatePercent': float(data['errorRatePercent']),
        'p95LatencyDeltaPercent': float(data['p95LatencyDeltaPercent']),
        'costDeltaPercent': float(data['costDeltaPercent']),
        'criticalSecurityAlert': bool(data['criticalSecurityAlert']),
        'dataConsistencyIssue': bool(data['dataConsistencyIssue']),
        'source': source_name,
        'updatedAt': data.get('updatedAt', now)
    }
    write_payload(payload)
    raise SystemExit(0)

# 2) Datadog webhook/json endpoint mode
# env:
#   METRICS_DATADOG_URL
#   METRICS_DATADOG_API_KEY (optional)
url = os.getenv('METRICS_DATADOG_URL')
if url:
    req = urllib.request.Request(url)
    key = os.getenv('METRICS_DATADOG_API_KEY')
    if key:
        req.add_header('DD-API-KEY', key)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    payload = {
        'errorRatePercent': float(data['errorRatePercent']),
        'p95LatencyDeltaPercent': float(data['p95LatencyDeltaPercent']),
        'costDeltaPercent': float(data['costDeltaPercent']),
        'criticalSecurityAlert': bool(data['criticalSecurityAlert']),
        'dataConsistencyIssue': bool(data['dataConsistencyIssue']),
        'source': 'datadog',
        'updatedAt': data.get('updatedAt', now)
    }
    write_payload(payload)
    raise SystemExit(0)

# 3) No source configured -> keep current file if exists; otherwise emit template w/ manual source
if out.exists():
    print(json.dumps({'ok': True, 'source': 'existing', 'path': str(out), 'note': 'no external source env configured'}))
else:
    payload = {
        'errorRatePercent': 0.0,
        'p95LatencyDeltaPercent': 0.0,
        'costDeltaPercent': 0.0,
        'criticalSecurityAlert': False,
        'dataConsistencyIssue': False,
        'source': 'manual',
        'updatedAt': now
    }
    write_payload(payload)
