# ClawOS 模型分配 v3

**策略**: 
1. glm-5 大力出奇迹，用足
2. opus 好钢用在刀刃上，关键决策

---

## 分配方案

| 角色 | 模型 | 原因 |
|------|------|------|
| **Command Layer** |||
| assistant | glm-5 | 高频响应，免费 |
| **gm** | **opus** | ⚡ 决策关键，刀刃 |
| **validator** | **opus** | ⚡ 质检关键，刀刃 |
| platform-pm | glm-5 | 后台任务 |
| **PM Layer** |||
| coding-pm | glm-5 | 编排任务 |
| writing-pm | glm-5 | 编排任务 |
| research-pm | glm-5 | 编排任务 |
| **Worker Layer** |||
| analyst-* | glm-5 | 分析任务 |
| creator-code | codex | 代码编写 |
| creator-frontend | codex | 代码编写 |
| creator-backend | codex | 代码编写 |
| **creator-writing** | **opus** | ⚡ 写作质量，刀刃 |
| critic-code | codex | 代码审查 |
| critic-writing | glm-5 | 通用审查 |
| **critic-risk** | **opus** | ⚡ 风险判断，刀刃 |
| executor-* | glm-5 | 执行任务 |
| connector-* | glm-5 | 整合任务 |

---

## 刀刃角色 (用 opus)

1. **gm** - 全局决策，决定系统效率
2. **validator** - 独立质检，保证输出质量
3. **critic-risk** - 风险判断，保护资产
4. **creator-writing** - 重要写作，质量关键

## 大力角色 (用 glm-5)

- assistant - 高频
- 所有 PM - 编排
- 所有 Analyst - 分析
- 所有 Executor - 执行
- 所有 Connector - 整合
- 部分 Critic - 通用审查

## 代码角色 (用 codex)

- coder-*
- critic-code

---

## 成本估算

| 模型 | 使用频率 | 月成本 |
|------|----------|--------|
| glm-5 | 90%+ | $0 |
| opus | ~5% | ~$10-20 |
| codex | ~5% | ~$5-10 |

**总计: ~$15-30/月**
