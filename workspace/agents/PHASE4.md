# OpenClaw Professional Agents - Phase 4 实施计划

## 目标

将现有的 Professional Agents 系统与 OpenClaw 深度集成，实现真实的 LLM 调用和完整的端到端工作流。

## 实施步骤

### Step 1: 理解 OpenClaw Agent 架构 ✅

**已确认**：
- OpenClaw 使用 `agents.list` 配置多个 agents
- 每个 agent 有独立的 workspace、`agentDir` 和 sessions
- Bindings 用于路由消息到特定 agents
- Skills 从三个位置加载：bundled、`~/.openclaw/clawos/skills`、`<workspace>/skills`

### Step 2: 设计集成架构

**集成方式**：采用"代理模式"而非直接集成

```
┌─────────────────────────────────────────────┐
│         OpenClaw Gateway             │
│  (agents: main, dev, legal, etc.)    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│   OpenClaw Agent Runtime              │
│   (embedded pi-mono)                 │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│   Agent Skill (wrapper)               │
│   - Reads workspace/agents/*.json      │
│   - Routes task to appropriate agent   │
│   - Calls LLM via OpenClaw tools    │
└─────────────────────────────────────────────┘
```

**关键设计决策**：
1. 不修改 OpenClaw 核心代码
2. 创建一个 **OpenClaw Skill** 来包装我们的 Agent 系统
3. 使用 OpenClaw 的工具（web_search、web_fetch）来实现 agent 能力
4. 在 agent.json 中配置 `skills` 引用

### Step 3: 创建 OpenClaw Skill 包装器

**文件**：`~/.openclaw/clawos/skills/openclaw-agents/SKILL.md`

**功能**：
- 提供一个 CLI 命令：`/agent <task>` 或 `/ask <agent> <task>`
- 内部调用 `agent-router.js` 路由任务
- 通过 OpenClaw 的工具执行 LLM 调用
- 返回 agent 的响应

**工作流程**：
1. 接收用户请求（例如："审查服务合同"）
2. 调用 Agent Router 分析任务
3. 获取路由结果（例如：LegalAgent）
4. 加载 agent 的 prompt.md 和 agent.json
5. 通过 OpenClaw 的 agent runtime 执行（使用配置的模型）
6. 返回响应给用户

### Step 4: 更新 Agent 配置

**更新 `agent.json`**：
- 移除当前的模拟执行逻辑
- 添加 OpenClaw 工具引用
- 配置模型使用 OpenClaw 的模型引用

**示例配置**：
```json
{
  "id": "legalagent",
  "model": {
    "primary": "anthropic/claude-opus-4-5",  // 使用 OpenClaw 模型格式
    "provider": "anthropic"
  },
  "skills": [
    "web_search",    // OpenClaw 内置工具
    "web_fetch"
  ]
}
```

### Step 5: 创建 OpenClaw 配置

**更新 `~/.openclaw/clawos/openclaw.json`**：

**选项 A：单个 agent，使用 skill 路由**
```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/clawos/workspace",
      model: {
        primary: "zai/glm-4.7",
        fallbacks: ["opencode/glm-4.7-free", "opencode/kimi-k2.5-free"]
      }
    }
  },
  skills: {
    managed: {
      "openclaw-agents": {
        enabled: true
      }
    }
  }
}
```

**选项 B：多个 agents，每个 agent 一个 workspace**
```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/clawos/workspace" },
      { id: "devagent", workspace: "~/.openclaw/clawos/workspace-dev" },
      { id: "legalagent", workspace: "~/.openclaw/clawos/workspace-legal" },
      { id: "researchagent", workspace: "~/.openclaw/clawos/workspace-research" }
    ],
    defaults: {
      model: {
        primary: "zai/glm-4.7"
      }
    }
  },
  bindings: [
    // 通过 @mention 或 /命令 路由到特定 agents
  ]
}
```

### Step 6: 实现真实 LLM 调用层

**问题**：当前 `task-dispatcher.js` 是模拟执行

**解决方案**：
- 创建 `llm-executor.js`：通过 OpenClaw 工具调用 LLM
- 或直接使用 OpenClaw 的 agent runtime（推荐）

**推荐方案**：让 OpenClaw 的 agent runtime 处理 LLM 调用
- Skill 只负责路由和上下文管理
- 实际的 LLM 调用由 OpenClaw pi-mono 完成

### Step 7: 测试和验证

**测试场景**：
1. [ ] 单 agent 路由："创建一个 API" → DevAgent
2. [ ] 单 agent 路由："审查合同" → LegalAgent
3. [ ] 单 agent 路由："研究 AI 趋势" → ResearchAgent
4. [ ] 并行投票：高风险任务 → 3 agents 投票
5. [ ] 顺序链：代码 + 法律审查
6. [ ] 工具调用：web_search、web_fetch

**性能指标**：
- 响应延迟
- Token 使用量
- 成本分析
- 成功率

## 实施优先级

### P0 (立即实施)
- [ ] 创建 OpenClaw Skill 包装器 (`openclaw-agents`)
- [ ] 测试基本路由功能
- [ ] 验证 3 个 agents 的独立工作

### P1 (短期)
- [ ] 实现并行投票模式
- [ ] 实现顺序链模式
- [ ] 添加监控和指标收集

### P2 (中期)
- [ ] 性能优化
- [ ] 成本分析
- [ ] 完整的集成测试

## 关键挑战

### 1. Agent 执行上下文
- 如何将 agent 的 prompt 注入到 OpenClaw 的上下文？
- 解决：使用 OpenClaw 的 workspace bootstrap 文件

### 2. 模型配置
- DevAgent 需要 Claude 3.5 Sonnet
- LegalAgent 需要 GPT-4o
- ResearchAgent 需要 Claude Opus 4.5
- 当前只配置了 opencode 模型
- 解决：需要添加 OpenAI 和 Anthropic OAuth/API 配置

### 3. 工具调用
- agents 需要调用 web_search、web_fetch
- 需要确保工具权限正确配置
- 解决：在 skill 配置中启用工具

### 4. 会话管理
- 每个 agent 需要独立的会话
- 需要跟踪 agent 之间的上下文传递
- 解决：使用 OpenClaw 的 sessions_send

## 技术细节

### Skill 结构
```
~/.openclaw/clawos/skills/openclaw-agents/
├── SKILL.md              # Skill 定义
├── index.js             # 主逻辑
├── agent-router.js       # 从 workspace/agents/ 复制
├── task-dispatcher.js   # 从 workspace/agents/ 复制
├── context-manager.js   # 从 workspace/agents/ 复制
├── config.json          # Skill 配置
└── tests/              # Skill 测试
```

### 命令接口
```
/agent <task>          # 自动路由到合适的 agent
/agent dev <task>       # 强制使用 DevAgent
/agent legal <task>     # 强制使用 LegalAgent
/agent research <task>  # 强制使用 ResearchAgent
/agent status          # 显示 agents 健康状态
/agent list            # 列出所有 agents
```

## 下一步行动

1. 创建 `~/.openclaw/clawos/skills/openclaw-agents/` 目录
2. 实现 SKILL.md 和 index.js
3. 测试基本功能
4. 迭代改进

---

**版本**：1.0
**状态**：规划阶段
**预计时间**：2-3 小时
