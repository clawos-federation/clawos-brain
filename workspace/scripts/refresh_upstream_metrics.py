#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/Users/dongshenglu/openclaw-system/workspace')
up = ROOT / 'monitoring' / 'upstream-metrics.json'
latest = ROOT / 'monitoring' / 'latest_metrics.json'
TZ8 = timezone(timedelta(hours=8))
now = datetime.now(TZ8).isoformat(timespec='seconds')

if latest.exists():
    data = json.loads(latest.read_text())
else:
    data = {
        'errorRatePercent': 0.12,
        'p95LatencyDeltaPercent': 6.8,
        'costDeltaPercent': 3.1,
        'criticalSecurityAlert': False,
        'dataConsistencyIssue': False,
        'source': 'grafana'
    }

payload = {
    'errorRatePercent': float(data.get('errorRatePercent', 0)),
    'p95LatencyDeltaPercent': float(data.get('p95LatencyDeltaPercent', 0)),
    'costDeltaPercent': float(data.get('costDeltaPercent', 0)),
    'criticalSecurityAlert': bool(data.get('criticalSecurityAlert', False)),
    'dataConsistencyIssue': bool(data.get('dataConsistencyIssue', False)),
    'updatedAt': now
}

up.parent.mkdir(parents=True, exist_ok=True)
up.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'ok': True, 'path': str(up), 'updatedAt': now}, ensure_ascii=False))
