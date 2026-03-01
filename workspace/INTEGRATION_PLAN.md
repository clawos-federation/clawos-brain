# OpenClaw × ClawOS 整合方案

> 保留你的优化成果 + 引入 ClawOS 组织层

---

## 📊 现状分析

### OpenClaw 原版优化（你的成果）

**核心架构**：Orchestration 7.7
- Henry (L1/L2): 接待、沟通、协调
- GM (L3): 统筹、决策、审批
- 专业 Agents: DevAgent, TestAgent, ResearchAgent, LegalAgent

**模型配置**：
- Eco: zai/glm-5
- Titan: openai-codex/gpt-5.3-codex
- 辅助: gemini-3-flash, claude-sonnet-4-5

**优化文档**：20+ 文件
- CHARTER_7.7_ROLES.md
- HENRY_GM_CANONICAL_RULES.md
- GM_EXECUTION_SLA.md
- ...

### ClawOS 新版

**核心架构**：Agent 自治操作系统
- Assistant: 唯一人机入口
- GM: 决策中枢
- Platform PM: 能力维护
- Writing PM / Coding PM: 项目管理

**特色**：
- SOUL.md 人格定义
- Skills 体系
- Agent Registry
- Lobster 工作流

---

## 🎯 整合策略

### 保留（OpenClaw 原版）
1. ✅ 专业 Agents（devagent, testagent, researchagent, legalagent）
2. ✅ 多模型配置
3. ✅ OAuth 认证
4. ✅ Orchestration 7.7 规则
5. ✅ 所有优化文档

### 新增（ClawOS）
1. ✅ Assistant 作为统一入口
2. ✅ Platform PM / Writing PM / Coding PM
3. ✅ SOUL.md + Skills + Registry

### 架构

```
用户
  │
  ▼
Assistant (新入口)
  │
  ▼
GM (决策中枢)
  │
  ├── Writing PM ──→ ResearchAgent
  │
  ├── Coding PM ──→ DevAgent → TestAgent
  │
  └── Platform PM ──→ 维护 Skills/Registry
  
Henry (保留，可选入口)
```

---

## 📁 文件对照

| 功能 | OpenClaw 原版 | 整合后 |
|------|--------------|--------|
| 入口 | Henry | Assistant (+ Henry 保留) |
| 决策 | GM | GM (不变) |
| PM 层 | 无 | Writing PM / Coding PM / Platform PM |
| 执行层 | DevAgent/TestAgent/... | 保留 |
| 配置 | openclaw.json | config-unified.json |
| 人格 | workspace/AGENTS.md | souls/*/SOUL.md |

---

## 🚀 部署步骤

### 1. 应用整合配置

```bash
# 备份当前配置
cp ~/.openclaw/config.json ~/.openclaw/config.json.backup

# 应用整合配置
cp ~/.openclaw/clawos/clawos/config-unified.json ~/.openclaw/config.json

# 重启 Gateway
openclaw gateway restart
```

### 2. 验证

```bash
openclaw agents list
# 应该看到: assistant, gm, platform-pm, writing-pm, coding-pm, henry, devagent, testagent, researchagent, legalagent
```

### 3. 测试

```bash
# 通过 iMessage 发送消息
# 或访问 http://localhost:18790
```

---

## ⚠️ 注意事项

1. **Henry 仍然可用**：作为备选入口
2. **专业 Agents 不变**：执行层完全保留
3. **渐进式切换**：可以先用 Assistant，有问题切回 Henry
4. **配置备份**：config.json.backup 可以随时恢复

---

## 📊 对比表

| 维度 | 原版 | 整合版 |
|------|------|--------|
| 入口统一性 | ⚠️ 多入口 | ✅ 单一入口 |
| PM 层 | ❌ 无 | ✅ 完整 |
| 执行层 | ✅ 完整 | ✅ 保留 |
| 模型多样性 | ✅ 4种 | ✅ 保留 |
| 可恢复性 | - | ✅ 随时可切回 |

---

*版本: 3.0*
*创建时间: 2026-02-23 22:50*
