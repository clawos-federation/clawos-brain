---
name: gm-task-evaluate
description: 评估一个任务的可行性、所需资源和风险
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [node]
      env: []
---

# 任务评估 Skill

你收到一个新任务时，按以下框架评估：

## 评估维度

1. **可行性**（1-10分）：当前资源能否完成？
2. **复杂度**（low/medium/high/critical）：技术难度
3. **资源需求**：需要哪类 Agent、预计 LLM 调用次数
4. **风险点**：什么地方最可能失败？
5. **时间估算**：预计完成时间

## 任务类型识别

| 关键词 | 类型 | 推荐PM |
|--------|------|--------|
| 写、文章、书、博客 | writing | writing-pm |
| 开发、代码、API、网站 | coding | coding-pm |
| 调研、研究、分析 | research | research-pm |
| 设计、UI、图表 | design | design-pm |

## 输出格式

```json
{
  "taskId": "{{taskId}}",
  "type": "writing|coding|research|design",
  "feasibility": 8,
  "complexity": "medium",
  "requiredAgents": ["writer", "researcher"],
  "estimatedLLMCalls": 50,
  "risks": ["可能的风险"],
  "estimatedHours": 4,
  "recommendation": "approve|reject|clarify",
  "reason": "推荐原因"
}
```

## 评估示例

### 输入
```
任务：帮我写一篇关于 OpenClaw 的技术博客，3000字左右
```

### 输出
```json
{
  "taskId": "task-001",
  "type": "writing",
  "feasibility": 9,
  "complexity": "low",
  "requiredAgents": ["writer", "researcher"],
  "estimatedLLMCalls": 30,
  "risks": [],
  "estimatedHours": 2,
  "recommendation": "approve",
  "reason": "任务明确，资源充足，风险低"
}
```
