# OpenClaw Professional Agents

专业 agents 系统架构和实现。

---

## 📋 快速导航

- [快速开始](#-快速开始) - 5 分钟上手
- [架构设计](#-架构设计) - 系统架构说明
- [API 参考](#-api-参考) - 组件接口文档
- [示例场景](#-示例场景) - 实际使用案例
- [故障排除](#-故障排除) - 常见问题解决

---

## 🚀 快速开始

### 1. 环境要求

- **Node.js** >= 18
- **OpenClaw** 已安装并配置

### 2. 初始化

```bash
# 进入 agents 目录
cd /Users/henry/openclaw-system/workspace/agents

# 安装依赖（如果需要）
npm install

# 验证安装
node agent-factory.js list
```

### 3. 第一个任务

```bash
# 路由一个简单的开发任务
node agent-router.js route "创建一个 REST API，支持用户注册和登录"

# 预期输出：
# ✅ Loaded agent registry
# 🔍 Task Analysis:
#    Keywords: 创建, API
#    Capabilities: code-generation
# 📊 Agent Scoring:
#    devagent  ██████████ 100%
# 🎯 Routing Strategy:
#    Mode: single-agent
#    Agents: devagent
```

### 4. 运行集成测试

```bash
node integration-test.js

# 预期输出：
# 📊 Results: 7 passed, 0 skipped, 0 failed
# 🎉 All tests passed!
```

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        User Request                          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                     Agent Router                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Task Parser │→│ Cap Matcher │→│ Strategy Selector   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   Task Dispatcher                            │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │  Single  │ Parallel │Sequential│ Hierarchy│             │
│  └──────────┴──────────┴──────────┴──────────┘             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                     Agents                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ DevAgent │  │LegalAgent│  │Research  │                  │
│  │(Code)    │  │(Legal)   │  │Agent     │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Agent 核心公式

```
Agent Effectiveness = (Model Capability) × (Skill Quality) × (Prompt Precision) × (Task Alignment)
```

### 核心组件

| 组件 | 文件 | 职责 | 输入 | 输出 |
|------|------|------|------|------|
| **Agent Factory** | `agent-factory.js` | Agent 加载、实例化 | agent-id | Agent 实例 |
| **Agent Router** | `agent-router.js` | 任务路由 | 任务描述 | 执行策略 |
| **Task Dispatcher** | `task-dispatcher.js` | 任务编排 | 策略 + 任务 | 执行结果 |
| **Context Manager** | `context-manager.js` | 上下文管理 | 任务 + 历史 | 上下文包 |
| **Agent Monitor** | `agent-monitor.js` | 监控和日志 | 执行事件 | 指标 + 日志 |

---

## 📁 目录结构

```
agents/
├── 📄 README.md                    # 本文档
├── 📄 QUICKSTART.md               # 快速上手指南
├── 📄 API.md                      # API 参考文档
├── 📄 EXAMPLES.md                 # 使用示例
│
├── 📋 agent-schema.json           # Agent 定义 JSON Schema
├── 📋 registry.json               # Agent 注册表
│
├── 🔧 agent-factory.js            # Agent 工厂
├── 🔧 agent-router.js             # Agent 路由器
├── 🔧 task-dispatcher.js          # 任务分发器
├── 🔧 context-manager.js          # 上下文管理器
├── 🔧 agent-monitor.js            # 监控和日志
├── 🧪 integration-test.js         # 集成测试
│
├── 📂 logs/                       # 执行日志
│   ├── exec_*.log                # 单次执行日志
│   └── metrics.json              # 聚合指标
│
├── 🤖 devagent/                   # 代码专家
│   ├── agent.json
│   ├── prompt.md
│   └── tests/
│       └── test-generation.js
│
├── ⚖️ legalagent/                 # 法律专家
│   ├── agent.json
│   ├── prompt.md
│   └── tests/
│
└── 🔬 researchagent/              # 研究专家
    ├── agent.json
    ├── prompt.md
    └── tests/
```

---

## 🔌 API 参考

### Agent Factory

```javascript
const { AgentFactory } = require('./agent-factory');
const factory = new AgentFactory();

// 加载单个 agent
const agent = factory.loadAgent('devagent');

// 加载所有 agents
const agents = factory.loadAllAgents();

// 更新 agent 状态
factory.updateAgentStatus('devagent', 'active');

// 列出所有 agents
factory.listAgents();
```

### Agent Router

```javascript
const { AgentRouter } = require('./agent-router');
const router = new AgentRouter();

// 分析任务
const analysis = router.analyzeTask('创建用户认证系统');
// 返回: { keywords, capabilities, complexity, risk }

// 评分 agents
const scores = router.scoreAgents(analysis);
// 返回: Map<agent-id, score>

// 路由决策
const strategy = router.decideStrategy(analysis, scores);
// 返回: { mode, agents, params }

// 完整路由
const result = router.route('创建用户认证系统');
```

### Task Dispatcher

```javascript
const { TaskDispatcher } = require('./task-dispatcher');
const dispatcher = new TaskDispatcher();

// 单 agent 执行
const result = await dispatcher.executeSingle(task, agentId);

// 并行投票
const result = await dispatcher.executeParallel(task, ['devagent', 'legalagent']);

// 顺序链
const result = await dispatcher.executeSequential(task, ['researchagent', 'devagent']);

// 查看历史
const history = dispatcher.getHistory();
```

### Context Manager

```javascript
const { ContextManager } = require('./context-manager');
const manager = new ContextManager();

// 打包上下文
const context = manager.pack({
  task: '创建 API',
  agentId: 'devagent',
  history: [],
  state: {}
});

// 解包上下文
const data = manager.unpack(contextId);

// 合并上下文
const merged = manager.merge([ctx1, ctx2], 'concatenate');

// 聚合结果
const result = manager.aggregate([result1, result2], 'vote');
```

### Agent Monitor

```javascript
const { AgentMonitor } = require('./agent-monitor');
const monitor = new AgentMonitor();

// 记录执行
monitor.logExecution({
  executionId: 'exec_xxx',
  agentId: 'devagent',
  task: '创建 API',
  mode: 'single-agent',
  success: true,
  duration: 1000
});

// 获取指标
const metrics = monitor.getMetrics();

// 获取健康状态
const health = monitor.getHealthStatus();

// 导出 CSV
monitor.exportMetrics('metrics.csv');
```

---

## 📖 示例场景

### 场景 1：简单开发任务

```bash
# 任务：创建一个简单的 Express 服务器
node agent-router.js route "创建一个 Express 服务器，包含基本的中间件和路由"

# 输出：
# 🔍 Task Analysis:
#    Keywords: 创建, 服务器, 路由
#    Capabilities: code-generation, technical-design
# 📊 Agent Scoring:
#    devagent  ██████████ 100%
# 🎯 Routing Strategy:
#    Mode: single-agent
#    Agents: devagent
```

### 场景 2：合同审查

```bash
# 任务：审查服务合同
node agent-router.js route "审查这份服务合同，识别潜在的法律风险和责任条款"

# 输出：
# 🔍 Task Analysis:
#    Keywords: 审查, 合同, 风险
#    Capabilities: contract-review, risk-assessment
# 📊 Agent Scoring:
#    legalagent  ██████████ 100%
# 🎯 Routing Strategy:
#    Mode: single-agent
#    Agents: legalagent
```

### 场景 3：市场研究

```bash
# 任务：研究竞品
node agent-router.js route "研究竞争对手的产品策略和市场定位"

# 输出：
# 🔍 Task Analysis:
#    Keywords: 研究, 竞争, 策略
#    Capabilities: research, competitive-intelligence
# 📊 Agent Scoring:
#    researchagent  ██████████ 100%
# 🎯 Routing Strategy:
#    Mode: single-agent
#    Agents: researchagent
```

### 场景 4：高风险任务（并行投票）

```bash
# 任务：处理敏感的法律-技术交叉问题
node task-dispatcher.js execute "设计一个符合 GDPR 的数据收集系统"

# 内部逻辑：
# - 识别为高风险任务（法律 + 技术）
# - 触发并行投票模式
# - DevAgent + LegalAgent + ResearchAgent 同时执行
# - 投票选出最佳方案
```

### 场景 5：复杂项目（顺序链）

```bash
# 任务：完整的系统开发
node task-dispatcher.js execute "开发一个电商平台，需要研究竞品、设计架构、编写代码"

# 内部逻辑：
# - 识别为复杂多步骤任务
# - 触发顺序链模式
# - Step 1: ResearchAgent 研究竞品
# - Step 2: DevAgent 设计架构
# - Step 3: DevAgent 编写代码
```

---

## 🧪 测试

### 运行测试

```bash
# 集成测试
node integration-test.js

# 特定 agent 测试
cd devagent/tests && node test-generation.js
cd legalagent/tests && node test-analysis.js
cd researchagent/tests && node test-research.js
```

### 测试覆盖

| 测试类型 | 文件 | 说明 |
|---------|------|------|
| 集成测试 | `integration-test.js` | 全流程测试 |
| Agent 加载 | `agent-factory.js` | Agent 实例化测试 |
| 路由测试 | `agent-router.js` | 任务路由测试 |
| 分发测试 | `task-dispatcher.js` | 任务编排测试 |
| 上下文测试 | `context-manager.js` | 上下文管理测试 |
| 监控测试 | `agent-monitor.js` | 监控功能测试 |

---

## 🔧 故障排除

### 问题 1：Agent 加载失败

**症状**：`Error: Agent 'xxx' not found`

**解决方案**：
```bash
# 检查 registry.json
node agent-factory.js list

# 验证 agent.json 存在
ls -la agents/xxx/agent.json

# 检查 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('agents/xxx/agent.json'))"
```

### 问题 2：路由无匹配

**症状**：`⚠️ No matching agents found`

**解决方案**：
```bash
# 检查关键词映射
# 编辑 agent-router.js 中的 taskKeywords 和 capabilityMap

# 测试路由
node agent-router.js route "你的任务描述"
```

### 问题 3：任务执行失败

**症状**：任务执行超时或报错

**解决方案**：
```bash
# 查看日志
cat logs/exec_*.log

# 检查健康状态
node agent-monitor.js health

# 验证 agent 状态
node agent-factory.js list
```

### 问题 4：上下文丢失

**症状**：多轮对话历史丢失

**解决方案**：
```bash
# 检查上下文存储
node context-manager.js list

# 清理过期上下文
node context-manager.js clear
```

---

## 📊 性能指标

### 当前性能

```
Agent Health Status:
   Status: HEALTHY
   Success Rate: 100.0%
   Total Executions: 12
   Avg Duration: 227ms
```

### 优化建议

| 指标 | 目标 | 当前 | 优化方案 |
|------|------|------|---------|
| 成功率 | >95% | 100% | ✅ 达标 |
| 平均延迟 | <500ms | 227ms | ✅ 达标 |
| 路由准确率 | >90% | ~85% | 扩充关键词 |
| 上下文命中率 | >80% | N/A | 待评估 |

---

## 📝 Agent 定义模板

```json
{
  "$schema": "../agent-schema.json",
  "id": "myagent",
  "version": "1.0.0",
  "name": "我的 Agent",
  "description": "描述这个 agent 做什么",
  
  "profile": {
    "role": "角色描述",
    "goals": ["目标1", "目标2"],
    "constraints": ["约束1", "约束2"]
  },
  
  "model": {
    "primary": "claude-3.5-sonnet",
    "fallback": ["gpt-4o", "glm-4.7"],
    "provider": "anthropic"
  },
  
  "promptFile": "prompt.md",
  
  "memory": {
    "type": "hybrid",
    "shortTerm": { "enabled": true, "maxTurns": 10 },
    "longTerm": { "enabled": true, "storage": "vector" },
    "semantic": { "enabled": true, "index": "MEMORY.md" }
  },
  
  "planning": {
    "enabled": true,
    "method": "chain_of_thought"
  },
  
  "skills": [
    { "id": "web_search", "required": true, "permission": "read-only" },
    { "id": "web_fetch", "required": true, "permission": "read-only" }
  ],
  
  "reflection": {
    "enabled": true,
    "autoSelfCritique": true,
    "improvePrompt": "请回顾你的工作..."
  },
  
  "capabilities": ["capability1", "capability2"],
  
  "guardrails": {
    "maxTokens": 4000,
    "allowedOperations": ["read", "search", "fetch"],
    "blockedPatterns": ["rm -rf", "drop database"],
    "requireHumanApproval": [],
    "disclaimer": "免责声明..."
  },
  
  "observability": {
    "logging": true,
    "metrics": ["latency", "tokens", "quality"],
    "tracing": true
  },
  
  "quality": {
    "threshold": 7.0,
    "tests": ["tests/test.js"],
    "autoTest": false
  },
  
  "metadata": {
    "author": "Your Name",
    "tags": ["tag1", "tag2"],
    "estimatedCost": "medium",
    "createdAt": "2026-02-11T00:00:00Z",
    "updatedAt": "2026-02-11T00:00:00Z"
  }
}
```

---

## 🤝 贡献指南

### 创建新 Agent

1. **Fork 并创建分支**
   ```bash
   git checkout -b feature/new-agent
   ```

2. **创建 Agent 目录**
   ```bash
   mkdir -p agents/myagent/tests
   ```

3. **编写 agent.json**
   - 参考模板和 devagent 示例
   - 确保通过 schema 验证

4. **编写 prompt.md**
   - 定义清晰的系统角色
   - 包含工作原则和流程
   - 提供示例输出格式

5. **编写测试**
   - 覆盖核心功能
   - 确保质量 >= 7.0

6. **更新注册表**
   ```json
   {
     "myagent": {
       "id": "myagent",
       "version": "1.0.0",
       "status": "development",
       "qualityScore": 0.0,
       "path": "./myagent/agent.json"
     }
   }
   ```

7. **测试验证**
   ```bash
   node agent-factory.js list
   node agent-router.js route "测试任务"
   node integration-test.js
   ```

8. **提交 PR**
   - 清晰的描述
   - 测试结果截图
   - 更新文档

---

## 📅 路线图

### ✅ 已完成

- [x] Phase 1: 基础架构
- [x] Phase 2: 核心功能
- [x] Phase 3: 专业 Agents

### 🚧 进行中

- [ ] Phase 4: OpenClaw 集成
- [ ] 完善文档和测试

### 📋 计划中

- [ ] Phase 5: 更多专业 Agents
- [ ] Phase 6: 性能优化
- [ ] Phase 7: 自动化评估

---

## 📞 支持

- **文档**: 本文档和 `/docs` 目录
- **问题**: 查看 [故障排除](#-故障排除) 部分
- **示例**: 查看 [EXAMPLES.md](./EXAMPLES.md)
- **API**: 查看 [API.md](./API.md)

---

**版本**: 1.0.0  
**最后更新**: 2026-02-11  
**维护者**: Zach + OpenClaw Team
