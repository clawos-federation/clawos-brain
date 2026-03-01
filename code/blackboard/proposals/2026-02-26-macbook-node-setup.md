# MacBook 编程节点配置指南

**目标**: 将 MacBook 配置为 ClawOS 编程节点
**状态**: 待配置

---

## 当前设备角色

| 设备 | 节点类型 | 角色 |
|------|----------|------|
| Mac mini (当前) | 服务器节点 | Command Layer + 研究/系统 Worker |
| MacBook (待配置) | 编程节点 | 代码 Worker 矩阵 |

---

## 配置步骤

### 1. 在 MacBook 上安装 OpenClaw

```bash
# 打开 MacBook 终端
brew install openclaw

# 初始化
openclaw init
```

### 2. 配置节点身份

在 MacBook 上创建 `~/clawos/IDENTITY.md`:

```markdown
# IDENTITY.md

- **Name:** ClawOS Coding Node
- **Node ID:** coding-node
- **Device:** MacBook
- **Role:** 编程节点 (代码 Worker 矩阵)
- **Federation:** ClawOS
```

### 3. 安装代码 Worker SOUL

从 GitHub 克隆或复制:

```bash
# 在 MacBook 上
mkdir -p ~/clawos/souls/workers

# 复制以下 Worker SOUL:
# - analyst/code.soul.md
# - creator/code.soul.md
# - critic/code.soul.md
# - executor/test.soul.md (可选)
```

### 4. 注册 Worker Agents

在 MacBook 上编辑 `~/.openclaw/config/agents.json`:

```json
{
  "analyst-code": {
    "model": "openai-codex/gpt-5.3-codex",
    "soul": "souls/workers/analyst/code.soul.md"
  },
  "creator-code": {
    "model": "openai-codex/gpt-5.3-codex",
    "soul": "souls/workers/creator/code.soul.md"
  },
  "critic-code": {
    "model": "openai-codex/gpt-5.3-codex",
    "soul": "souls/workers/critic/code.soul.md"
  }
}
```

### 5. 配置 API Keys

确保 MacBook 有:

- OpenAI API Key (用于 codex 模型)
- 或 Anthropic API Key (备用)

```bash
openclaw config set auth.openai-key "sk-..."
```

### 6. 测试连接

```bash
# 在 MacBook 上测试
openclaw agent --agent creator-code -m "写一个 hello world 函数"
```

---

## 编程节点 Worker 矩阵

| Worker | 职能 | 专用领域 |
|--------|------|----------|
| analyst-code | 分析 | 代码分析、架构评估 |
| creator-code | 创造 | 代码开发、功能实现 |
| critic-code | 评审 | 代码审查、安全审计 |

---

## 下一步

1. **在 MacBook 上安装 OpenClaw** - 需要物理访问
2. **配置 API Keys** - 需要 OpenAI/Anthropic key
3. **测试 Worker** - 验证代码能力

---

**状态**: ⏳ 等待 MacBook 配置
