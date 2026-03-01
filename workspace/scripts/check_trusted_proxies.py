#!/usr/bin/env python3
import json
from pathlib import Path

cfg = Path('/Users/dongshenglu/.openclaw/openclaw.json')
out = Path('/Users/dongshenglu/openclaw-system/workspace/docs/trusted-proxies-check.json')

c = json.loads(cfg.read_text())
gw = c.get('gateway', {})
trusted = gw.get('trustedProxies', [])
mode = gw.get('mode', 'unknown')

needs = len(trusted) == 0
suggest = {
  "gateway": {
    "trustedProxies": ["127.0.0.1", "::1"]
  }
}

result = {
  "ok": True,
  "gatewayMode": mode,
  "trustedProxiesConfigured": not needs,
  "trustedProxies": trusted,
  "action": "no_change" if not needs else "review_if_reverse_proxy",
  "patchDraft": suggest if needs else None
}
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False))
