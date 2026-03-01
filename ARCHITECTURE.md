# ClawOS 架构规范

> 版本: 2026.3 | 更新: 2026-03-01

---

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                  🧠 大脑 (GitHub)                        │
│         clawos-federation/clawos-brain                  │
│         clawos-federation/clawos-blackboard             │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│ 🏰 Mac mini 司令部   │       │ ⚔️ Alpha 方面军          │
│ ~/.openclaw/        │       │ /Volumes/LEGION/        │
│ (394MB)             │       │ clawos-alpha (139MB)    │
│                     │       │                         │
│ • Federation GM     │◄─────►│ • alpha-commander       │
│ • Local GM          │  同步  │ • risk-controller       │
│ • PMs + Workers     │       │ • 量化交易 (隔离)        │
└─────────────────────┘       └─────────────────────────┘
```

---

## 位置说明

### 1. 大脑 (GitHub)

| 仓库 | 用途 |
|------|------|
| `clawos-federation/clawos-brain` | 共享记忆、进化引擎 |
| `clawos-federation/clawos-blackboard` | 任务通信、实时状态 |
| `clawos-federation/clawos-alpha` | Alpha 方面军代码 |
| `clawos-federation/clawos-node-*` | 各节点配置 |

### 2. Mac mini 司令部

| 路径 | 用途 |
|------|------|
| `~/.openclaw/config.json` | 主节点配置 |
| `~/.openclaw/clawos/` | 本地工作目录 |
| `~/.openclaw/clawos/CLAUDE.md` | L0 指挥官协议 |
| `~/.openclaw/clawos/brain/` | 本地大脑 (从 GitHub 同步) |
| `~/.openclaw/clawos/blackboard/` | 本地黑板 (从 GitHub 同步) |

### 3. Alpha 方面军

| 路径 | 用途 |
|------|------|
| `/Volumes/LEGION/clawos-alpha/` | 量化系统主目录 |
| `/Volumes/LEGION/clawos-alpha/backtest/` | 回测引擎 |
| `/Volumes/LEGION/clawos-alpha/strategies/` | 策略库 |
| `/Volumes/LEGION/clawos-alpha/blackboard/` | Alpha 黑板 |

**特性:**
- 隔离运行 (risk-controller 必需)
- 可离线运行
- 外接硬盘大容量存储

### 4. 旧系统备份 (保留)

| 路径 | 状态 |
|------|------|
| `/Volumes/LEGION/openclaw-system/` (958MB) | 归档备份，暂不处理 |

---

## 节点配置

### Mac mini (司令部)

```json
{
  "node_id": "mac-mini",
  "type": "federation-head",
  "port": 18789,
  "federation": {
    "role": "head",
    "brain_source": "github:clawos-federation/clawos-brain",
    "blackboard_source": "github:clawos-federation/clawos-blackboard"
  }
}
```

### Alpha (方面军)

```json
{
  "node_id": "alpha",
  "type": "specialized",
  "port": 18790,
  "federation": {
    "role": "member",
    "head_node": "mac-mini:18789"
  },
  "security": {
    "isolated": true,
    "risk_controller_required": true
  }
}
```

---

## 同步机制

```bash
# Mac mini: 从 GitHub 同步大脑
cd ~/.openclaw/clawos/brain && git pull

# Mac mini: 从 GitHub 同步黑板
cd ~/.openclaw/clawos/blackboard && git pull

# Alpha: 从 GitHub 同步
cd /Volumes/LEGION/clawos-alpha && git pull
```

---

## 使用方式

```bash
# 启动 OpenCode (任意目录)
cd ~ && opencode

# 调度任务
openclaw agent --agent gm --task "[任务描述]"

# 查看 Alpha 战报
ls /Volumes/LEGION/clawos-alpha/blackboard/alpha/reports/
```

---

## 目录结构

```
~/.openclaw/
├── config.json              # Mac mini 主节点配置
├── clawos/                  # 本地工作目录
│   ├── CLAUDE.md            # L0 指挥官协议
│   ├── brain/               # 大脑 (GitHub 同步)
│   ├── blackboard/          # 黑板 (GitHub 同步)
│   ├── workspace/           # 工作区
│   └── code/                # 代码
├── agents/                  # Agent 配置
├── memory/                  # 记忆存储
└── credentials/             # 凭证

/Volumes/LEGION/clawos-alpha/
├── openclaw.json            # Alpha 配置
├── backtest/                # 回测引擎
├── strategies/              # 策略库
├── blackboard/              # Alpha 黑板
├── souls/                   # Agent 灵魂
├── skills/                  # 技能
└── scripts/                 # 脚本
```

---

## 清理记录 (2026-03-01)

| 操作 | 状态 |
|------|------|
| 删除 `~/clawos-alpha` | ✅ |
| 删除 `~/clawos-federation` | ✅ |
| 删除 `~/clawos-node-alpha` | ✅ |
| 清理备份文件 | ✅ |
| 更新路径引用 | ✅ |
| 配置 Git 关联 | ✅ |
