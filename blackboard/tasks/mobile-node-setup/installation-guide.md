# MacBook 移动节点 - 安装指令

**节点ID**: mobile
**主脑**: Mac mini (当前机器)
**状态**: 📋 配置已准备

---

## 🚀 安装步骤（在 MacBook 上执行）

### 1. 安装 OpenClaw

```bash
# 方法 A: Homebrew（推荐）
brew install openclaw

# 方法 B: npm
npm install -g openclaw
```

### 2. 初始化工作空间

```bash
# 创建工作空间
mkdir -p ~/clawos/workspaces
cd ~/clawos/workspaces

# 初始化
openclaw init
```

### 3. 创建节点身份

创建 `~/clawos/workspaces/IDENTITY.md`：

```bash
cat > ~/clawos/workspaces/IDENTITY.md << 'EOF'
# IDENTITY.md - 移动节点

- **Name:** ClawOS Mobile
- **Node ID:** mobile
- **Creature:** ClawOS 节点实例
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
- **Emoji:** 📱
- **Vibe:** 灵活、快速、随时在线
EOF
```

### 4. 创建用户配置

创建 `~/clawos/workspaces/USER.md`：

```bash
cat > ~/clawos/workspaces/USER.md << 'EOF'
# USER.md - About Your Human

- **Name:** Dongsheng Lu
- **What to call them:** dongsheng
- **Pronouns:** he/him
- **Timezone:** Asia/Shanghai
- **Notes:** ClawOS 创造者

## Context

- 移动办公场景
- 随时响应需求
- 协调其他节点工作
EOF
```

### 5. 创建 Federation 配置

创建 `~/clawos/config/federation.json`：

```bash
mkdir -p ~/clawos/config

cat > ~/clawos/config/federation.json << 'EOF'
{
  "nodeId": "mobile",
  "nodeName": "移动节点",
  "federation": "ClawOS",
  "brain": {
    "nodeId": "server",
    "blackboard": "cloudflare-r2://clawos-blackboard",
    "memory": "github://clawos-federation/memory"
  },
  "sync": {
    "interval": "5min",
    "blackboard": true,
    "memory": true
  },
  "agents": ["assistant", "platform-pm", "connector-research"],
  "model": "zai/glm-5"
}
EOF
```

### 6. 创建本地 Blackboard

```bash
mkdir -p ~/clawos/blackboard/{tasks,gm,shared,reports}
```

### 7. 测试连接

```bash
# 检查 OpenClaw 状态
openclaw status

# 测试 Federation 连接（需要主脑在线）
openclaw federation ping
```

---

## 📋 主脑端配置（已完成）

✅ 已在 Mac mini 的 `config/meta.json` 中添加 mobile 节点配置

---

## 🔄 同步机制

### Blackboard 同步

```
MacBook 写入 → ~/clawos/blackboard/
                ↓
        Cloudflare R2 (云存储)
                ↓
Mac mini 读取 ← ~/clawos/blackboard/
```

### 记忆同步

```
MacBook 任务 → EverMemOS → GitHub memory 分支
                              ↓
Mac mini 每天 ← ← ← ← ← ← ← ←
```

---

## 🎯 节点能力

移动节点可以：

| 能力 | 说明 |
|------|------|
| **快速响应** | 随时处理轻量级任务 |
| **信息收集** | 调研、汇总数据 |
| **协调节点** | 调用其他专业节点 |
| **个人助理** | 日程、提醒、整理 |

---

## ⚠️ 注意事项

1. **模型选择**：默认用 GLM-5（便宜、快速）
2. **在线时间**：on-demand（按需启动）
3. **成本预估**：~$3-5/月

---

## 🚀 快速开始

在 MacBook 上复制粘贴执行：

```bash
# 完整安装脚本
brew install openclaw && \
mkdir -p ~/clawos/{workspaces,config,blackboard/{tasks,gm,shared,reports}} && \
cd ~/clawos/workspaces && \
openclaw init

# 然后手动创建 IDENTITY.md, USER.md, federation.json
```

---

**Status**: 📋 指令已准备，等待在 MacBook 上执行
