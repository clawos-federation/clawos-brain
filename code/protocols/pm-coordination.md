# PM Coordination Protocol v1.0

**Effective Date**: 2026-02-25  
**Last Updated**: 2026-02-25

---

## 1. PM Hierarchy & Responsibilities

### L2 PMs (Tier: ECO)

| PM | Tier | Primary Domain | Subagents |
|----|----|--------|-----------|
| **Platform PM** | TITAN | Infrastructure, skills, registry, system health | sreagent, securityagent, alpha-bridge |
| **Coding PM** | ECO | Code development, testing, CI/CD | coder-frontend, coder-backend, tester-auto, github-ops |
| **Writing PM** | ECO | Content creation, research, review | writer-general, researcher-web, reviewer-content |

---

## 2. Resource Ownership & Boundaries

### Exclusive Resources (No Sharing)

- **Coding PM** → github-ops (code operations, PR management)
- **Writing PM** → writer-general, researcher-web, reviewer-content
- **Platform PM** → sreagent, securityagent, alpha-bridge

### Shared Resources (None Currently)

All agents are exclusively owned. No contention.

---

## 3. Cross-PM Coordination Rules

### Rule 1: Direct vs. Indirect Access

**Direct Access**: Each PM controls its own subagents directly.

**Indirect Access**: If PM A needs PM B's agent:
1. PM A sends request to PM B (via message or task queue)
2. PM B evaluates request and decides to accept/reject
3. If accepted, PM B executes task using its agent
4. PM B returns results to PM A

**Example**: Platform PM needs git operation → requests Coding PM → Coding PM uses github-ops

### Rule 2: Priority System

**Priority Levels** (highest to lowest):
1. **CRITICAL** — System down, security breach, data loss risk
2. **HIGH** — Feature deadline, blocking issue, performance degradation
3. **NORMAL** — Regular tasks, maintenance, optimization
4. **LOW** — Nice-to-have, documentation, cleanup

**Conflict Resolution**:
- CRITICAL > HIGH > NORMAL > LOW
- Same priority → FIFO (first request wins)
- PM can escalate to GM if priority disputed

### Rule 3: Task Handoff Protocol

When PM A requests PM B's agent:

```
Request Format:
{
  "from_pm": "platform-pm",
  "to_pm": "coding-pm",
  "task_id": "unique-id",
  "priority": "HIGH",
  "agent": "github-ops",
  "action": "commit-registry-update",
  "deadline": "2026-02-25T12:00:00Z",
  "context": "Update agent registry after skill validation"
}

Response Format:
{
  "task_id": "unique-id",
  "status": "accepted|rejected",
  "reason": "if rejected",
  "eta": "2026-02-25T11:30:00Z",
  "result": "after completion"
}
```

### Rule 4: Conflict Resolution

**Scenario 1**: Two PMs request same agent simultaneously
- Lower priority request waits
- If same priority, FIFO
- Max wait time: 30 minutes (then escalate to GM)

**Scenario 2**: PM requests agent for task exceeding agent's permissions
- Requesting PM must escalate to GM
- GM decides: approve, deny, or modify permissions

**Scenario 3**: Agent fails during PM's task
- PM retries up to 2 times
- If still fails, escalate to Platform PM (sreagent investigates)
- GM notified if issue persists >1 hour

---

## 4. Heartbeat & Monitoring

### Platform PM Heartbeat (Every 1 hour)

Tasks:
1. Check all subagent health (sreagent, securityagent, alpha-bridge)
2. Verify Coding PM and Writing PM are responsive
3. Scan for stuck tasks (>30 min without progress)
4. Generate system health report
5. Escalate issues to GM if needed

### Coding PM Heartbeat (Recommended: Every 2 hours)

Tasks:
1. Check github-ops availability
2. Verify code repositories are accessible
3. Check CI/CD pipeline status
4. Report build failures

### Writing PM Heartbeat (Recommended: Every 4 hours)

Tasks:
1. Check writer-general availability
2. Verify research sources are accessible
3. Report content generation issues

---

## 5. Escalation Path

```
Issue Detected
    ↓
PM Attempts Resolution (max 15 min)
    ↓
If Unresolved → Escalate to GM
    ↓
GM Reviews & Decides
    ↓
If Critical → Notify Human Operator
```

---

## 6. Communication Channels

- **PM-to-PM**: Task queue in `~/clawos/blackboard/tasks/`
- **PM-to-GM**: Escalation messages in `~/clawos/blackboard/gm/escalations.md`
- **PM-to-Agents**: Direct subagent invocation
- **PM-to-Human**: Notifications in `~/clawos/notifications/`

---

## 7. Decision Log

All PM decisions must be logged in respective blackboard:
- Platform PM: `~/clawos/blackboard/platform-pm/decisions.md`
- Coding PM: `~/clawos/blackboard/coding-pm/decisions.md`
- Writing PM: `~/clawos/blackboard/writing-pm/decisions.md`

Format:
```markdown
### Decision N: [Title]
- **Time**: 2026-02-25T10:30:00Z
- **Type**: Resource | Priority | Escalation | Other
- **Context**: [Why this decision]
- **Decision**: [What was decided]
- **Rationale**: [Why this approach]
- **Impact**: [Effect on system]
```

---

## 8. Review & Updates

- **Review Frequency**: Monthly (first Monday of month)
- **Update Process**: Propose changes → GM approval → Update protocol
- **Version History**: Maintained in git

---

*This protocol ensures clear boundaries, prevents conflicts, and enables efficient multi-PM coordination.*
