---
name: coding-workflow
description: 开发工作流 Skill，编排开发任务的完整流程
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [node, git]
      env: []
---

# 开发工作流 Skill

编排开发任务的完整流程，从需求到交付。

## 工作流阶段

```
1. 需求分析 → 明确功能、接口、约束
2. 技术设计 → 架构、数据模型、API
3. 编码实现 → 前端/后端/全栈
4. 测试验证 → 单元测试、集成测试
5. 代码审查 → Review、修复
6. 部署交付 → 提交、发布
```

## 并发策略

**重要**：使用有限并行模式

| 阶段 | 并发数 | 原因 |
|------|--------|------|
| 技术设计 | 1 | 需要统一架构 |
| 编码实现 | 2-3 | 前后端可并行 |
| 测试验证 | 2 | 单元/E2E 可并行 |
| 代码审查 | 1 | 需要完整上下文 |

## Worker 选择

| 任务类型 | 推荐 Worker | 备选 |
|----------|-------------|------|
| 前端开发 | coder-frontend | tester-auto |
| 后端开发 | coder-backend | tester-auto |
| 全栈开发 | coder-frontend + coder-backend | - |
| 测试编写 | tester-auto | - |
| Git 操作 | github-ops | - |

## 输入参数

```typescript
interface CodingWorkflowInput {
  taskId: string;
  type: 'frontend' | 'backend' | 'fullstack' | 'api' | 'tool';
  description: string;
  techStack?: {
    frontend?: string[];
    backend?: string[];
    database?: string;
  };
  requirements: {
    features: string[];
    testCoverage?: number;  // 默认 0.8
    documentation?: boolean;
  };
  delivery?: {
    targetRepo?: string;
    createPR?: boolean;
    branchName?: string;
  };
}
```

## 输出格式

```json
{
  "taskId": "{{taskId}}",
  "status": "completed",
  "artifacts": [
    {
      "type": "code",
      "path": "~/clawos/output/{{taskId}}/src/",
      "fileCount": 15
    },
    {
      "type": "test",
      "path": "~/clawos/output/{{taskId}}/tests/",
      "coverage": 0.85
    }
  ],
  "metrics": {
    "totalLLMCalls": 120,
    "totalTokens": 500000,
    "executionTimeMs": 14400000,
    "testCoverage": 0.85,
    "linesOfCode": 2500
  },
  "quality": {
    "lintPassed": true,
    "testsPassed": true,
    "reviewApproved": true
  },
  "delivery": {
    "prUrl": "https://github.com/xxx/pull/123",
    "branch": "feature/{{taskId}}"
  }
}
```

## 质量门禁

| 检查项 | 要求 | 失败处理 |
|--------|------|----------|
| Lint | 0 errors | 修复后继续 |
| Type Check | 0 errors | 修复后继续 |
| Test Coverage | >= 80% | 补充测试 |
| Unit Tests | 全部通过 | 修复后继续 |
| Code Review | 通过 | 修改后重新审查 |

## 工作流配置

```yaml
workflow:
  name: coding-workflow
  maxConcurrent: 3
  timeout: 28800000  # 8小时
  retryPolicy:
    maxRetries: 2
    backoffMs: 120000
  qualityGates:
    - lint
    - typeCheck
    - testCoverage
    - unitTests
    - codeReview
```

## 异常处理

| 异常 | 处理方式 |
|------|----------|
| Lint 失败 | Coder 修复 |
| 测试失败 | Coder 修复 + Tester 验证 |
| Review 不通过 | 按反馈修改 |
| 依赖安装失败 | 换用备选方案 |
| Token 超限 | 分模块处理 |
