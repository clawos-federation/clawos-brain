# SOUL 文件精简指南

**目标**: 将 SOUL 文件从 5k 压缩到 2k tokens
**原则**: 保留核心，删除冗余

---

## 精简原则

### 1. 用表格代替长文本

**之前** (200 tokens):
```markdown
## 核心职责

你是 GM，你的职责是：
1. 评估任务 - 判断任务可行性
2. 任命 PM - 选择合适的 PM
3. 最终验收 - 委托 validator 验收
4. 冲突仲裁 - 当 PM 间有冲突时仲裁
```

**之后** (50 tokens):
```markdown
## 核心职责

| 职责 | 描述 |
|------|------|
| 评估 | 判断可行性 |
| 任命 | 选择 PM |
| 验收 | 委托 validator |
| 仲裁 | PM 冲突处理 |
```

**节省**: 150 tokens (75%)

### 2. 合并重复内容

**之前** (300 tokens):
```markdown
## 🚫 禁止行为

- ❌ 不要读取原始文件
- ❌ 不要执行任务
- ❌ 不要联系 Worker

## ✅ 必须行为

- ✅ 只读 summary.md
- ✅ 指派 PM
- ✅ 输出简洁
```

**之后** (100 tokens):
```markdown
## 行为规则

| 允许 | 禁止 |
|------|------|
| 读 summary.md | 读原始文件 |
| 指派 PM | 执行任务 |
| 输出 <2k | 联系 Worker |
```

**节省**: 200 tokens (67%)

### 3. 删除示例和模板

**之前** (500 tokens):
```markdown
## 输出格式

### 任务评估

```json
{
  "taskId": "task-xxx",
  "evaluation": {
    "feasibility": 8,
    "complexity": "medium",
    ...
  }
}
```

### 验收请求

```json
{
  "taskId": "task-xxx",
  ...
}
```
```

**之后** (50 tokens):
```markdown
## 输出格式

见: templates/gm-output-templates.md
```

**节省**: 450 tokens (90%)

### 4. 使用链接代替内容

**之前** (200 tokens):
```markdown
## 工作流程

1. 收到任务
2. 评估任务（1分钟内）
3. 任命 PM
4. 等待汇报
5. 验收
6. 通知

详细流程：
[详细描述每一步...]
```

**之后** (50 tokens):
```markdown
## 工作流程

见: workflows/gm-workflow.md
```

**节省**: 150 tokens (75%)

---

## GM SOUL 精简示例

### 当前版本 (5k tokens)

```markdown
# SOUL.md - ClawOS GM Agent

你是 ClawOS 的 GM...

[大量详细描述]
[示例]
[模板]
[完整流程]
```

### 精简版本 (2k tokens)

```markdown
# SOUL.md - ClawOS GM (精简版)

你是 GM，全局决策中枢（Opus）。

## 🚨 Opus 铁律

| 限制 | 值 |
|------|-----|
| 输入 | <5k |
| 输出 | <2k |
| 只读 | summary.md |

## 核心职责

| 职责 | 动作 |
|------|------|
| 评估 | 判断可行性 |
| 任命 | 选择 PM |
| 验收 | 委托 validator |

## 行为规则

| 允许 | 禁止 |
|------|------|
| 读 summary.md | 读原始文件 |
| 指派 PM | 执行任务 |
| 输出简洁 | 联系 Worker |

## 模板

见: templates/gm-templates.md
```

**节省**: 3k tokens (60%)

---

## 精简清单

### GM SOUL

- [ ] 用表格替代长文本（-1k）
- [ ] 删除示例和模板（-1k）
- [ ] 合并重复内容（-0.5k）
- [ ] 使用链接（-0.5k）
- [ ] **目标**: 5k → 2k ✅

### validator SOUL

- [ ] 用表格替代长文本（-0.5k）
- [ ] 删除示例（-0.5k）
- [ ] **目标**: 3k → 1.5k ✅

### assistant SOUL

- [ ] 用表格替代长文本（-0.5k）
- [ ] 删除示例（-0.5k）
- [ ] **目标**: 4k → 2k ✅

### PM SOUL

- [ ] 统一格式（-0.3k 每个）
- [ ] **目标**: 3k → 2k ✅

---

## 实施步骤

### Step 1: 备份原文件

```bash
cp -r ~/openclaw-system/clawos/souls ~/openclaw-system/clawos/souls.backup
```

### Step 2: 精简 GM SOUL

```bash
# 编辑
vim ~/openclaw-system/clawos/souls/command/gm.soul.md

# 验证 tokens
wc -w ~/openclaw-system/clawos/souls/command/gm.soul.md
```

### Step 3: 测试

```bash
# 重启 OpenClaw
openclaw gateway restart

# 测试 GM
openclaw agent run gm --task "测试任务"
```

### Step 4: 验证

```bash
# 检查 token 消耗
openclaw stats tokens | grep gm
```

---

## 预期效果

### Token 节省

| 角色 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| GM | 5k | 2k | 60% |
| validator | 3k | 1.5k | 50% |
| assistant | 4k | 2k | 50% |
| PM (每个) | 3k | 2k | 33% |

### 成本节省

| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| GM 启动 | $0.075 | $0.03 | 60% |
| GM 任务 | $0.075 | $0.03 | 60% |
| **每次调用** | **$0.15** | **$0.06** | **60%** |

---

## 注意事项

### 1. 不要删除核心规则

**保留**：
- Opus 铁律
- 核心职责
- 行为规则

**可删**：
- 示例
- 模板
- 详细流程

### 2. 使用外部文档

将详细内容移到：
- `templates/` - 模板文件
- `workflows/` - 工作流文档
- `docs/` - 详细文档

### 3. 保持可读性

精简不是压缩，而是：
- 用更少的字说清楚
- 用表格代替列表
- 用链接代替重复

---

**创建时间**: 2026-02-26 10:05
**状态**: ⏳ 待实施
