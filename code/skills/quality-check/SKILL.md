---
name: quality-check
description: 质量检查 Skill，用于 PM 验收工作产出
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: []
      env: []
---

# 质量检查 Skill

用于 PM 验收 Worker 的产出物，确保质量达标。

## 检查维度

| 维度 | 检查项 | 通过标准 |
|------|--------|----------|
| **完整性** | 是否覆盖所有要求 | 无遗漏 |
| **准确性** | 事实是否正确 | 无错误 |
| **规范性** | 格式是否符合标准 | 符合模板 |
| **可用性** | 产出是否可直接使用 | 无需大改 |

## 评分标准

| 分数 | 等级 | 处理方式 |
|------|------|----------|
| 9-10 | 优秀 | 直接通过 |
| 7-8 | 良好 | 小修改后通过 |
| 5-6 | 及格 | 打回重做部分 |
| <5 | 不合格 | 全部重做 |

## 输出格式

```json
{
  "taskId": "{{taskId}}",
  "artifactPath": "产出物路径",
  "score": 8,
  "grade": "良好",
  "checks": {
    "completeness": { "passed": true, "note": "" },
    "accuracy": { "passed": true, "note": "" },
    "format": { "passed": false, "note": "格式问题：xxx" },
    "usability": { "passed": true, "note": "" }
  },
  "decision": "pass|revise|reject",
  "feedback": "具体反馈",
  "requireRework": ["需要重做的部分"]
}
```

## 检查流程

```
1. 读取产出物
   ↓
2. 逐项检查
   ↓
3. 计算分数
   ↓
4. 给出决策
   ↓
5. 记录反馈
```

## 示例

### 输入
```
产出物：~/clawos/output/task-001/article.md
要求：3000字技术博客，包含代码示例
```

### 输出
```json
{
  "taskId": "task-001",
  "artifactPath": "~/clawos/output/task-001/article.md",
  "score": 8,
  "grade": "良好",
  "checks": {
    "completeness": { "passed": true, "note": "字数达标，包含示例" },
    "accuracy": { "passed": true, "note": "技术内容正确" },
    "format": { "passed": true, "note": "Markdown格式规范" },
    "usability": { "passed": true, "note": "可直接发布" }
  },
  "decision": "pass",
  "feedback": "质量良好，可以直接使用",
  "requireRework": []
}
```
