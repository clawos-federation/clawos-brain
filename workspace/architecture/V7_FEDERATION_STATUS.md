# ClawOS Federation v7 Status

> Last Updated: 2026-02-27 20:37

## v7 Core Concept

**Node = OpenClaw instance (not physical machine)**

- Same-machine nodes use localhost HTTP routing (< 100ms latency)
- Cross-machine nodes use Blackboard + Tailscale
- Zero-cost incubation: create new nodes locally, migrate to cloud when mature

## Node Status

| Node | Status | Transport | Port | Notes |
|------|--------|-----------|------|-------|
| **alpha** | ✅ Online | localhost | 18790 | Quant node, running |
| **mac-mini** | ✅ Online | local | 18789 | Main node |
| **macbook-air** | ❌ Offline | blackboard | 18789 | Sleeping, Tailscale 100.71.170.104 |
| **cloud-node** | ❌ Planned | blackboard | TBD | AWS Lightsail ($5/mo) |

## Communication Channels

1. **localhost HTTP** - same-machine nodes (immediate, < 100ms)
2. **Blackboard** - cross-machine normal tasks (< 5 min polling)
3. **Tailscale SSH** - cross-machine P0 urgent (seconds)

## Pending Tasks

| Task ID | Target | State | Description |
|---------|--------|-------|-------------|
| req_20260227_200645 | macbook-air | pending | 开发 babel chrome 插件 v2 |
| req_20260227_203220_e68aee2d | alpha | pending | 测试 localhost 路由 |
| req_example | any | pending | Implement user authentication |

## Completed Tasks

| Task ID | Node | Description |
|---------|------|-------------|
| req_20260227_195930 | mac-mini | Python 函数计算两数之和 |

## Key Files

```
~/.openclaw/clawos/
├── clawos-brain/          ← DNA/Scripts
│   └── scripts/
│       ├── dispatch-task.sh    ← v7 routing logic
│       ├── check-federation.sh ← Task polling
│       └── incubate-node.sh    ← Node creation
├── clawos-blackboard/     ← Communication
│   └── federation/
│       ├── requests/           ← Pending tasks
│       ├── results/            ← Completed results
│       └── node-status/        ← Node registry
└── clawos-node-alpha/     ← Alpha config

~/.openclaw-alpha/         ← Alpha instance
~/.openclaw/               ← Main instance
```

## Next Steps

1. ⏳ MacBook Air wakes up → processes pending tasks
2. ⏳ Alpha task polling → process localhost-routed tasks
3. ⏳ Cloud node deployment → AWS Lightsail setup
