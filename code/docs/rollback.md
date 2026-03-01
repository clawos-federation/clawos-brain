# ClawOS v5 Rollback Guide

> **Version**: 5.0.0-phase0.5  
> **Last Updated**: 2026-02-27  
> **Purpose**: Safe rollback procedures for v5 features

---

## Quick Reference

| Feature | Config Path | Default | Risk |
|---------|-------------|---------|------|
| identity-system | `features.identity-system.enabled` | false | Medium |
| a2a-registry | `features.a2a-registry.enabled` | false | Medium |
| evolution-scheduler | `features.evolution-scheduler.enabled` | false | High |
| utility-scoring | `features.utility-scoring.enabled` | false | Low |
| memory-l3 | `features.memory-l3.enabled` | false | Medium |
| risk-controller | `features.risk-controller.enabled` | false | High |

---

## Disabling Individual Features

### 1. Identity System

```bash
# Disable identity verification
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.identity-system.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Revert behavior: Agents use simple name-based identification
# Impact: A2A registry will stop working (depends on identity)
```

### 2. A2A Registry

```bash
# Disable A2A communication
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.a2a-registry.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Revert behavior: All agent communication goes through GM → PM chain
# Impact: Direct agent-to-agent calls will fail
```

### 3. Evolution Scheduler

```bash
# Disable evolution scheduling
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.evolution-scheduler.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Stop any running evolution processes
pkill -f "evolution" || true

# Revert behavior: No automatic self-improvement
# Impact: Manual evolution triggers still work
```

### 4. Utility Scoring

```bash
# Disable utility tracking
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.utility-scoring.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Revert behavior: Static priority-based task assignment
# Impact: No reputation-based routing
```

### 5. Memory L3

```bash
# Disable long-term memory
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.memory-l3.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Revert behavior: Only L1 (session) and L2 (blackboard) memory active
# Impact: No vector search, no cross-session learning
```

### 6. Risk Controller

```bash
# Disable risk automation
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features.risk-controller.enabled = false' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# Revert behavior: All risky operations require manual approval
# Impact: Increased human oversight needed
```

---

## Full v4 Reversion

To completely revert to v4 behavior:

```bash
# 1. Disable all v5 features
cat ~/.openclaw/clawos/clawos/config/features.json | jq '
  .features.identity-system.enabled = false |
  .features.a2a-registry.enabled = false |
  .features.evolution-scheduler.enabled = false |
  .features.utility-scoring.enabled = false |
  .features.memory-l3.enabled = false |
  .features.risk-controller.enabled = false
' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# 2. Stop any v5-specific services
pkill -f "evolution" || true
pkill -f "risk-controller" || true

# 3. Clear v5 caches
rm -rf ~/clawos/blackboard/metrics/*.cache 2>/dev/null || true

# 4. Verify v4 operation
openclaw agent --agent gm --task "status check"
```

---

## Emergency Stop Procedure

### Level 1: Soft Stop (Disable new v5 operations)

```bash
# Set emergency flag
cat ~/.openclaw/clawos/clawos/config/features.json | jq '
  .emergencyStop.enabled = true |
  .emergencyStop.reason = "Manual emergency stop" |
  .emergencyStop.timestamp = (now | todate)
' > /tmp/features.json
mv /tmp/features.json ~/.openclaw/clawos/clawos/config/features.json

# All v5 features will be ignored, v4 behavior resumes
```

### Level 2: Hard Stop (Kill all v5 processes)

```bash
# Run soft stop first
# (commands from Level 1)

# Then kill processes
pkill -9 -f "evolution" || true
pkill -9 -f "risk-controller" || true
pkill -9 -f "a2a-registry" || true

# Clear shared memory
rm -rf /tmp/clawos-* 2>/dev/null || true
```

### Level 3: Nuclear (Restore from backup)

```bash
# ONLY use if system is completely unstable

# 1. Stop everything
pkill -9 -f "openclaw" || true

# 2. Restore config from backup
cp ~/.openclaw/clawos/clawos/config/features.json.bak ~/.openclaw/clawos/clawos/config/features.json 2>/dev/null || true

# 3. Clear blackboard (KEEPS task data)
rm -rf ~/clawos/blackboard/metrics/* 2>/dev/null || true

# 4. Restart
cd ~/.openclaw/clawos && openclaw start
```

---

## Verification After Rollback

```bash
# Check feature flags
cat ~/.openclaw/clawos/clawos/config/features.json | jq '.features | to_entries[] | select(.value.enabled == true)'

# Should return empty if all disabled

# Check system health
cat ~/clawos/blackboard/metrics/system-metrics.json | jq '.health'

# Should show status: "healthy"

# Test basic operation
openclaw agent --agent gm --task "echo rollback test"
```

---

## Rollback Decision Matrix

| Symptom | Action | Rollback Level |
|---------|--------|----------------|
| Slow response | Disable utility-scoring | Individual |
| Memory errors | Disable memory-l3 | Individual |
| Agent conflicts | Disable a2a-registry | Individual |
| Unexpected behavior | Disable evolution-scheduler | Individual |
| Risk bypass attempts | Disable risk-controller | Individual |
| System instability | Full v4 reversion | Full |
| Complete failure | Nuclear restore | Level 3 |

---

## Contact

If rollback doesn't resolve issues:
1. Check logs: `~/.openclaw/clawos/clawos/logs/`
2. Review metrics: `~/clawos/blackboard/metrics/`
3. Report issue with reproduction steps
