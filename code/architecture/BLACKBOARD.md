# ClawOS Blackboard 结构设计

**版本**: 2.0.0

---

## 混合存储架构

```
本地存储 (~/clawos/blackboard/)
    ↓ 同步
Cloudflare R2 (跨节点共享)
    ↓ 持久化
GitHub memory分支 (永久归档)
```

---

## 目录结构

```
~/clawos/blackboard/
│
├── tasks/{taskId}/                    # 任务目录
│   ├── task.json                      # 任务定义
│   ├── team-composition.json          # PM选角决策
│   ├── status.md                      # 实时进度
│   ├── result.json                    # 最终产出
│   ├── validation.json                # Validator评分
│   ├── memory-harvest.json            # 记忆提炼摘要
│   └── escalations/                   # 升级请求（如有）
│
├── gm/                                # GM专属
│   ├── decisions.md                   # 决策日志
│   ├── pm-performance.json            # PM历史表现
│   └── arbitrations.md                # 仲裁记录
│
├── roles/                             # 角色实例状态
│   ├── active.json                    # 当前活跃实例
│   │   {
│   │     "instances": [
│   │       {
│   │         "id": "inst-xxx",
│   │         "role": "analyst-code",
│   │         "taskId": "task-xxx",
│   │         "startedAt": "...",
│   │         "status": "running"
│   │       }
│   │     ]
│   │   }
│   │
│   └── memory-queue.json              # 待归还记忆队列
│       {
│         "queue": [
│           {
│             "taskId": "task-xxx",
│             "roleId": "analyst-code",
│             "status": "pending",
│             "enqueuedAt": "..."
│           }
│         ]
│       }
│
├── escalations/                       # 紧急上报
│   └── {timestamp}.json
│       {
│         "level": "critical|high|normal",
│         "from": "agent-id",
│         "issue": "...",
│         "suggestedAction": "...",
│         "requiresHumanApproval": true
│       }
│
├── shared/                            # 跨节点共享
│   ├── risk-limits.json               # 风控规则（只有人能修改）
│   ├── node-status.json               # 各节点状态
│   └── knowledge-sync.json            # 知识同步状态
│
├── harvest/                           # 知识收割
│   ├── daily/                         # 每日收割结果
│   │   └── {date}.json
│   └── weekly/                        # 每周精华
│       └── {week}.json
│
└── reports/                           # 进化报告
    ├── daily/{date}.md
    ├── weekly/{week}.md
    └── monthly/{month}.md
```

---

## 文件格式

### task.json

```json
{
  "taskId": "task-20260225-001",
  "type": "coding|writing|research|quant",
  "description": "任务描述",
  "priority": "high|normal|low",
  "createdBy": "assistant",
  "createdAt": "2026-02-25T19:00:00+08:00",
  "deadline": "2026-02-25T21:00:00+08:00",
  "assignedPM": "coding-pm",
  "status": "pending|running|completed|failed",
  "context": {
    "source": "telegram|claude-code",
    "userId": "user-id",
    "channelId": "channel-id"
  }
}
```

### team-composition.json

```json
{
  "taskId": "task-xxx",
  "pmDecision": {
    "pmId": "coding-pm",
    "decidedAt": "...",
    "reasoning": "..."
  },
  "team": [
    {
      "role": "analyst-code",
      "reason": "需要分析现有架构",
      "priority": 1,
      "memoryLoaded": true,
      "instanceId": "inst-xxx"
    },
    {
      "role": "creator-code",
      "reason": "需要实现新功能",
      "priority": 2,
      "memoryLoaded": true,
      "instanceId": "inst-yyy"
    }
  ],
  "workflow": "coding-task",
  "estimatedTime": "2h"
}
```

### validation.json

```json
{
  "taskId": "task-xxx",
  "validatorId": "validator",
  "validatedAt": "...",
  "iterations": 1,
  "result": {
    "score": 8.5,
    "pass": true,
    "criteria": {
      "correctness": 9.0,
      "completeness": 8.5,
      "quality": 8.0,
      "standards": 8.5
    },
    "issues": [
      {
        "severity": "minor",
        "description": "...",
        "location": "file:line"
      }
    ],
    "suggestions": ["..."]
  }
}
```

### memory-harvest.json

```json
{
  "taskId": "task-xxx",
  "harvestedAt": "...",
  "experiences": [
    {
      "roleId": "analyst-code",
      "cells": [
        {
          "type": "success",
          "content": "成功模式描述",
          "value": 0.7
        },
        {
          "type": "insight",
          "content": "洞察内容",
          "value": 0.6
        }
      ]
    }
  ],
  "crossPollinationCandidates": [
    {
      "fromRole": "critic-code",
      "toRole": "critic-writing",
      "pattern": "批判技巧",
      "value": 0.8
    }
  ]
}
```

---

## 同步机制

### 本地 → R2

```python
def sync_to_r2(local_path, r2_bucket):
    """同步本地 Blackboard 到 R2"""
    # 1. 任务完成后立即同步
    # 2. 每5分钟增量同步
    # 3. 使用 R2 S3 兼容 API
    pass
```

### R2 → GitHub

```yaml
# .github/workflows/memory-to-github.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时

jobs:
  sync:
    steps:
      - name: Download from R2
        run: rclone sync r2:clawos-blackboard ./blackboard
        
      - name: Extract memories
        run: python scripts/extract_memories.py
        
      - name: Commit to memory branch
        run: |
          git checkout memory
          git add memory/
          git commit -m "memory: sync from R2"
          git push
```

---

## 访问控制

| 目录 | assistant | gm | validator | platform-pm | PM | Workers |
|------|-----------|-----|-----------|-------------|-----|---------|
| tasks/ | R | RW | R | R | RW | W |
| gm/ | - | RW | - | R | R | - |
| roles/ | - | R | - | RW | R | - |
| escalations/ | R | RW | - | R | W | W |
| shared/ | R | R | R | R | R | R |
| harvest/ | - | R | - | RW | - | - |

---

## 清理策略

```yaml
retention:
  tasks:
    completed: 30 days
    failed: 7 days
    
  harvest:
    daily: 7 days
    weekly: 90 days
    
  reports:
    daily: 30 days
    weekly: 1 year
    monthly: permanent
    
  memory-queue:
    pending: 24 hours
    completed: immediate delete
```

---

**ClawOS Blackboard v2**
