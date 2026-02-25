# ClawOS Brain

Shared memory and evolution engine for ClawOS multi-agent system.

## Structure

```
clawos-brain/
├── blackboard/       # Shared state
│   ├── gm/           # GM decisions
│   ├── roles/        # Active roles
│   ├── shared/       # Shared context
│   └── tasks/        # Task status
├── memory/           # Persistent memory
│   └── *.md          # Daily memory files
└── templates/        # Memory templates
```

## Blackboard Architecture

The Blackboard is the central shared memory where all agents read and write:

| Directory | Purpose |
|-----------|---------|
| `gm/decisions.md` | GM decision log |
| `roles/active.json` | Currently active roles |
| `shared/context.md` | Shared context |
| `tasks/{taskId}/` | Individual task status |

## Memory System

Four-layer memory architecture:
1. **Session Memory** - Within conversation
2. **Daily Memory** - Cross-session within day
3. **Role Memory** - Persistent per role
4. **Evolution Memory** - System improvements

---
ClawOS 2026.3 - 17 Agents Architecture
