#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

job_id = 'db9d1961-f9dc-47c6-8110-dbb485367b84'
out = Path('/Users/dongshenglu/openclaw-system/workspace/docs/cron-delivery-check.json')

p = subprocess.run([
  'openclaw','cron','runs','--id',job_id
], capture_output=True, text=True)

if p.returncode != 0:
  out.write_text(json.dumps({"ok":False,"error":p.stderr.strip()},ensure_ascii=False,indent=2)+"\n")
  print(json.dumps({"ok":False,"error":p.stderr.strip()},ensure_ascii=False))
  raise SystemExit(1)

raw = p.stdout.strip()
obj = json.loads(raw)
entries = obj.get('entries', [])
recent = entries[:10]
fail = [e for e in recent if e.get('status') == 'error']

res = {
  "ok": True,
  "jobId": job_id,
  "recentCount": len(recent),
  "errorCount": len(fail),
  "needsAttention": len(fail) > 0,
  "latestError": fail[0] if fail else None
}
out.write_text(json.dumps(res, ensure_ascii=False, indent=2)+"\n")
print(json.dumps(res, ensure_ascii=False))
