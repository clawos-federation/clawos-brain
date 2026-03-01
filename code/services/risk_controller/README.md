# Risk Controller Service

SDK-level risk enforcement for ClawOS with hard enforcement for Alpha isolation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         GM Layer                            │
│  (validates before dispatch using risk_controller)          │
└─────────────────────┬───────────────────────────────────────┘
                      │ validate_action()
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Risk Controller                          │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Node Restriction│  │ Action Restrict │                   │
│  │   (hard)        │  │    (hard)       │                   │
│  └─────────────────┘  └─────────────────┘                   │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Resource Limit  │  │ Safety Action   │                   │
│  │ (soft/hard)     │  │    (hard)       │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ reads
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              risk-limits.json                               │
│  ~/clawos/blackboard/shared/risk-limits.json               │
│                                                             │
│  immutable: [alpha-isolation, trading-limits, disconnect]   │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### SDK Integration

```python
from clawos.services.risk_controller import (
    validate_action,
    get_allowed_nodes,
    get_risk_controller
)

# Simple validation
allowed, reason = validate_action(
    "alpha-executor",
    "execute-trade",
    {"targetNode": "quant"}
)

# Get allowed nodes
nodes = get_allowed_nodes("alpha-executor")
# Returns: ["quant", "alpha-codespace-001"]

# Check immutability
rc = get_risk_controller()
is_immutable = rc.is_rule_immutable("alpha-isolation")  # True
```

### Rule Types

| Type | Description | Enforcement |
|------|-------------|-------------|
| `node-restriction` | Limit which nodes an agent can run on | Hard |
| `action-restriction` | Forbid specific actions | Hard |
| `resource-limit` | Token/cost limits | Soft/Hard |
| `safety-action` | Auto-triggered safety | Hard |

### Immutable Rules

These rules **cannot** be modified at runtime:
- `alpha-isolation` - Alpha executor node restriction
- `trading-limits` - Trading risk limits
- `disconnect-action` - Auto-stop on disconnect

## Files

```
clawos/services/risk_controller/
├── __init__.py              # Package exports
├── controller.py            # Core RiskController class
└── gm_integration_example.py # GM usage example

~/clawos/blackboard/shared/
├── risk-limits.json         # Rule definitions
└── violations/
    └── violations.json      # Violation log
```

## Rule Configuration

Edit `~/clawos/blackboard/shared/risk-limits.json`:

```json
{
  "rules": [
    {
      "id": "my-rule",
      "type": "node-restriction",
      "agents": ["my-agent"],
      "allowedNodes": ["node-1", "node-2"],
      "enforcement": "hard",
      "bypassable": false
    }
  ]
}
```

**Note**: Rules in `immutable` array cannot be changed at runtime.

## Violation Logging

All violations are logged to memory and can be saved:

```python
rc = get_risk_controller()
rc.save_violation_log()  # Saves to violations.json
print(rc.violation_log)  # Access in-memory log
```
