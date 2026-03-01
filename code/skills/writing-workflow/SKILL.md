---
name: writing-workflow
description: 写作工作流 Skill，编排写作任务的完整流程
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [node]
      env: []
---

# 写作工作流 Skill

编排写作任务的完整流程，从大纲到最终产出。

## 工作流阶段

```
1. 需求分析 → 明确主题、字数、风格
2. 大纲策划 → 结构、章节、要点
3. 内容创作 → 分章节/段落写作
4. 审核修订 → 质量检查、修改
5. 最终交付 → 排版、输出
```

## 并发策略

**重要**：使用有限并行模式，避免挤爆 Sub-agent 队列

| 阶段 | 并发数 | 原因 |
|------|--------|------|
| 大纲策划 | 1 | 需要统一规划 |
| 内容创作 | 2-3 | 有限并行，避免队列阻塞 |
| 审核修订 | 1 | 需要上下文连贯 |

## Worker 选择

| 任务类型 | 推荐 Worker | 备选 |
|----------|-------------|------|
| 技术文章 | writer-general | researcher-web |
| 书籍 | writer-general | reviewer-content |
| 文案 | writer-general | - |
| 调研报告 | researcher-web | writer-general |

## 输入参数

```typescript
interface WritingWorkflowInput {
  taskId: string;
  type: 'article' | 'book' | 'copy' | 'report';
  title: string;
  wordCount: number;
  style?: 'technical' | 'casual' | 'formal';
  chapters?: number;  // 书籍专用
  outline?: string;   // 可选：已有大纲
  references?: string[]; // 参考资料路径
}
```

## 输出格式

```json
{
  "taskId": "{{taskId}}",
  "status": "completed",
  "artifacts": [
    {
      "type": "markdown",
      "path": "~/clawos/output/{{taskId}}/output.md",
      "wordCount": 3250
    }
  ],
  "metrics": {
    "totalLLMCalls": 45,
    "totalTokens": 150000,
    "executionTimeMs": 7200000,
    "revisionCount": 1
  },
  "quality": {
    "score": 8,
    "passedQA": true
  }
}
```

## 工作流配置

```yaml
workflow:
  name: writing-workflow
  maxConcurrent: 2
  timeout: 14400000  # 4小时
  retryPolicy:
    maxRetries: 2
    backoffMs: 60000
```

## 异常处理

| 异常 | 处理方式 |
|------|----------|
| Writer 超时 | 换用备选 Worker |
| 质量不达标 | 打回重做，最多 2 次 |
| 资料不足 | 先调用 Researcher 补充 |
| Token 超限 | 分段处理 |
