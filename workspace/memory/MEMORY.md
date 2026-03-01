# MEMORY.md - ClawOS 长期记忆

> **最后更新**: 2026-02-25
> **版本**: 1.0.0

---

## 系统概览

ClawOS 是基于 OpenClaw 的 16 Agents 三层架构 AI 操作系统。

### 架构

```
Command Layer (4): assistant → gm ← validator
                          alpha-bridge
       ↓
PM Layer (3): platform-pm | coding-pm | writing-pm
       ↓
Workers (9): 开发组(3) | 写作组(3) | 系统组(3)
```

### 模型分层

| Tier | 模型 | Agent |
|------|------|-------|
| TITAN | opus-4-6-thinking | gm, validator |
| HARDCORE | gpt-5.3-codex | 开发组, 系统组 |
| ECO | glm-5 | assistant, PMs, 写作组 |

---

## 重要决策记录

### 2026-02-24: Phase 1 完成

- 完成三层架构实施
- Blackboard 共享黑板系统
- 5 个 Lobster 工作流
- HEARTBEAT 通知机制
- Per-user Assistant 模板

### 2026-02-23: OpenClaw + ClawOS 融合

- 统一配置到 clawos/openclaw.json
- 15 → 16 Agents (新增 alpha-bridge)
- 模型分层体系确立

---

## 项目状态

| 组件 | 状态 | 版本 |
|------|------|------|
| Agent 架构 | ✅ 完成 | 16 Agents |
| Blackboard | ✅ 完成 | v2.0 |
| Lobster 工作流 | ✅ 完成 | 5 工作流 |
| HEARTBEAT | ✅ 完成 | v1.0 |
| SOUL 文件 | ✅ 完成 | 16/16 |
| 记忆系统 | ✅ 完成 | v1.0 |

---

## 关键文件路径

| 文件 | 路径 |
|------|------|
| 主协议 | `CLAUDE.md` |
| Agent 配置 | `clawos/openclaw.json` |
| Agent 注册表 | `workspace/agents/registry.json` |
| SOUL 文件 | `clawos/souls/*/SOUL.md` |
| 技能库 | `clawos/skills/*/SKILL.md` |
| 工作流 | `clawos/workflows/*.lobster.yaml` |
| Blackboard | `clawos/blackboard/` |

---

## 待办事项

- [ ] openclaw CLI 集成
- [ ] 工作流引擎运行时
- [ ] 监控仪表板
- [ ] 多用户支持

---

## 联系方式

通过 GM Agent 或 Assistant 进行系统交互。
