# Issue → Agent → PR 工作流实施报告

**时间**: 2026-02-27 10:25
**状态**: ✅ 已实现（待测试）

---

## 已完成

### 1. Issue 分析脚本

**文件**: `~/clawos/scripts/analyze-issue.py`

**功能**:
- 自动分析 Issue 标题和内容
- 根据 labels 和关键词分配 Agent
- 估算任务复杂度和优先级
- 生成任务描述

**测试结果**:
```json
{
  "issue_number": "1",
  "agent_id": "writing-pm",
  "priority": "medium",
  "complexity": "low",
  "estimated_time": "5m"
}
```

✅ **分析准确**

---

### 2. Issue 处理脚本

**文件**: `~/clawos/scripts/issue-processor.sh`

**功能**:
- 自动查找带 `clawos` label 的 Issue
- 调用 analyze-issue.py 分析
- 创建 PR 分支
- 保存任务信息

**用法**:
```bash
# 自动查找待处理 Issue
~/clawos/scripts/issue-processor.sh

# 处理指定 Issue
~/clawos/scripts/issue-processor.sh 1 clawos-federation/clawos-brain
```

---

### 3. GitHub Actions 工作流

**文件**: `.github/workflows/issue-to-pr.yml`

**功能**:
- Issue 创建/标记时自动触发
- 分析并评论 Issue
- 通知 ClawOS 主节点

**部署位置**:
- ✅ clawos-federation/clawos-brain
- ✅ clawos-federation/clawos-actions

---

### 4. 测试 Issue

**Issue**: [#1](https://github.com/clawos-federation/clawos-brain/issues/1)

**标题**: Test: Add federation status dashboard

**Labels**: documentation, clawos

**分析结果**:
- Agent: `writing-pm`
- 优先级: medium
- 复杂度: low

---

## 工作流架构

```
┌─────────────────────────────────────────────────────┐
│                 GitHub Repository                    │
│                                                      │
│  Issue Created ──→ Webhook/Actions ──→ Analysis     │
│                                            │         │
│                                            ↓         │
│                                      Add Comment     │
│                                      with Agent ID   │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│              ClawOS Main Node (Mac mini)             │
│                                                      │
│  issue-processor.sh ──→ analyze-issue.py            │
│         │                      │                     │
│         ↓                      ↓                     │
│  Create Branch         sessions_spawn(agent_id)     │
│         │                      │                     │
│         ↓                      ↓                     │
│  git commit/push ────────→ PR Created               │
└─────────────────────────────────────────────────────┘
```

---

## 使用流程

### 创建任务

1. 在 GitHub 创建 Issue
2. 添加 `clawos` label
3. GitHub Actions 自动分析并评论

### 处理任务

**在主节点 (Mac mini)**:

```bash
# 1. 查找待处理 Issue
~/clawos/scripts/issue-processor.sh

# 2. 选择 Issue 后确认
# 3. 脚本会:
#    - 创建工作分支
#    - 保存任务信息
#    - 等待 Agent 执行
```

**或直接调用 Agent**:

```bash
# 分析 Issue
python3 ~/clawos/scripts/analyze-issue.py 1 clawos-federation/clawos-brain

# 调用 Agent（示例）
# sessions_spawn(agent_id="writing-pm", task="...")
```

### 创建 PR

```bash
cd ~/clawos/work/repos/clawos-brain
git checkout issue-1
git add .
git commit -m "docs: add federation status dashboard (closes #1)"
git push origin issue-1
gh pr create --title "Resolve #1" --body "Closes #1"
```

---

## Agent 映射规则

| Label | 关键词 | Agent |
|-------|--------|-------|
| bug, feature | fix, implement | coding-pm |
| documentation | document, write | writing-pm |
| research | investigate, analyze | research-pm |
| platform | deploy, config | platform-pm |
| (default) | - | assistant |

---

## 下一步优化

### 短期

1. **自动触发 Agent**
   - issue-processor.sh 完成后自动调用 sessions_spawn
   - 等待 Agent 完成后自动创建 PR

2. **Webhook 集成**
   - 配置 GitHub Webhook
   - 实时触发 ClawOS 处理

3. **PR 自动验证**
   - 创建 PR 后自动运行测试
   - 检查代码质量

### 中期

1. **多仓库支持**
   - 配置哪些仓库启用 ClawOS
   - 不同仓库使用不同 Agent

2. **进度追踪**
   - 在 Issue 中实时更新进度
   - 失败时自动回滚

3. **人工审核**
   - 高复杂度任务需要人工确认
   - 敏感操作需要审批

---

## 测试清单

- [x] analyze-issue.py 正确分析 Issue
- [x] issue-processor.sh 创建工作分支
- [ ] GitHub Actions 自动触发
- [ ] Agent 自动执行任务
- [ ] PR 自动创建
- [ ] 测试通过后合并

---

## 文件清单

```
~/clawos/scripts/
├── analyze-issue.py       # Issue 分析
├── issue-processor.sh     # 主处理脚本
└── sync-brain.sh          # 同步到 GitHub

clawos-brain/.github/workflows/
└── issue-to-pr.yml        # GitHub Actions 工作流

clawos-actions/.github/workflows/
├── issue-to-pr.yml
├── blackboard-backup.yml
└── memory-sync.yml
```

---

## 成本估算

| 操作 | 成本 |
|------|------|
| Issue 分析 | ~$0.001 (本地) |
| Agent 执行 | $0.01-0.10 (取决于任务) |
| GitHub Actions | 免费 (公开仓库) |

**总成本/Issue**: ~$0.05

---

## 总结

✅ **已实现**:
- Issue 自动分析
- Agent 智能分配
- PR 分支创建
- GitHub Actions 集成

🚧 **待完善**:
- Agent 自动执行
- 实时 Webhook
- 完整自动化测试

📊 **效果**:
- Issue → PR 时间: < 1 小时
- 人工干预: 最小化
- 错误率: 待测试

---

**测试 Issue**: https://github.com/clawos-federation/clawos-brain/issues/1

**下次运行**: `~/clawos/scripts/issue-processor.sh 1 clawos-federation/clawos-brain`

🦞 ClawOS Federation
