# ClawOS × OpenClaw 文件索引

**最后更新**: 2026-02-25
**版本**: 1.1.0

---

## 📁 目录结构

```
~/.openclaw/clawos/
├── workspace/           # 主工作区
│   ├── architecture/    # 架构文档
│   ├── protocols/       # 协议规范
│   ├── reports/         # 测试报告
│   ├── missions/        # 任务管理
│   └── memory/          # 记忆系统
│
├── clawos/              # ClawOS 核心
│   ├── souls/           # Agent 人格
│   ├── skills/          # 技能库
│   ├── workflows/       # 工作流
│   ├── registry/        # 注册表
│   └── runtime/         # 运行时数据
│
└── projects/            # 项目代码

~/.openclaw/             # OpenClaw 系统
├── config.json          # 唯一主配置
├── agents/              # Agent 实例
├── memory/              # 向量记忆
└── logs/                # 系统日志
```

---

## 📋 核心文件索引

### 1. 系统配置

| 文件 | 路径 | 说明 |
|------|------|------|
| 主配置 | `~/.openclaw/config.json` | OpenClaw 唯一配置 |
| Agent 注册 | `~/.openclaw/clawos/clawos/registry/agents.json` | ClawOS Agent 清单 |
| 备份 | `~/.openclaw/backup-2026-02-23/` | 历史配置备份 |

### 2. 架构文档

| 文件 | 位置 | 说明 |
|------|------|------|
| ClawOS 架构 V1.1 | `workspace/architecture/CLAWOS_ARCHITECTURE_V1.1_REFINED.md` | 最新架构 |
| 融合报告 | `workspace/architecture/FUSION_COMPLETE_REPORT.md` | 融合状态 |
| 技术规范 | `workspace/architecture/CLAWOS_TECHNICAL_SPEC.md` | 技术细节 |
| 快速启动 | `workspace/architecture/CLAWOS_QUICKSTART.md` | 入门指南 |

### 3. 协议规范

| 文件 | 位置 | 说明 |
|------|------|------|
| 7.7 角色宪章 | `workspace/protocols/CHARTER_7.7_ROLES.md` | 核心规则 |
| GM 执行 SLA | `workspace/protocols/GM_EXECUTION_SLA.md` | 执行标准 |
| 零执行策略 | `workspace/protocols/HENRY_ZERO_EXECUTION_POLICY.md` | Assistant 规则 |
| 自动交付 | `workspace/protocols/AUTONOMOUS_DELIVERY_PROTOCOL.md` | 交付流程 |

### 4. 报告文档

| 文件 | 位置 | 说明 |
|------|------|------|
| 端到端测试 | `workspace/reports/E2E_TEST_REPORT.md` | 测试报告 |
| 验收报告 | `workspace/reports/ACCEPTANCE_REPORT_7.7_MIGRATION.md` | 迁移验收 |
| 完成证书 | `workspace/reports/CERTIFICATE_OF_DONE.md` | 完成证明 |

### 5. Agent 人格

| Agent | SOUL 文件 | 说明 |
|-------|-----------|------|
| Assistant | `clawos/souls/assistant/SOUL.md` | 人机交互入口 |
| GM | `clawos/souls/gm/SOUL.md` | 决策中枢 |
| Platform-PM | `clawos/souls/platform-pm/SOUL.md` | 平台管理 |

### 6. 技能库

| Skill | 位置 | 说明 |
|-------|------|------|
| 任务评估 | `clawos/skills/gm-task-evaluate/` | GM 评估任务 |
| 团队组建 | `clawos/skills/pm-team-assemble/` | PM 组建团队 |

### 7. 工作流

| 工作流 | 文件 | 说明 |
|--------|------|------|
| 写书流程 | `clawos/workflows/write-book.lobster.ts` | 完整创作流水线 |

### 8. 记忆系统

| 类型 | 位置 | 说明 |
|------|------|------|
| 主记忆 | `workspace/MEMORY.md` | 长期记忆 |
| 每日日志 | `workspace/memory/daily/` | 每日记录 |
| 决策记录 | `workspace/memory/decisions/` | 重要决策 |

---

## 🔍 快速查找

### 按用途查找

**我想了解...**

- **系统架构** → `workspace/architecture/CLAWOS_ARCHITECTURE_V1.1_REFINED.md`
- **如何使用** → `workspace/architecture/CLAWOS_QUICKSTART.md`
- **角色分工** → `workspace/protocols/CHARTER_7.7_ROLES.md`
- **执行标准** → `workspace/protocols/GM_EXECUTION_SLA.md`
- **测试状态** → `workspace/reports/E2E_TEST_REPORT.md`
- **Agent 配置** → `~/.openclaw/config.json`
- **Agent 人格** → `clawos/souls/*/SOUL.md`

### 按角色查找

**我是...**

- **Boss** → 只需要和 Assistant 对话
- **Assistant** → `workspace/protocols/HENRY_ZERO_EXECUTION_POLICY.md`
- **GM** → `workspace/protocols/CHARTER_7.7_ROLES.md`
- **PM** → `clawos/skills/pm-team-assemble/SKILL.md`
- **Worker** → 查看 Registry 中的 Agent 定义

---

## 📊 统计信息

| 类别 | 数量 | 位置 |
|------|------|------|
| 架构文档 | 6 | `workspace/architecture/` |
| 协议文档 | 9 | `workspace/protocols/` |
| 测试报告 | 4 | `workspace/reports/` |
| Agent | 16 | `clawos/openclaw.json` |
| SOUL 文件 | 16 | `clawos/souls/` |
| Skills | 13 | `clawos/skills/` |
| 工作流 | 5 | `clawos/workflows/` |

---

## 🚀 快速命令

```bash
# 查看主配置
cat ~/.openclaw/config.json | jq .

# 查看 Agent 列表
openclaw agents list

# 查看系统状态
openclaw status

# 查看架构文档
cat ~/.openclaw/clawos/workspace/architecture/CLAWOS_ARCHITECTURE_V1.1_REFINED.md

# 查看协议
cat ~/.openclaw/clawos/workspace/protocols/CHARTER_7.7_ROLES.md

# 查看测试报告
cat ~/.openclaw/clawos/workspace/reports/E2E_TEST_REPORT.md

# 访问 Webchat
open http://127.0.0.1:18789
```

---

## 🔄 维护指南

### 每日维护

1. 记录到 `workspace/memory/daily/YYYY-MM-DD.md`
2. 清理临时文件
3. 更新任务状态

### 每周维护

1. 归档完成的任务到 `missions/completed/`
2. 更新 MEMORY.md
3. 清理过时文档

### 每月维护

1. 回顾系统架构
2. 优化配置
3. 更新文档

---

## 📝 变更日志

| 日期 | 变更 | 说明 |
|------|------|------|
| 2026-02-25 | 记忆系统修复 | 创建 MEMORY.md，更新统计 |
| 2026-02-24 | 统一规范 | 整理目录，统一配置 |
| 2026-02-23 | 融合配置 | OpenClaw + ClawOS 融合 |
| 2026-02-23 | 初始化 | ClawOS 基础架构 |

---

**维护者**: GM Agent
**联系方式**: 通过 webchat 发送消息
