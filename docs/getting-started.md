# ClawOS 入门指南

欢迎使用 ClawOS - 你的个人 AI 多代理系统！

## 快速开始

### 1. 启动 ClawOS 会话

```bash
# 在终端启动
openclaw

# 或者使用特定 agent
openclaw --agent assistant
```

首次启动时，ClawOS 会自动：
- 加载默认 Agent (assistant)
- 初始化记忆系统
- 连接配置的消息渠道（Telegram/Discord/iMessage 等）

### 2. 基本交互

**发送消息**：直接输入文字，按 Enter 发送

**常用命令**：
- `/status` - 查看当前会话状态
- `/help` - 显示帮助信息
- `/clear` - 清除对话历史
- `/exit` - 退出会话

**示例对话**：
```
你: 帮我写一个 Python 函数计算斐波那契数列
ClawOS: [调用 coding-pm]
已创建文件: fib.py
[显示代码]
```

---

## 黑板系统

ClawOS 的核心是 **黑板 (Blackboard)** - 一个所有 Agent 共享的工作空间。

### 黑板位置

```
~/clawos/blackboard/
├── shared/         # 共享上下文
├── tasks/          # 任务状态
├── gm/             # GM 决策日志
├── reports/        # 进化报告
└── proposals/      # 改进提案
```

### 如何使用黑板

**查看共享状态**：
```bash
cat ~/clawos/blackboard/shared/evolution-status-latest.md
```

**查看任务进度**：
```bash
ls ~/clawos/blackboard/tasks/
```

**提交提案**：
```bash
echo "# 新功能提案..." > ~/clawos/blackboard/proposals/my-proposal.md
```

### 黑板自动同步

如果你的 ClawOS 配置了联邦模式，黑板会自动同步到 GitHub：

```bash
# 手动同步
~/clawos/scripts/sync-brain.sh push  # 推送到 GitHub
~/clawos/scripts/sync-brain.sh pull  # 从 GitHub 拉取
```

---

## 多 Agent 协作

ClawOS 使用**层级调度**实现多 Agent 协作：

```
Command Layer (决策层)
├── assistant  - 你的个人助理
├── gm         - 总经理，分配任务
└── validator  - 质量验证

PM Layer (管理层)
├── coding-pm   - 开发任务协调
├── writing-pm  - 写作任务协调
├── research-pm - 调研任务协调
└── platform-pm - 运维任务协调

Worker Layer (执行层)
├── coder-frontend
├── coder-backend
├── writer-general
└── ...
```

### 任务如何流转

```
你: "帮我实现一个登录功能"
    ↓
assistant 接收 → 分析是开发任务
    ↓
调用 gm → 分配给 coding-pm
    ↓
coding-pm → 调用 coder-backend
    ↓
执行 → 返回结果给你
```

### 最佳实践

**1. 明确任务类型**

| 你说 | Agent 理解 |
|------|-----------|
| "写个功能" | coding-pm |
| "写篇文章" | writing-pm |
| "查一下" | research-pm |
| "部署到" | platform-pm |

**2. 提供足够上下文**

❌ 不好：
```
"修一下 bug"
```

✅ 好：
```
"修复登录页面的 bug：用户名包含特殊字符时会崩溃"
```

**3. 利用记忆系统**

ClawOS 会记住重要信息：
```
你: "我正在开发一个电商网站"
ClawOS: [记录到记忆]
...
你: "帮我加个购物车"
ClawOS: [理解上下文] 为你的电商网站添加购物车功能...
```

---

## 记忆系统

ClawOS 有四层记忆：

| 层级 | 位置 | 持久性 |
|------|------|--------|
| 会话记忆 | 对话中 | 会话内 |
| 每日记忆 | `memory/YYYY-MM-DD.md` | 当天 |
| 角色记忆 | `workspaces/{agent}/memory/` | 永久 |
| 进化记忆 | `MEMORY.md` | 永久 |

### 查看记忆

```bash
# 查看长期记忆
cat ~/clawos/workspaces/MEMORY.md

# 查看今日记忆
cat ~/clawos/workspaces/memory/$(date +%Y-%m-%d).md
```

---

## 常见场景

### 场景 1：开发新功能

```
你: 帮我在 clawos-core 里添加一个日志清理脚本

ClawOS:
1. [GM 分配] → coding-pm
2. [coding-pm] → 设计方案
3. [coder-backend] → 编写代码
4. [validator] → 验证质量
5. [返回] 脚本已创建在 scripts/clean-logs.sh
```

### 场景 2：写文档

```
你: 为 API 写一份使用文档

ClawOS:
1. [GM 分配] → writing-pm
2. [writing-pm] → 生成文档
3. [返回] 文档已创建在 docs/api.md
```

### 场景 3：系统维护

```
你: 检查一下系统健康状态

ClawOS:
1. [platform-pm] → 运行检查
2. [返回] 报告：
   - 磁盘使用: 45%
   - 内存: 12GB/16GB
   - Agent 状态: 全部正常
```

---

## 高级功能

### 自定义 Agent

在 `~/clawos/workspaces/` 创建新的 Agent 工作空间：

```bash
mkdir -p ~/clawos/workspaces/my-agent
cd ~/clawos/workspaces/my-agent

# 创建 SOUL 文件
cat > SOUL.md << 'EOF'
# My Custom Agent

你是一个专门处理 [特定任务] 的 Agent。

## 能力
- 能力 1
- 能力 2
EOF
```

### 配置定时任务

```bash
# 在 openclaw.json 中配置 heartbeat
{
  "agents": {
    "list": [{
      "id": "my-agent",
      "heartbeat": {
        "every": "1h",
        "prompt": "检查 xxx 并报告"
      }
    }]
  }
}
```

### 联邦模式

配置多个节点协同工作：

```bash
# 节点配置
openclaw config set federation.enabled true
openclaw config set federation.brain clawos-federation/clawos-brain
```

---

## 故障排查

### Agent 不响应

```bash
# 检查状态
openclaw status

# 重启
openclaw gateway restart
```

### 记忆丢失

```bash
# 检查记忆文件
ls ~/clawos/workspaces/memory/

# 手动添加记忆
echo "重要信息: ..." >> ~/clawos/workspaces/MEMORY.md
```

### 同步失败

```bash
# 检查 Git 状态
cd ~/clawos-brain
git status

# 强制同步
~/clawos/scripts/sync-brain.sh push
```

---

## 下一步

- 📖 阅读 [ClawOS 架构文档](../architecture/README.md)
- 🦞 加入 [Discord 社区](https://discord.com/invite/clawd)
- 🔧 探索 [GitHub 仓库](https://github.com/clawos-federation)
- 📚 查看 [更多文档](https://docs.openclaw.ai)

---

**有问题？** 直接问 ClawOS："我有个问题..."

🦞 **ClawOS - 让 AI 帮你完成更多**
