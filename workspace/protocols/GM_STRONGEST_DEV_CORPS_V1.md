# GM Strongest Dev Corps v1

## Objective
Build a GM-commanded, production-grade software development corps that is fast, testable, secure, and recoverable.

## Command Structure
- **Henry (Interaction Officer)**: intake, clarification, progress sync, result narration
- **GM (Commander-in-Chief)**: decomposition, orchestration, quality gates, rollback decision
- **Corps Units (Execution)**: specialist agents under GM only

Command chain:
`User -> Henry -> GM -> Specialist Corps -> GM -> Henry -> User`

## Core Corps (Standing Units)
1. **DevAgent** — implementation, refactor, integration
2. **TestAgent** — test design, regression, acceptance checks
3. **ResearchAgent** — technical scouting, trade-off analysis
4. **SREAgent** — deployment, observability, incident handling, rollback
5. **ProductAgent** — requirement decomposition, acceptance criteria
6. **DataAgent** — instrumentation, KPI tracking, A/B readout
7. **SecurityAgent** — dependency risk, permission minimization, security checks

## Initial Expansion Priority
P0 onboard:
- SREAgent
- ProductAgent
- DataAgent

P1 onboard:
- SecurityAgent

## Governance Rules
1. Henry does not execute side-effecting tasks by default.
2. Only GM can route specialist agents.
3. Config/file write/external send/destructive actions require GM quality gate.
4. White-list only (`allowAny=false`) for subagent routing.

## Dynamic Corps Policy
- Dynamic composition is allowed only inside configured + authorized agent pool.
- No unlimited spontaneous new unit creation.
- New unit admission requires:
  - clear scope (do/don’t)
  - verifiable outputs
  - safety boundaries
  - retirement condition

## Admission Checklist (for new units)
- [ ] agent id + model configured in `openclaw.json` -> `agents.list`
- [ ] added to `gm.subagents.allowAgents`
- [ ] template mapping added in `TEAM_TEMPLATES.md`
- [ ] smoke test task passes under GM orchestration
- [ ] rollback/removal path documented

## Standard Development Battleflow
1. Requirement brief (GM + Product + Research)
2. Architecture + execution plan (GM + Dev + SRE)
3. Parallel build (Dev) + early tests (Test)
4. Quality gate (Test + Security + SRE)
5. Release gate (SRE) + metrics check (Data)
6. Postmortem and template updates (GM)

## Quality Gates (Minimum)
- reproducible commands
- test evidence
- risk notes
- rollback path
- success metrics baseline

## Reliability Controls
- Daily `GM routing selfcheck` cron must stay green.
- If routing fails, alert immediately and freeze risky changes.
- Prefer staged rollout + explicit rollback triggers.

## KPIs
- First progress update within 10 min for non-trivial tasks
- On-time progress update rate >95%
- One-pass acceptance rate >85%
- Rework due to orchestration/communication <10%

## 7-Day Rollout Suggestion
- **D1**: onboard SRE/Product/Data agent entries + allowlist
- **D2**: add team templates for ops/product/data tracks
- **D3**: run smoke tasks for each new unit
- **D4**: enforce quality gate checklist in all project closures
- **D5**: connect deployment + monitoring playbook to SRE flow
- **D6**: metrics dashboard + data-readout loop
- **D7**: full drill (feature -> test -> deploy -> monitor -> postmortem)

---

Version: v1
Date: 2026-02-21
Owner: GM
