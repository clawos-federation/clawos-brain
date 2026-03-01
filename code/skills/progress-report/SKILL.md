---
name: progress-report
description: 进度汇报 Skill，用于 PM 向 GM 汇报任务进度
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: []
      env: []
---

# 进度汇报 Skill

用于 PM 定期向 GM 汇报任务进度，确保信息透明。

## 汇报频率

| 情况 | 频率 |
|------|------|
| 正常执行 | 每小时一次 |
| 遇到问题 | 立即汇报 |
| 里程碑完成 | 立即汇报 |
| 任务完成 | 立即汇报 |

## 汇报内容

| 字段 | 说明 |
|------|------|
| taskId | 任务ID |
| status | 当前状态 |
| percent | 完成百分比 |
| currentStep | 当前步骤 |
| completedSteps | 已完成步骤列表 |
| blockedBy | 阻塞问题（如有） |
| estimatedTimeRemaining | 预计剩余时间 |
| issues | 需要关注的问题 |

## 输出格式

```json
{
  "taskId": "{{taskId}}",
  "timestamp": "2026-02-24T08:00:00Z",
  "status": "running|blocked|completed|failed",
  "progress": {
    "percent": 65,
    "currentStep": "编写第3章",
    "completedSteps": ["大纲", "第1章", "第2章"],
    "totalSteps": 5
  },
  "timing": {
    "startedAt": "2026-02-24T06:00:00Z",
    "elapsedMinutes": 120,
    "estimatedRemainingMinutes": 60
  },
  "resources": {
    "llmCalls": 45,
    "tokensUsed": 125000
  },
  "issues": [],
  "nextUpdate": "2026-02-24T09:00:00Z"
}
```

## 汇报模板

### 正常进度
```
📊 任务进度汇报

任务：【{{taskName}}】
状态：执行中
进度：{{percent}}%

已完成：
- {{completedSteps}}

当前：{{currentStep}}

预计剩余：{{estimatedRemainingMinutes}} 分钟
```

### 遇到阻塞
```
⚠️ 任务阻塞汇报

任务：【{{taskName}}】
阻塞原因：{{blockedBy}}

当前进度：{{percent}}%
已尝试：{{attempted}}
需要支持：{{needHelp}}

等待指示。
```

### 任务完成
```
✅ 任务完成汇报

任务：【{{taskName}}】
完成时间：{{completedAt}}

产出物：
- {{artifacts}}

资源消耗：
- LLM 调用：{{llmCalls}} 次
- Token 使用：{{tokensUsed}}

请验收。
```
