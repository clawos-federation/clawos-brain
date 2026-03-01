# ClawOS Skills Manifest

> **Total Skills**: 13 | **Last Updated**: 2026-02-27

## Skills Directory

| Skill | Description | Category |
|-------|-------------|----------|
| **alpha-bridge** | 本地与 Codespace Alpha 系统的通信桥梁 | Communication |
| **blackboard** | 统一的黑板读写操作，支持从共享黑板读取和写入数据（带文件锁） | System |
| **coding-workflow** | 开发工作流 Skill，编排开发任务的完整流程 | Workflow |
| **error-escalation** | 标准化错误上报和升级机制 | System |
| **git-operations** | Git 版本控制操作 Skill，提供标准化 Git 工作流支持 | System |
| **gm-task-evaluate** | 评估任务的可行性、所需资源和风险 | Command |
| **openclaw-agents** | Agent 路由和执行系统（DevAgent, LegalAgent, ResearchAgent） | Agent |
| **pm-team-assemble** | 从 Agent Registry 挑选 Worker 组建团队 | PM |
| **progress-report** | 进度汇报 Skill，用于 PM 向 GM 汇报任务进度 | PM |
| **quality-check** | 质量检查 Skill，用于 PM 验收工作产出 | PM |
| **security-scan** | 安全扫描 Skill，提供代码安全和配置审计能力 | Security |
| **writing-workflow** | 写作工作流 Skill，编排写作任务的完整流程 | Workflow |
| **qveris** | QVeris 金融数据接入，10,000+ 工具统一调用，支持市场数据和风险评估 | Finance |

## Categories

| Category | Skills | Count |
|----------|--------|-------|
| **Communication** | alpha-bridge | 1 |
| **System** | blackboard, error-escalation, git-operations | 3 |
| **Workflow** | coding-workflow, writing-workflow | 2 |
| **Command** | gm-task-evaluate | 1 |
| **Agent** | openclaw-agents | 1 |
| **PM** | pm-team-assemble, progress-report, quality-check | 3 |
| **Security** | security-scan | 1 |
| **Finance** | qveris | 1 |

## Directory Structure

```
clawos/skills/
├── MANIFEST.md              # This file
├── alpha-bridge/            # 本地 ↔ Alpha 系统通信
│   └── SKILL.md
├── blackboard/
│   └── SKILL.md
├── coding-workflow/
│   └── SKILL.md
├── error-escalation/
│   └── SKILL.md
├── git-operations/
│   └── SKILL.md
├── gm-task-evaluate/
│   └── SKILL.md
├── openclaw-agents/
│   ├── SKILL.md
│   ├── agent-factory.js
│   ├── agent-monitor.js
│   ├── agent-router.js
│   ├── config.json
│   ├── context-manager.js
│   ├── index.js
│   └── task-dispatcher.js
├── pm-team-assemble/
│   └── SKILL.md
├── progress-report/
│   └── SKILL.md
├── quality-check/
│   └── SKILL.md
├── qveris/                  # QVeris 金融数据接入
│   └── SKILL.md
├── security-scan/
│   └── SKILL.md
└── writing-workflow/
    └── SKILL.md
```

## 架构说明

### Alpha 系统分离

Alpha 量化交易系统现在是**完全独立**运行在 Codespace 上的系统：

| 系统 | 运行位置 | Skills |
|------|----------|--------|
| **Local ClawOS** | 本地 Mac | 本地 12 个 Skills |
| **Alpha ClawOS** | Codespace | alpha-backtest, alpha-data, git-operations (独立) |

**本地与 Alpha 的通信**：通过 `alpha-bridge` Agent/Skill 使用 `gh codespace ssh` 命令。

## Changelog

| Date | Action | Details |
|------|--------|---------|
| 2026-02-24 | REFACTOR | Alpha 系统分离：删除本地 alpha-* souls/skills，添加 alpha-bridge |
| 2026-02-24 | CREATE | Added `git-operations` skill for github-ops Agent |
| 2026-02-24 | CREATE | Added `security-scan` skill for securityagent Agent |
| 2026-02-24 | MERGE | Merged `blackboard-read` + `blackboard-write` into unified `blackboard` skill |
| 2026-02-24 | MERGE | Merged `skills/openclaw-agents/` into `clawos/skills/openclaw-agents/` |
| 2026-02-24 | CLEANUP | Removed empty `skills/` directory |
| 2026-02-24 | CREATE | Created this MANIFEST.md |
| 2026-02-27 | CREATE | Added `qveris` skill for QVeris financial data integration |
| 2026-02-27 | ADD | Added Finance category for financial data skills |
