# OpenClaw Agents Skill

专业的 Agent 路由和执行系统，支持 DevAgent、LegalAgent、ResearchAgent 等专业 agents。

## Description

此 skill 提供了一个智能 agent 路由和执行系统，可以将用户的任务自动路由到最合适的专业 agent，并通过 OpenClaw 的 runtime 执行。

## Features

- **智能路由**：自动分析任务关键词、复杂度和风险，选择最合适的 agent
- **多 agent 协作**：支持单 agent、并行投票、顺序链三种协作模式
- **中英文支持**：同时支持中英文任务输入
- **质量保证**：每个 agent 都有 7.0 的质量阈值和自动自我批判

## Agents

| Agent | 主模型 | 专长 |
|--------|---------|-------|
| **DevAgent** | claude-3.5-sonnet | 代码生成、bug 修复、测试、重构 |
| **LegalAgent** | gpt-4o | 法律分析、合同审查、合规检查 |
| **ResearchAgent** | claude-opus-4-5 | 深度研究、数据分析、趋势预测 |

## Usage

### 自动路由（推荐）

```
/agent <task>
```

示例：
```
/agent 审查服务合同
/agent 创建一个用户认证 API
/agent 研究人工智能最新趋势
```

### 指定 agent

```
/agent dev <task>          # 使用 DevAgent
/agent legal <task>        # 使用 LegalAgent
/agent research <task>       # 使用 ResearchAgent
```

### 管理命令

```
/agent status          # 显示 agents 健康状态
/agent list            # 列出所有 agents
/agent health dev       # 检查特定 agent 状态
```

## Collaboration Modes

### Single Agent（单 agent）
适用于简单任务，自动选择最匹配的 agent。

```
/agent 修复 API bug
```

### Parallel Voting（并行投票）
适用于高风险任务，3 个 agents 同时执行并投票。

```
/agent [high-risk] 评估技术方案的风险
```

### Sequential Chain（顺序链）
适用于多阶段任务，agents 按顺序执行。

```
/agent [chain] 开发并审查支付系统
```

## Configuration

Skill 会自动从 `~/.openclaw/workspace/agents/` 加载：

- `registry.json` - Agent 注册表
- `agent-router.js` - 智能路由器
- `task-dispatcher.js` - 任务分发器
- `context-manager.js` - 上下文管理器
- `agent-monitor.js` - 监控和指标
- `devagent/`, `legalagent/`, `researchagent/` - 专业 agents

## Requirements

- OpenClaw workspace at `~/.openclaw/workspace/agents/`
- Web search tools (web_search, web_fetch) enabled
- Models configured:
  - `claude-3.5-sonnet` for DevAgent
  - `gpt-4o` for LegalAgent
  - `claude-opus-4-5` for ResearchAgent

## Notes

- 首次使用会自动创建 workspace 结构
- 所有 agent 执行都通过 OpenClaw 的 agent runtime
- 工具调用（web_search、web_fetch）需要相应权限
- 建议为每个 agent 配置不同的 workspace 以实现完全隔离

## Examples

### 代码开发
```
/agent 创建一个 RESTful API 端点，支持 JWT 认证
```
→ DevAgent 处理，使用 claude-3.5-sonnet

### 法律审查
```
/agent legal 审查这份服务合同，识别潜在风险
```
→ LegalAgent 处理，使用 gpt-4o

### 深度研究
```
/agent research 研究 2025 年 AI 行业的最新趋势和竞争格局
```
→ ResearchAgent 处理，使用 claude-opus-4-5

### 并行协作
```
/agent [vote] 评估这个架构方案的可行性和风险
```
→ DevAgent、LegalAgent、ResearchAgent 同时执行并投票

## Troubleshooting

### Agent not found
确保 `~/.openclaw/workspace/agents/registry.json` 存在且包含 agent。

### Tool access denied
在 `~/.openclaw/openclaw.json` 中确保启用了 web_search 和 web_fetch 工具。

### Model not available
确保在 `~/.openclaw/agents/<agentId>/auth-profiles.json` 中配置了相应的 model 提供商。
