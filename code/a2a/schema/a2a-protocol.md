# A2A Protocol Documentation

## Overview

**A2A (Agent-to-Agent)** is Google's open protocol for agent discovery and communication, announced in April 2025. It enables AI agents to discover each other's capabilities, negotiate tasks, and collaborate seamlessly.

## Core Concepts

### Agent Cards

An **Agent Card** is a JSON document that describes an agent's:
- Identity and purpose
- Capabilities and skills
- Performance metrics
- Communication endpoints
- Authentication requirements

Think of it as a "business card" for AI agents.

### Protocol Version

This implementation follows **A2A Protocol v0.3.0** specifications.

## How Agent Cards Work

```
┌─────────────────┐     ┌─────────────────┐
│  Agent A (GM)   │     │  Agent B (PM)   │
│                 │     │                 │
│  1. Need task   │     │  Publishes      │
│     delegation  │     │  Agent Card     │
│        ↓        │     │        ↓        │
│  2. Discover ───┼────→│  Card Registry  │
│     agents      │     │                 │
│        ↓        │     │                 │
│  3. Query card  │←────┼── Card served   │
│        ↓        │     │                 │
│  4. Match skills│     │                 │
│        ↓        │     │                 │
│  5. Delegate    │────→│  Accept task    │
└─────────────────┘     └─────────────────┘
```

## ClawOS Integration

### Tier-Based Discovery

ClawOS uses A2A cards for hierarchical agent discovery:

| Tier | Role | Card Usage |
|------|------|------------|
| Command | GM, Orchestrator | Discovers PMs for delegation |
| PM | Coding-PM, Alpha-PM | Discovers Workers for execution |
| Worker | Coder, Tester, Deployer | Executes tasks, reports results |

### Discovery Flow

1. **GM receives task** from user or cron
2. **GM queries registry** for agents with matching skills
3. **GM evaluates utility scores** to select best PM
4. **PM appointed** receives task via A2A message
5. **PM discovers workers** using same pattern
6. **Worker executes** and reports back

### Utility Scoring

Agents are scored on:
- Task completion rate
- Response time
- Error rate
- Skill relevance match

Score formula:
```
utility = (successRate * 0.4) + (skillMatch * 0.3) + (speed * 0.2) + (reliability * 0.1)
```

## Agent Card Structure

### Minimal Card

```json
{
  "schemaVersion": "1.0",
  "humanReadableId": "openclaw/worker/coder",
  "name": "Coder Worker",
  "description": "Executes coding tasks: write, refactor, debug code",
  "capabilities": {
    "streaming": true,
    "toolUse": true
  },
  "skills": [
    {"id": "code-write", "name": "Code Writing"},
    {"id": "code-refactor", "name": "Code Refactoring"}
  ]
}
```

### Full Card Example

```json
{
  "schemaVersion": "1.0",
  "humanReadableId": "openclaw/pm/coding-pm",
  "agentVersion": "2.1.0",
  "name": "Coding Project Manager",
  "description": "Manages coding projects: task breakdown, worker coordination, quality validation",
  "provider": {
    "organization": "ClawOS",
    "url": "https://clawos.local"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "taskEvaluation": true,
    "pmAppointment": true,
    "finalValidation": true,
    "toolUse": true,
    "multiModal": false
  },
  "skills": [
    {
      "id": "task-breakdown",
      "name": "Task Breakdown",
      "description": "Break down complex tasks into atomic subtasks",
      "tags": ["planning", "decomposition"],
      "proficiency": "expert"
    },
    {
      "id": "code-review",
      "name": "Code Review",
      "description": "Review code for quality and best practices",
      "tags": ["quality", "validation"],
      "proficiency": "advanced"
    }
  ],
  "identity": {
    "did": "did:clawos:codingpm001",
    "node": "coding-pm",
    "tier": "pm",
    "parent": "openclaw/command/gm"
  },
  "memory": {
    "persistent": true,
    "blackboardIntegration": true,
    "maxContextTokens": 128000,
    "memoryTypes": ["short-term", "long-term"]
  },
  "performance": {
    "utilityScore": 0.87,
    "metrics": {
      "tasksCompleted": 1247,
      "tasksFailed": 23,
      "avgResponseTimeMs": 3400,
      "successRate": 0.982
    },
    "nominationEligible": true
  },
  "status": {
    "state": "idle",
    "healthEndpoint": "https://clawos.local/agents/coding-pm/health",
    "lastHeartbeat": "2025-02-27T10:30:00Z"
  },
  "pricing": {
    "model": "free",
    "note": "Internal ClawOS agent"
  },
  "endpoints": {
    "a2a": "https://clawos.local/a2a/coding-pm",
    "rpc": "https://clawos.local/rpc/coding-pm",
    "websocket": "wss://clawos.local/ws/coding-pm",
    "card": "https://clawos.local/cards/coding-pm.json"
  },
  "authentication": {
    "schemes": ["jwt"]
  }
}
```

## Card Registry

ClawOS maintains a local card registry at:
```
~/clawos/a2a/registry/
├── cards/
│   ├── gm.json
│   ├── coding-pm.json
│   ├── alpha-pm.json
│   ├── coder.json
│   ├── tester.json
│   └── ...
└── index.json          # Quick lookup index
```

## Validation

All cards must validate against:
- JSON Schema Draft 2020-12
- ClawOS-specific constraints
- Required fields for tier

## API Endpoints

### Get Card
```
GET /a2a/cards/{agent-id}
Response: Agent Card JSON
```

### Query Agents
```
POST /a2a/query
Body: {"skills": ["code-review"], "tier": "worker"}
Response: Array of matching Agent Cards
```

### Health Check
```
GET /a2a/agents/{agent-id}/health
Response: {"status": "healthy", "timestamp": "..."}
```

## Security Considerations

1. **Authentication**: Cards declare supported auth schemes
2. **Authorization**: Tier-based access control
3. **Integrity**: Cards can be signed with DID
4. **Privacy**: Internal agents not exposed externally

## References

- [Google A2A Protocol Spec](https://github.com/google/A2A) (external reference)
- ClawOS Agent Hierarchy: `workspace/AGENTS.md`
- Agent Identity: `workspace/SOUL.md`

---

*Part of ClawOS 2026.3 · A2A Integration Phase 2*
