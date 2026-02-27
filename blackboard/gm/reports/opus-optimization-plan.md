# Opus 使用优化方案

**时间**: 2026-02-26 08:35
**优先级**: critical
**目标**: 让 Opus 只用在刀刃上

---

## 当前 Opus 使用情况

| 角色 | 模型 | 理由 | 合理性 |
|------|------|------|--------|
| GM | opus | 决策中枢 | ✅ 合理 |
| validator | opus | 质检验收 | ✅ 合理 |
| creator-writing | opus | 高质量写作 | 🤔 需评估 |
| critic-risk | opus | 风险判断 | ✅ 合理 |

---

## 问题诊断

### GM 问题

| 指标 | 目标 | 当前 | 差距 |
|------|------|------|------|
| 输入 tokens | <5k | 45k | 9x |
| 读取内容 | summary.md | summary.md + 其他文件 | - |
| 响应时间 | <30s | 32s | 接近 |

**根本原因**：GM 还是读了太多文件，没有严格遵守"只看摘要"。

---

## 优化方案

### 1. GM 严格限制（最高优先级）

**修改 GM SOUL，添加硬性规则**：

```markdown
## 🚨 Opus 使用铁律

**GM 是 Opus，必须极其惜用。**

### 硬性限制

| 限制 | 值 | 原因 |
|------|-----|------|
| 单次输入 | <5k tokens | Opus 很贵 |
| 禁止读取 | 所有原始文件 | 让 PM 读 |
| 只能读取 | summary.md + decisions.md | 决策必需 |
| 单次决策时间 | <30s | 效率要求 |

### 工作流（严格遵守）

```
1. 收到任务
   ↓
2. 指派 PM（不读任何文件）
   ↓
3. PM 返回摘要（<5k tokens）
   ↓
4. 基于摘要做决策
   ↓
5. 输出决策（<2k tokens）
```

### 禁止行为

- ❌ 读取 blackboard/tasks/*/*（原始文件）
- ❌ 读取 memory/*.md（长记忆）
- ❌ 读取 logs/*（日志文件）
- ❌ 执行任何需要 >5k tokens 输入的决策

### 必须行为

- ✅ 只读 summary.md
- ✅ 需要更多信息？指派 research-pm
- ✅ 决策后立即输出，不拖延
```

### 2. research-pm 输出规范

**强制 research-pm 返回格式**：

```markdown
# 信息收集报告（供 GM 决策）

**总长度**: <5k tokens

## 任务
{一句话}

## 核心发现（3-5 点）
- {发现1}
- {发现2}

## 数据摘要（表格形式）
| 指标 | 值 |
|------|-----|

## 建议（2-3 条）
1. {建议1}

---
**完整报告**: /path/to/full/report.md（GM 不需要看）
```

### 3. 其他 Opus 角色评估

| 角色 | 评估 | 建议 |
|------|------|------|
| validator | ✅ 保留 | 质检需要高智商 |
| creator-writing | 🤔 待定 | 普通写作用 glm-5，关键内容才用 opus |
| critic-risk | ✅ 保留 | 风险判断需要慎重 |

**creator-writing 优化**：
```json
{
  "creator-writing-default": "zai/glm-5",
  "creator-writing-critical": "vectorengine-claude/claude-opus-4-6-thinking"
}
```

规则：
- 普通内容（邮件、文档）：glm-5
- 关键内容（对外公告、重要文案）：opus

---

## 实施步骤

### Phase 1: GM SOUL 强化（立即）
- [ ] 添加"Opus 使用铁律"到 GM SOUL
- [ ] 添加 token 限制规则
- [ ] 添加禁止行为清单

### Phase 2: research-pm 输出规范（立即）
- [ ] 更新 research-pm SOUL，添加输出格式
- [ ] 强制 <5k tokens 限制

### Phase 3: 模型分配优化（评估）
- [ ] 评估 creator-writing 使用场景
- [ ] 实现动态模型选择

### Phase 4: 监控（长期）
- [ ] 每次 GM 调用记录 token 消耗
- [ ] 超过 5k 触发告警

---

## 预期效果

| 指标 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| GM 单次 tokens | 45k | <5k | 9x |
| GM 成本/次 | ~$0.50 | ~$0.05 | 10x |
| 响应时间 | 32s | <20s | 1.6x |

---

**Status**: 🚀 Ready for Immediate Implementation
