# Skill Discovery Proposal

**Proposal ID**: [AUTO-GENERATED]
**Created**: [TIMESTAMP]
**Source**: ClawHub
**Status**: ⏳ PENDING APPROVAL

---

## Skill Information

| Field | Value |
|-------|-------|
| **Skill Name** | [SKILL_NAME] |
| **Skill ID** | [SKILL_ID] |
| **Version** | [VERSION] |
| **Author** | [AUTHOR] |
| **Category** | [CATEGORY] |
| **ClawHub URL** | [URL] |

## Description

[BRIEF_DESCRIPTION]

## Dependencies

| Dependency | Version | Required |
|------------|---------|----------|
| [DEP_1] | [VERSION] | Yes/No |
| [DEP_2] | [VERSION] | Yes/No |

## Security Assessment

### Auto-Check Results

| Check | Status | Notes |
|-------|--------|-------|
| ClawHub Verified | ✅/❌ | [NOTES] |
| No Executable Code | ✅/❌ | [NOTES] |
| Minimal Permissions | ✅/❌ | [NOTES] |
| No External Calls | ✅/❌ | [NOTES] |
| Dependencies Safe | ✅/❌ | [NOTES] |

### Permission Requirements

```json
{
  "allowedCommands": ["[CMD_1]", "[CMD_2]"],
  "blockedCommands": ["*"],
  "fileAccess": ["[PATH_1]"],
  "networkAccess": false
}
```

### Risk Assessment

- **Risk Level**: LOW / MEDIUM / HIGH
- **Rationale**: [RATIONALE]
- **Mitigations**: [MITIGATIONS]

## Sandbox Test Results

**Test Date**: [DATE]
**Test Environment**: ~/clawos/sandbox/

| Test Case | Result |
|-----------|--------|
| Install | ✅/❌ |
| Basic Execution | ✅/❌ |
| Error Handling | ✅/❌ |
| Cleanup | ✅/❌ |

## Installation Plan

1. Download skill from ClawHub
2. Verify checksum matches manifest
3. Extract to `~/clawos/skills/[SKILL_NAME]/`
4. Run post-install scripts (if any)
5. Update MANIFEST.md
6. Create audit log entry

## Approval

### Review Chain

| Reviewer | Status | Date | Notes |
|----------|--------|------|-------|
| Security Agent | ⏳ PENDING | - | - |
| Platform PM | ⏳ PENDING | - | - |
| GM | ⏳ PENDING | - | - |
| Human | ⏳ PENDING | - | - |

### Final Decision

- **Decision**: ⏳ PENDING / ✅ APPROVED / ❌ REJECTED
- **Approved By**: [HUMAN_NAME]
- **Approval Date**: [DATE]
- **Notes**: [NOTES]

---

## Audit Trail

| Timestamp | Action | Actor | Details |
|-----------|--------|-------|---------|
| [TS] | Proposal Created | System | Auto-generated from ClawHub scan |
| - | - | - | - |

---

*This proposal requires human approval before installation.*
