#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path('/Users/dongshenglu/openclaw-system/workspace')
src = ROOT / 'monitoring' / 'latest_metrics.json'
dst = ROOT / 'MIGRATION_METRICS.json'

required = [
    'errorRatePercent',
    'p95LatencyDeltaPercent',
    'costDeltaPercent',
    'criticalSecurityAlert',
    'dataConsistencyIssue',
    'source'
]

if not src.exists():
    raise SystemExit(f'source file not found: {src}')

payload = json.loads(src.read_text())
missing = [k for k in required if k not in payload]
if missing:
    raise SystemExit(f'missing fields: {missing}')

if payload.get('source') in ('default-template', '', None):
    raise SystemExit('invalid source: must be real source (e.g. grafana/datadog/manual)')

normalized = {
    'errorRatePercent': float(payload['errorRatePercent']),
    'p95LatencyDeltaPercent': float(payload['p95LatencyDeltaPercent']),
    'costDeltaPercent': float(payload['costDeltaPercent']),
    'criticalSecurityAlert': bool(payload['criticalSecurityAlert']),
    'dataConsistencyIssue': bool(payload['dataConsistencyIssue']),
    'source': str(payload['source']),
    'syncedAt': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
}

if 'updatedAt' in payload:
    normalized['upstreamUpdatedAt'] = payload['updatedAt']

dst.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'ok': True, 'source': normalized['source']}, ensure_ascii=False))
