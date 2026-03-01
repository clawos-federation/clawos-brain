# HEARTBEAT.md - ClawOS Periodic Checks

**Read this file on heartbeat. Follow instructions strictly.**

## Purpose

HEARTBEAT is the proactive monitoring and notification mechanism that keeps users informed of system status, task progress, and potential issues without being prompted.

## Files

| File | Purpose |
|------|---------|
| `~/clawos/blackboard/assistant/{userId}/heartbeat-state.json` | Per-user state tracking |
| `~/clawos/blackboard/assistant/{userId}/notifications.json` | Pending notifications queue |
| `~/clawos/blackboard/gm/status.md` | GM decision log and escalations |
| `~/clawos/blackboard/tasks/pending.md` | Pending task queue |

## Periodic Checks (rotate through these)

### 1. Blackboard Status Check
```
Read: ~/clawos/blackboard/gm/status.md
Read: ~/clawos/blackboard/tasks/pending.md
```
- Check for pending tasks requiring attention
- Report any blocked or failed tasks to user
- Update heartbeat-state.json with findings

### 2. Active Workflow Check
```
Read: ~/clawos/blackboard/platform-pm/active-workflows.md
Read: ~/clawos/blackboard/coding-pm/status.md
Read: ~/clawos/blackboard/writing-pm/status.md
```
- Check for running workflows that may need intervention
- Report status of long-running tasks
- Identify tasks approaching timeout

### 3. Agent Health Check
```
Read: ~/.openclaw/agents/*/agent/SOUL.md (sample 2-3)
```
- Verify agent configurations are intact
- Check for any configuration drift
- Report any anomalies

### 4. Persistence Layer Check
```
Read: ~/clawos/blackboard/persistence/metrics/daily-report.json
```
- Review daily metrics
- Identify trends (escalation rate, retry rate)
- Alert on anomalies

## Notification Priority Levels

| Level | Emoji | Condition | Action |
|-------|-------|-----------|--------|
| CRITICAL | Critical | System failure, data loss risk | Immediate alert |
| HIGH | High | Task failed, approval needed | Alert within 1 check |
| MEDIUM | Medium | Task progress update | Alert if user is waiting |
| LOW | Low | Routine status | Silent unless requested |
| INFO | Info | Informational only | Silent |

## When to Alert User

### Always Alert
- Pending task > 24h without progress
- Workflow failure detected
- Agent configuration issues
- Critical system file missing
- Approval request pending > 2h
- GM escalation created

### Alert If User Has Active Session
- Task completed successfully
- Task progress milestone reached (25%, 50%, 75%)
- Worker assignment changed
- Validation score available

### Batch Notifications
- Multiple LOW priority items
- Daily summary (configurable time)
- Weekly metrics summary

## When to Stay Silent (HEARTBEAT_OK)

- No pending tasks
- All workflows running normally
- No configuration issues
- Outside working hours (23:00-08:00) unless urgent
- User in "focus mode" (preferences.json: focusMode: true)
- Only LOW priority items

## State Tracking

Store last check timestamps in:
```
~/clawos/blackboard/assistant/{userId}/heartbeat-state.json
```

Format:
```json
{
  "userId": "user-xxx",
  "lastCheck": "2026-02-24T10:30:00Z",
  "tasks": {
    "tracked": ["task-001", "task-002"],
    "completed": ["task-000"],
    "failed": []
  },
  "notifications": {
    "pending": [
      {
        "id": "notif-001",
        "priority": "MEDIUM",
        "message": "Task task-001 is 50% complete",
        "createdAt": "2026-02-24T10:00:00Z"
      }
    ],
    "sent": ["notif-000"]
  },
  "state": {
    "lastProgressUpdate": "2026-02-24T10:30:00Z",
    "lastEscalation": null,
    "quietMode": false,
    "focusMode": false
  },
  "lastChecks": {
    "blackboard": "2026-02-24T10:30:00Z",
    "workflows": "2026-02-24T10:25:00Z",
    "health": "2026-02-24T09:00:00Z",
    "persistence": "2026-02-24T08:00:00Z"
  }
}
```

## Notification Format

### Task Progress Update
```
**Task Update**
- Task: {taskName}
- Status: {status} ({progress}%)
- Agent: {assignedAgent}
- ETA: {estimatedCompletion}
```

### Task Completion
```
**Task Completed**
- Task: {taskName}
- Duration: {duration}
- Output: {outputPath}
- Validation Score: {score}/10
```

### Escalation Alert
```
**Escalation Required**
- Priority: HIGH
- Task: {taskName}
- Issue: {escalationReason}
- Action Needed: {recommendedAction}
```

### Approval Request
```
**Approval Needed**
- Task: {taskName}
- Type: {approvalType}
- Details: {summary}
- Timeout: {remaining} remaining
```

## Integration with Assistant

The HEARTBEAT mechanism integrates with the Assistant agent:

1. **On Session Start**: Check for pending notifications and report to user
2. **During Session**: Periodic checks based on activity
3. **On Session End**: Queue any pending notifications for next session

## Implementation Notes

- HEARTBEAT runs at configurable intervals (default: 5 minutes)
- State is persisted to survive session boundaries
- Notifications are deduplicated to avoid spam
- User preferences control notification frequency and quiet hours
