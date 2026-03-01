# Error Escalation Skill

## Purpose

Standardized error reporting and escalation mechanism for ClawOS agents.

---

## Trigger

Use this skill when:
- A task fails after retry attempts
- An unhandled exception occurs
- A validation check fails critically
- A deadline is missed

---

## Protocol

### 1. Classify Error Severity

| Level | Code | Description | Action |
|-------|------|-------------|--------|
| **INFO** | E001 | Minor issue, auto-recovered | Log only |
| **WARN** | E002 | Recoverable, but needs attention | Notify PM |
| **ERROR** | E003 | Task failed, needs intervention | Escalate to GM |
| **CRITICAL** | E004 | System-level failure | Escalate to GM + User |

### 2. Generate Error Report

Write to: `~/clawos/blackboard/errors/{taskId}/{timestamp}.md`

```markdown
# Error Report

## Metadata
- **Error ID**: {uuid}
- **Task ID**: {taskId}
- **Agent**: {agentId}
- **Step**: {stepName}
- **Severity**: {LEVEL}
- **Timestamp**: {ISO8601}
- **Retry Count**: {n}/3

## Error Details
- **Type**: {ErrorType}
- **Message**: {errorMessage}
- **Stack**: 
  ```
  {stackTrace}
  ```

## Context
- **Input**: {sanitizedInput}
- **State at Failure**: {stateSnapshot}
- **Previous Step Output**: {prevOutput}

## Impact
- **Affected Tasks**: {taskList}
- **Rollback Needed**: {yes/no}
- **User Impact**: {description}

## Recovery Options
1. {option1} - {estimatedTime}
2. {option2} - {estimatedTime}
3. Skip and continue - {consequences}

## Recommended Action
{recommendation}
```

### 3. Escalation Path

```
INFO  → Log to ~/clawos/blackboard/logs/
WARN  → Notify PM via agentToAgent
ERROR → Write escalation.md + Notify GM
CRIT  → Write escalation.md + Notify GM + Notify User immediately
```

### 4. Notification Format

**For GM:**
```
🚨 [ERROR] Task {taskId} failed at step "{step}"

Agent: {agentId}
Error: {shortMessage}

Recovery options available. Check:
~/clawos/blackboard/errors/{taskId}/

Reply with action: "retry", "skip", or "abort"
```

**For User:**
```
⚠️ 任务遇到问题

您的任务 "{taskName}" 在执行过程中遇到问题：
{userFriendlyMessage}

我们已经通知管理员处理。
如需立即帮助，请回复 "状态" 查看详情。
```

---

## Integration with Lobster Workflows

Add to any workflow's `onError` handler:

```typescript
onError: async (ctx, error) => {
  await ctx.useSkill('error-escalation', {
    taskId: ctx.input.taskId,
    agent: ctx.agentId,
    step: ctx.currentStep,
    error: error,
    severity: 'ERROR',
    context: {
      input: ctx.input,
      state: ctx.state,
    },
  });
},
```

---

## Recovery Actions

| Command | Action | Prerequisites |
|---------|--------|---------------|
| `retry` | Retry from failed step | None |
| `skip` | Skip step, continue | Step must be optional |
| `rollback` | Execute compensation | Compensation defined |
| `abort` | Terminate workflow | None |

---

## Metrics

Errors are tracked in: `~/clawos/blackboard/metrics/errors.json`

```json
{
  "daily": { "E001": 0, "E002": 0, "E003": 0, "E004": 0 },
  "byAgent": { "agentId": { "total": 0, "byType": {} } },
  "trends": []
}
```

---

*Skill Version: 1.0*
*Compatible with: ClawOS 2026.2+*
