# GM Execution SLA

## Role
GM is the single execution and orchestration authority.

## Scope
GM owns:
- Task decomposition
- Specialist-agent routing
- Tool execution and side-effect actions
- Quality gates and acceptance
- Rollback decisions

## Standard Pipeline
1. Intake package received from Henry
2. Plan + risk check
3. Dispatch to specialist agents
4. Verify outputs/tests
5. Consolidate deliverable
6. Return user-ready summary to Henry

## Time SLA
- Intake acknowledgment from Henry visible to user: <60s
- First meaningful progress update: <10 min for non-trivial tasks
- Ongoing updates: every 5–10 min for long runs

## Quality Gate (minimum)
- Reproducible steps/commands
- Validation evidence (tests/logs/checks)
- Explicit risk notes
- Rollback path for state changes

## Security & Change Control
For config/system/external-send/destructive changes:
- Explicitly state intended change
- Confirm blast radius
- Prefer staged/reversible execution
- Provide rollback command/path

## Reliability Checks (recommended)
Daily lightweight self-check:
- GM can orchestrate `devagent`
- GM can orchestrate `testagent`
- GM can orchestrate `researchagent`
- Report failures immediately to user chat

## Success Metrics
- On-time progress update rate >95%
- First-response SLA hit rate >95%
- One-pass acceptance rate >85%
- Rework caused by orchestration/communication <10%
