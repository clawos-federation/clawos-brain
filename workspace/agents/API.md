# API 参考

OpenClaw Professional Agents 各组件的详细 API 接口说明。

---

## 目录

- [AgentFactory](#agentfactory)
- [AgentRouter](#agentrouter)
- [TaskDispatcher](#taskdispatcher)
- [ContextManager](#contextmanager)
- [AgentMonitor](#agentmonitor)

---

## AgentFactory

Agent 工厂类，负责 agent 的加载、实例化和生命周期管理。

### 构造函数

```javascript
const { AgentFactory } = require('./agent-factory');
const factory = new AgentFactory(options);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `registryPath` | string | `'./registry.json'` | 注册表路径 |
| `schemaPath` | string | `'./agent-schema.json'` | Schema 路径 |
| `defaultTimeout` | number | 30000 | 默认超时(ms) |

### 方法

#### loadAgent(agentId)

加载单个 agent。

```javascript
const agent = factory.loadAgent('devagent');
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agentId` | string | ✅ | Agent ID |

**返回值**

```javascript
{
  id: 'devagent',
  version: '0.1.0',
  name: '代码专家 (DevAgent)',
  profile: { /* ... */ },
  model: { /* ... */ },
  memory: { /* ... */ },
  capabilities: ['code-generation', 'bug-fixing', ...],
  // ...
}
```

**抛出异常**

```javascript
// Agent 未找到
throw new Error("Agent 'xxx' not found in registry");

// Schema 验证失败
throw new Error("Agent schema validation failed: xxx");
```

#### loadAllAgents()

加载所有 agents。

```javascript
const agents = factory.loadAllAgents();
// Map<agentId, Agent>
```

#### listAgents()

列出所有 agents（不加载）。

```javascript
const list = factory.listAgents();
```

**返回值**

```javascript
[
  {
    id: 'devagent',
    version: '0.1.0',
    status: 'active',
    qualityScore: 9.7,
    path: './devagent/agent.json'
  },
  // ...
]
```

#### updateAgentStatus(agentId, status)

更新 agent 状态。

```javascript
factory.updateAgentStatus('devagent', 'active');
factory.updateAgentStatus('newagent', 'development');
```

**Status 值**

| 值 | 说明 |
|---|------|
| `active` | 活跃，可用于执行任务 |
| `development` | 开发中，测试用途 |
| `deprecated` | 已废弃，不推荐使用 |
| `disabled` | 禁用，不可用 |

#### validateAgent(agentId)

验证 agent 配置。

```javascript
const result = factory.validateAgent('devagent');
```

**返回值**

```javascript
{
  valid: true,
  errors: [],
  warnings: []
}
```

---

## AgentRouter

Agent 路由器，负责任务分析和路由决策。

### 构造函数

```javascript
const { AgentRouter } = require('./agent-router');
const router = new AgentRouter(options);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `registryPath` | string | `'./registry.json'` | 注册表路径 |
| `defaultStrategy` | string | `'single-agent'` | 默认策略 |
| `enableParallel` | boolean | `true` | 启用并行 |
| `enableSequential` | boolean | `true` | 启用顺序链 |

### 方法

#### analyzeTask(task)

分析任务。

```javascript
const analysis = router.analyzeTask('创建一个用户认证系统');
```

**返回值**

```javascript
{
  task: '创建一个用户认证系统',
  keywords: ['创建', '用户', '认证', '系统'],
  capabilities: ['code-generation', 'technical-design'],
  complexity: 'medium',
  risk: 'low',
  estimatedDuration: 5000,
  suggestedAgents: ['devagent']
}
```

**复杂度评估**

| 值 | 说明 | 触发条件 |
|---|------|---------|
| `low` | 简单任务 | 单关键词，单 capability |
| `medium` | 中等任务 | 多关键词，多 capability |
| `high` | 复杂任务 | 跨域，多步骤，高风险 |

**风险评估**

| 值 | 说明 | 触发条件 |
|---|------|---------|
| `low` | 低风险 | 一般任务 |
| `medium` | 中等风险 | 涉及敏感操作 |
| `high` | 高风险 | 法律、医疗、金融等 |

#### scoreAgents(analysis)

对 agents 进行评分。

```javascript
const scores = router.scoreAgents(analysis);
// Map<agentId, { score, reasons: [] }>
```

**返回值**

```javascript
Map {
  'devagent' => {
    score: 1.0,
    reasons: ['capability match: code-generation'],
    confidence: 0.95
  },
  'legalagent' => {
    score: 0.1,
    reasons: [],
    confidence: 0.3
  }
}
```

#### decideStrategy(analysis, scores)

决定执行策略。

```javascript
const strategy = router.decideStrategy(analysis, scores);
```

**返回值**

```javascript
{
  mode: 'single-agent',  // single-agent | parallel-voting | sequential-chain | hierarchy
  agents: ['devagent'],
  params: {
    votingThreshold: 0.7,
    timeout: 30000,
    minAgents: 2,
    maxAgents: 3
  },
  reasoning: '任务简单，单 agent 足够'
}
```

**策略选择规则**

| 条件 | 策略 |
|------|------|
| 单 agent 得分 >= 0.9 | `single-agent` |
| 高风险（risk=high）| `parallel-voting` |
| 多步骤任务 | `sequential-chain` |
| 超复杂任务 | `hierarchy` |

#### route(task)

完整路由流程。

```javascript
const result = router.route('创建一个用户认证系统');
```

**返回值**

```javascript
{
  task: '创建一个用户认证系统',
  analysis: { /* ... */ },
  scores: Map { /* ... */ },
  strategy: { /* ... */ },
  routingTime: 45  // ms
}
```

---

## TaskDispatcher

任务分发器，负责任务执行和编排。

### 构造函数

```javascript
const { TaskDispatcher } = require('./task-dispatcher');
const dispatcher = new TaskDispatcher(options);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `factory` | AgentFactory | required | Agent 工厂实例 |
| `contextManager` | ContextManager | required | 上下文管理器 |
| `monitor` | AgentMonitor | required | 监控实例 |
| `defaultTimeout` | number | 60000 | 默认超时(ms) |
| `maxRetries` | number | 3 | 最大重试次数 |

### 方法

#### execute(task, strategy)

执行任务（通用接口）。

```javascript
const result = await dispatcher.execute(task, strategy);
```

#### executeSingle(task, agentId)

单 agent 执行。

```javascript
const result = await dispatcher.executeSingle(
  '创建 API',
  'devagent'
);
```

**返回值**

```javascript
{
  executionId: 'exec_xxx',
  agentId: 'devagent',
  task: '创建 API',
  mode: 'single-agent',
  success: true,
  confidence: 0.9,
  result: {
    // Agent 执行结果
    output: '创建了 REST API...',
    artifacts: []
  },
  duration: 2500,
  context: { /* ... */ }
}
```

#### executeParallel(task, agentIds, options)

并行投票执行。

```javascript
const result = await dispatcher.executeParallel(
  '设计 GDPR 合规系统',
  ['devagent', 'legalagent', 'researchagent'],
  {
    votingMethod: 'score-weighted',
    timeout: 30000,
    minResponses: 2
  }
);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `votingMethod` | string | `'score-weighted'` | 投票方法 |
| `timeout` | number | 30000 | 超时(ms) |
| `minResponses` | number | 2 | 最少响应数 |

**返回值**

```javascript
{
  executionId: 'exec_xxx',
  mode: 'parallel-voting',
  agents: ['devagent', 'legalagent', 'researchagent'],
  responses: [
    { agentId: 'devagent', output: '...', score: 0.95 },
    { agentId: 'legalagent', output: '...', score: 0.85 },
    { agentId: 'researchagent', output: '...', score: 0.80 }
  ],
  winner: 'devagent',
  consensus: 0.87,
  duration: 4500
}
```

#### executeSequential(task, agentChain, options)

顺序链执行。

```javascript
const result = await dispatcher.executeSequential(
  '开发电商平台',
  ['researchagent', 'devagent', 'legalagent'],
  {
    passContext: true,
    stopOnError: false
  }
);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `passContext` | boolean | `true` | 传递上下文 |
| `stopOnError` | boolean | `false` | 遇错停止 |

**返回值**

```javascript
{
  executionId: 'exec_xxx',
  mode: 'sequential-chain',
  chain: ['researchagent', 'devagent', 'legalagent'],
  steps: [
    {
      step: 1,
      agentId: 'researchagent',
      success: true,
      output: { findings: [...] }
    },
    {
      step: 2,
      agentId: 'devagent',
      success: true,
      output: { code: [...] }
    },
    {
      step: 3,
      agentId: 'legalagent',
      success: true,
      output: { review: [...] }
    }
  ],
  duration: 12000,
  finalResult: { /* 聚合结果 */ }
}
```

#### getHistory(executionId)

获取执行历史。

```javascript
const history = dispatcher.getHistory();
// 或指定执行 ID
const exec = dispatcher.getHistory('exec_xxx');
```

---

## ContextManager

上下文管理器，负责上下文的打包、解包和状态管理。

### 构造函数

```javascript
const { ContextManager } = require('./context-manager');
const manager = new ContextManager(options);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `storageDir` | string | `'./logs/contexts'` | 存储目录 |
| `defaultTTL` | number | 3600000 | 默认 TTL(ms) |
| `maxSize` | number | 1000 | 最大上下文数 |

### 方法

#### pack(data)

打包上下文。

```javascript
const context = manager.pack({
  task: '创建 API',
  agentId: 'devagent',
  history: [
    { role: 'user', content: '创建一个 API' },
    { role: 'assistant', content: '好的，我来创建...' }
  ],
  state: {
    apiDesign: { /* ... */ },
    code: []
  },
  metadata: {
    createdAt: new Date(),
    ttl: 3600000
  }
});
```

**返回值**

```javascript
{
  id: 'ctx_xxx',
  data: { /* ... */ },
  size: 1024,
  createdAt: '2026-02-11T12:00:00Z',
  expiresAt: '2026-02-11T13:00:00Z'
}
```

#### unpack(contextId)

解包上下文。

```javascript
const data = manager.unpack('ctx_xxx');
```

#### merge(contexts, method)

合并多个上下文。

```javascript
const merged = manager.merge(
  [context1, context2, context3],
  'concatenate'  // 或 'union'
);
```

**合并方法**

| 方法 | 说明 |
|------|------|
| `concatenate` | 顺序拼接历史 |
| `union` | 合并状态对象 |

#### aggregate(results, method)

聚合多个结果。

```javascript
const summary = manager.aggregate(
  [result1, result2, result3],
  'vote'  // 或 'merge', 'consensus', 'best', 'summary'
);
```

**聚合方法**

| 方法 | 说明 | 适用场景 |
|------|------|---------|
| `vote` | 投票选择 | 并行执行 |
| `merge` | 合并内容 | 顺序链 |
| `consensus` | 共识提取 | 多视角 |
| `best` | 选择最佳 | 质量优先 |
| `summary` | 生成摘要 | 结果汇总 |

#### list(filter)

列出上下文。

```javascript
const contexts = manager.list({
  agentId: 'devagent',
  since: '2026-02-11T00:00:00Z',
  limit: 10
});
```

#### clear(expiredOnly)

清理过期上下文。

```javascript
const removed = manager.clear(true);  // 只清理过期的
const removed = manager.clear(false);  // 清理所有
```

---

## AgentMonitor

Agent 监控器，负责日志记录、指标收集和健康检查。

### 构造函数

```javascript
const { AgentMonitor } = require('./agent-monitor');
const monitor = new AgentMonitor(options);
```

**Options**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `logDir` | string | `'./logs'` | 日志目录 |
| `metricsFile` | string | `'./logs/metrics.json'` | 指标文件 |
| `retentionDays` | number | 7 | 保留天数 |

### 方法

#### logExecution(execution)

记录执行。

```javascript
monitor.logExecution({
  executionId: 'exec_xxx',
  agentId: 'devagent',
  task: '创建 API',
  mode: 'single-agent',
  strategy: { /* ... */ },
  input: { /* ... */ },
  output: { /* ... */ },
  success: true,
  duration: 2500,
  tokens: { prompt: 500, completion: 200 },
  error: null,
  metadata: {
    timestamp: new Date(),
    userId: 'user_xxx'
  }
});
```

#### logEvent(event)

记录事件。

```javascript
monitor.logEvent({
  type: 'agent_loaded',
  agentId: 'devagent',
  timestamp: new Date(),
  data: { version: '0.1.0' }
});
```

#### getMetrics(filter)

获取指标。

```javascript
const metrics = monitor.getMetrics({
  agentId: 'devagent',
  since: '2026-02-11T00:00:00Z',
  aggregate: 'hourly'
});
```

**返回值**

```javascript
{
  totalExecutions: 100,
  successRate: 0.95,
  avgDuration: 2500,
  avgConfidence: 0.88,
  agentBreakdown: {
    devagent: { count: 50, successRate: 0.98, avgDuration: 2000 },
    legalagent: { count: 30, successRate: 0.93, avgDuration: 3500 },
    researchagent: { count: 20, successRate: 0.90, avgDuration: 4000 }
  },
  modeBreakdown: {
    'single-agent': { count: 60, successRate: 0.97 },
    'parallel-voting': { count: 25, successRate: 0.92 },
    'sequential-chain': { count: 15, successRate: 0.87 }
  },
  hourlyDistribution: [
    { hour: 0, count: 5 },
    { hour: 1, count: 3 },
    // ...
  ]
}
```

#### getHealthStatus()

获取健康状态。

```javascript
const health = monitor.getHealthStatus();
```

**返回值**

```javascript
{
  status: 'healthy',  // healthy | degraded | unhealthy
  timestamp: '2026-02-11T12:00:00Z',
  uptime: 86400,
  checks: {
    agentRegistry: { status: 'healthy', latency: 5 },
    contextStorage: { status: 'healthy', usage: 0.15 },
    logStorage: { status: 'healthy', usage: 0.08 }
  },
  alerts: []
}
```

**健康状态定义**

| 状态 | 说明 |
|------|------|
| `healthy` | 所有检查正常 |
| `degraded` | 部分指标异常，仍可服务 |
| `unhealthy` | 服务不可用 |

#### exportMetrics(path, format)

导出指标。

```javascript
// 导出为 CSV
monitor.exportMetrics('./metrics.csv', 'csv');

// 导出为 JSON
monitor.exportMetrics('./metrics.json', 'json');

// 导出为 Prometheus 格式
monitor.exportMetrics('./metrics.prom', 'prometheus');
```

#### cleanup()

清理旧日志。

```javascript
monitor.cleanup();
// 移除 7 天前的日志文件
```

---

## 错误处理

### 错误类型

```javascript
// Agent 未找到
throw new AgentNotFoundError('devagent');

// 任务执行失败
throw new ExecutionError('Task failed after 3 retries');

// 上下文过期
throw new ContextExpiredError('Context expired');

// 超时
throw new TimeoutError('Execution timeout after 60000ms');
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| `EAGENT001` | Agent 未找到 |
| `EAGENT002` | Agent 加载失败 |
| `EAGENT003` | Agent 执行失败 |
| `EROUTE001` | 路由失败 |
| `EROUTE002` | 无匹配的 Agent |
| `ECTX001` | 上下文创建失败 |
| `ECTX002` | 上下文过期 |
| `ECTX003` | 上下文合并失败 |
| `EDISP001` | 分发失败 |
| `EDISP002` | 超时 |
| `EDISP003` | 重试次数耗尽 |

---

## 事件

### Agent 生命周期事件

```javascript
factory.on('agent_loaded', (agent) => { /* ... */ });
factory.on('agent_unloaded', (agent) => { /* ... */ });
factory.on('agent_error', (error) => { /* ... */ });
```

### 任务执行事件

```javascript
dispatcher.on('task_started', (task) => { /* ... */ });
dispatcher.on('task_completed', (result) => { /* ... */ });
dispatcher.on('task_failed', (error) => { /* ... */ });
dispatcher.on('step_completed', (step) => { /* ... */ });
```

### 监控事件

```javascript
monitor.on('execution_logged', (log) => { /* ... */ });
monitor.on('alert_triggered', (alert) => { /* ... */ });
monitor.on('metrics_updated', (metrics) => { /* ... */ });
```

---

**最后更新**: 2026-02-11
