# 新节点配置模板

## 基本信息部分

```json
{
  "id": "{node-id}",
  "name": "{节点名称}",
  "device": "{设备类型}",
  "specialization": "{专长领域}",
  "model": "{默认模型}",
  "memory": ["SimpleMem", "EverMemOS"],
  "agents": ["{agent-1}", "{agent-2}"],
  "onlineHours": "{在线时间}"
}
```

---

## 配置选项

### 专长领域 (specialization)

| 值 | 描述 |
|-----|------|
| mobile-office | 移动办公 |
| software-engineering | 软件工程 |
| academic-writing | 学术写作 |
| quantitative-finance | 量化交易 |
| personal-assistant | 个人助理 |
| research-analysis | 研究分析 |
| data-engineering | 数据工程 |
| security-ops | 安全运维 |

### 在线时间 (onlineHours)

| 值 | 描述 |
|-----|------|
| 24/7 | 全天候 |
| workdays | 工作日 |
| market-hours | 交易时间 |
| on-demand | 按需 |

### 默认模型 (model)

| 值 | 适用场景 | 成本 |
|-----|----------|------|
| zai/glm-5 | 通用、高频 | 低 |
| openai-codex/gpt-5.3-codex | 代码任务 | 中 |
| vectorengine-claude/claude-opus-4-6-thinking | 决策、质检 | 高 |

---

## IDENTITY.md 模板

```markdown
# IDENTITY.md

- **Name:** {节点名}
- **Node ID:** {node-id}
- **Device:** {设备}
- **Role:** {角色}
- **Federation:** ClawOS
- **Emoji:** {emoji}

---

## 特点

- {特点1}
- {特点2}

## 职责

- {职责1}
- {职责2}
```

---

## federation.json 模板

```json
{
  "nodeId": "{node-id}",
  "federation": "ClawOS",
  "brain": {
    "url": "http://{主脑地址}:3000",
    "token": "{从主脑获取}"
  },
  "sync": {
    "blackboard": "~/clawos/blackboard/",
    "memory": "~/clawos/memory/"
  },
  "agents": ["{agent-1}", "{agent-2}"],
  "model": "{默认模型}"
}
```

---

## 安装步骤

1. 安装 OpenClaw: `brew install openclaw`
2. 初始化: `openclaw init --node {node-id}`
3. 配置 IDENTITY.md
4. 配置 federation.json
5. 测试连接: `openclaw federation ping`

---

**模板版本**: 1.0
**最后更新**: 2026-02-26
