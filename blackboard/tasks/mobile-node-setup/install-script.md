# MacBook 节点配置脚本

**节点ID**: mobile
**生成时间**: 2026-02-26 09:41

---

## 📱 一键安装指令

在 MacBook 上执行：

```bash
# 1. 安装 OpenClaw
brew install openclaw

# 2. 初始化节点
openclaw init --node mobile --federation ClawOS

# 3. 配置工作空间
mkdir -p ~/clawos/workspaces
cd ~/clawos/workspaces

# 4. 创建 IDENTITY.md
cat > IDENTITY.md << 'EOF'
# IDENTITY.md

- **Name:** ClawOS Mobile
- **Node ID:** mobile
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
- **Emoji:** 📱
EOF

# 5. 配置 Federation 连接
mkdir -p ~/clawos/config
cat > ~/clawos/config/federation.json << 'EOF'
{
  "nodeId": "mobile",
  "federation": "ClawOS",
  "brain": {
    "url": "http://dongsheng-mac-mini.local:3000",
    "token": "MOBILE_TOKEN_PLACEHOLDER"
  },
  "sync": {
    "blackboard": "~/clawos/blackboard/",
    "memory": "~/clawos/memory/"
  },
  "agents": ["assistant", "platform-pm", "connector-research"],
  "model": "zai/glm-5"
}
EOF

# 6. 创建 Blackboard 目录
mkdir -p ~/clawos/blackboard/{tasks,gm,shared,roles}

# 7. 创建记忆目录
mkdir -p ~/clawos/memory

# 8. 测试连接
openclaw status
```

---

## 🔑 Token 获取

**从主脑获取 Token**：

在 Mac mini 上执行：
```bash
# 生成 token
openclaw federation token generate --node mobile

# 输出示例：
# FED_TOKEN_mobile_x7k2m9p4q1
```

然后在 MacBook 上替换 `MOBILE_TOKEN_PLACEHOLDER`。

---

## ✅ 验证清单

安装后验证：

```bash
# 1. 检查 OpenClaw 版本
openclaw --version

# 2. 检查节点状态
openclaw status

# 3. 测试主脑连接
openclaw federation ping

# 4. 检查 Blackboard
ls ~/clawos/blackboard/

# 5. 检查记忆
ls ~/clawos/memory/
```

---

## 🔄 同步机制

### Blackboard 同步

```bash
# 手动同步（首次）
openclaw blackboard sync --from brain

# 自动同步（配置后）
# 每小时自动同步
```

### 记忆同步

```bash
# 拉取主脑记忆
openclaw memory pull

# 推送本地记忆
openclaw memory push
```

---

## 📋 Agent 配置

### mobile 节点的 Agents

| Agent | 职责 | 模型 |
|-------|------|------|
| **assistant** | 用户交互 | GLM-5 |
| **platform-pm** | 平台维护 | GLM-5 |
| **connector-research** | 信息整合 | GLM-5 |

### 启动 Agent

```bash
# 启动 assistant
openclaw agent start assistant

# 查看运行状态
openclaw agent status
```

---

## 🎯 首次任务

配置完成后，测试任务：

```bash
# 在 MacBook 上对 assistant 说：
"测试移动节点连接"

# 预期响应：
"移动节点 (mobile) 已连接到 ClawOS Federation"
```

---

## 🔧 高级配置（可选）

### 配置 iMessage 通知

```bash
# 在 MacBook 上配置
openclaw notify config imessage --enable

# 测试
openclaw notify test "MacBook 节点上线"
```

### 配置自动上线

```bash
# 开机自动启动 OpenClaw
openclaw autostart enable
```

---

## 🚨 故障排查

### 连接失败

```bash
# 检查网络
ping dongsheng-mac-mini.local

# 检查端口
nc -zv dongsheng-mac-mini.local 3000

# 查看日志
openclaw logs --tail 100
```

### Token 无效

```bash
# 在主脑重新生成
openclaw federation token regenerate --node mobile

# 在 MacBook 更新
# 编辑 ~/clawos/config/federation.json
```

---

**Status**: ✅ 配置指令已生成
**下一步**: 用户在 MacBook 上执行指令
