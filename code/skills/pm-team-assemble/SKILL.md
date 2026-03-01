---
name: pm-team-assemble
description: 从 Agent Registry 挑选合适的 Worker 组建团队
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [node, cat, jq]
---

# 团队组建 Skill

PM 使用此 Skill 从 Registry 挑选 Worker 组建项目团队。

## 输入

```json
{
  "taskType": "coding",
  "requirements": {
    "needsFrontend": true,
    "needsBackend": true,
    "needsTest": true,
    "needsGithub": true
  },
  "constraints": {
    "maxTeamSize": 5,
    "minSuccessRate": 0.8
  }
}
```

## 团队角色

| 角色 | 职责 | 默认 Skills |
|------|------|-------------|
| product | 需求分析 | summarize, clarify |
| architect | 架构设计 | design, evaluate |
| frontend | UI 开发 | react, typescript, testing |
| backend | API 开发 | python, api, database |
| test | 测试验证 | pytest, jest, e2e |
| github | 代码提交 | git, pr, release |

## 匹配逻辑

1. 从 `~/clawos/registry/agents.json` 读取 Agent 列表
2. 按 skills 过滤匹配
3. 按 successRate 排序
4. 选择 top-N
5. 检查是否正在执行其他任务
6. 返回可用团队

## 输出

```json
{
  "teamId": "team-xxx",
  "members": [
    {
      "role": "frontend",
      "agentId": "writer-frontend",
      "model": "claude-sonnet-4-6",
      "successRate": 0.92
    },
    {
      "role": "backend",
      "agentId": "coder-backend",
      "model": "claude-sonnet-4-6",
      "successRate": 0.89
    }
  ],
  "estimatedCost": 0.50,
  "estimatedTime": 4
}
```

## 注意事项

- 优先选择 successRate > 0.85 的 Agent
- 同一 Agent 不能同时在多个团队
- 如果找不到合适 Agent，通知 Platform PM
- 团队组建后，写入 `~/clawos/teams/{teamId}.json`
