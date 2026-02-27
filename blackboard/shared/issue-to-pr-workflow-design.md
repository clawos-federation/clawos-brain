# Issue → Agent → PR 工作流设计

**时间**: 2026-02-27 10:08
**状态**: 设计中

---

## 工作流概述

```
用户创建 Issue
    ↓
GitHub Webhook → ClawOS
    ↓
分析 Issue 类型
    ↓
分配给合适的 Agent
    ↓
Agent 执行任务
    ↓
创建 PR 提交结果
    ↓
Actions 自动验证
    ↓
合并或等待审核
```

---

## 架构设计

### 方案 A: GitHub Webhook + 本地服务（推荐）

```
GitHub Issue → Webhook → ClawOS Gateway → 分发 Agent
                              ↓
                          执行任务
                              ↓
                          gh pr create
```

**优点**: 实时响应
**缺点**: 需要公网 IP 或 Tailscale

### 方案 B: 轮询模式

```
定时任务 (每 5 分钟)
    ↓
gh issue list --state open
    ↓
分析未处理 Issue
    ↓
执行任务
```

**优点**: 简单可靠
**缺点**: 有延迟

### 方案 C: GitHub Actions 触发

```
Issue 创建 → Actions 触发 → 调用 ClawOS API
```

**优点**: 完全在 GitHub 上
**缺点**: 需要 ClawOS 暴露 API

---

## 实施方案: 混合模式

1. **主流程**: 轮询模式（简单可靠）
2. **加速**: Webhook（可选）
3. **备份**: Actions（失败重试）

---

## 角色映射

| Label | Agent | 说明 |
|-------|-------|------|
| `bug` | coding-pm | Bug 修复 |
| `feature` | coding-pm | 新功能 |
| `docs` | writing-pm | 文档更新 |
| `research` | research-pm | 调研任务 |
| `question` | assistant | 问题回答 |

---

## 执行步骤

### Step 1: Issue 分析

```python
def analyze_issue(issue):
    # 提取标题、内容、labels
    # 判断任务类型
    # 估算复杂度
    # 返回 agent_id 和 task
```

### Step 2: 任务分配

```python
def assign_to_agent(agent_id, task):
    # 调用 sessions_spawn
    # 等待结果
    # 返回执行结果
```

### Step 3: 创建 PR

```bash
# 创建分支
git checkout -b issue-{issue_number}

# 提交更改
git add .
git commit -m "fix: resolve issue #{issue_number}"

# 创建 PR
gh pr create --title "Resolve #${issue_number}" --body "..."
```

---

## 文件结构

```
~/clawos/scripts/
├── issue-processor.sh      # 主脚本
├── analyze-issue.py        # Issue 分析
├── create-pr.sh            # 创建 PR
└── issue-workflow.cron     # 定时任务
```

---

## 安全考虑

1. **只处理特定 Label 的 Issue**
2. **需要 @clawos-bot 触发**
3. **限制执行时间**
4. **敏感操作需要人工确认**

---

## 测试计划

1. 创建测试 Issue
2. 添加 `clawos` label
3. 等待处理
4. 验证 PR 创建

---

🦞 ClawOS
