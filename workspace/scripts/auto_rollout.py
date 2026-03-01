#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_METRIC_AGE_MIN = 20

ROOT = Path('/Users/dongshenglu/openclaw-system/workspace')
state_path = ROOT / 'MIGRATION_ROLLOUT_STATE.json'
metrics_path = ROOT / 'MIGRATION_METRICS.json'
log_path = ROOT / 'logs' / 'migration_rollout.log'
log_path.parent.mkdir(parents=True, exist_ok=True)

TZ8 = timezone(timedelta(hours=8))
now = datetime.now(TZ8)

if not state_path.exists():
    raise SystemExit('MIGRATION_ROLLOUT_STATE.json not found')

state = json.loads(state_path.read_text())

# Default metrics template when absent
if metrics_path.exists():
    metrics = json.loads(metrics_path.read_text())
else:
    metrics = {
        'errorRatePercent': 0.0,
        'p95LatencyDeltaPercent': 0.0,
        'costDeltaPercent': 0.0,
        'criticalSecurityAlert': False,
        'dataConsistencyIssue': False,
        'source': 'default-template'
    }

traffic = state.get('traffic', {})
current = int(traffic.get('v7_7', 0))

# Freshness guard: freeze rollout when upstream metrics are stale
stale_metrics = False
stale_reason = None
raw_upstream_ts = metrics.get('upstreamUpdatedAt')
if raw_upstream_ts:
    try:
        upstream_dt = datetime.fromisoformat(str(raw_upstream_ts).replace('Z', '+00:00'))
        age_min = (now - upstream_dt.astimezone(TZ8)).total_seconds() / 60
        stale_metrics = age_min > MAX_METRIC_AGE_MIN
        if stale_metrics:
            stale_reason = f"metrics_stale:{age_min:.1f}min"
    except Exception:
        stale_metrics = True
        stale_reason = 'metrics_timestamp_parse_error'

# Gates
rollback = (
    metrics.get('errorRatePercent', 0) > 2
    or metrics.get('p95LatencyDeltaPercent', 0) > 30
    or bool(metrics.get('criticalSecurityAlert', False))
    or bool(metrics.get('dataConsistencyIssue', False))
)

has_real_metrics = metrics.get('source') not in (None, '', 'default-template')

go = (
    has_real_metrics
    and not stale_metrics
    and metrics.get('errorRatePercent', 0) <= 0.5
    and metrics.get('p95LatencyDeltaPercent', 0) <= 15
    and metrics.get('costDeltaPercent', 0) <= 10
    and not bool(metrics.get('criticalSecurityAlert', False))
)

next_steps = {5: 20, 20: 50, 50: 100, 100: 100}

if rollback:
    new = 0
    state['status'] = 'rolled_back'
    state['phase'] = 'rollback'
elif go:
    new = next_steps.get(current, current)
    state['status'] = 'progressing' if new < 100 else 'full_rollout'
    state['phase'] = 'C' if new < 100 else 'D'
else:
    new = current
    state['status'] = 'hold'
    if stale_metrics and stale_reason:
        state['holdReason'] = stale_reason
    elif 'holdReason' in state:
        del state['holdReason']

if state.get('status') != 'hold' and 'holdReason' in state:
    del state['holdReason']

state['traffic'] = {'v6_6_1': 100 - new, 'v7_7': new}
state['lastEvaluatedAt'] = now.isoformat(timespec='seconds')
state['nextCheckpoint'] = (now + timedelta(minutes=30)).isoformat(timespec='seconds')
state['lastMetrics'] = metrics
state['metricFreshness'] = {
    'maxAgeMinutes': MAX_METRIC_AGE_MIN,
    'stale': stale_metrics,
    'reason': stale_reason
}

state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')

with log_path.open('a', encoding='utf-8') as f:
    f.write(f"[{now.isoformat(timespec='seconds')}] traffic={new}% status={state['status']} metrics={metrics}\n")

print(json.dumps({'ok': True, 'traffic_v7_7': new, 'status': state['status']}, ensure_ascii=False))
