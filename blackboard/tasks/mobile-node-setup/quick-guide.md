# MacBook 配置指南

**时间**: 2026-02-26 19:58
**状态**: ✅ 准备就绪

---

## 快速配置（3 步）

### 步骤 1: 在 MacBook 上执行

复制以下命令，在 MacBook 终端粘贴执行：

```bash
# 创建目录和基础文件
mkdir -p ~/clawos/{workspaces,config,blackboard/{tasks,gm,shared,roles},memory,logs}

# 创建 IDENTITY.md
cat > ~/clawos/workspaces/IDENTITY.md << 'EOF'
# IDENTITY.md

- **Name:** ClawOS Mobile
- **Node ID:** mobile
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
- **Emoji:** 📱
EOF

# 创建 USER.md
cat > ~/clawos/workspaces/USER.md << 'EOF'
# USER.md

- **Name:** Dongsheng Lu
- **What to call them:** dongsheng
- **Timezone:** Asia/Shanghai
EOF

# 创建 MEMORY.md
cat > ~/clawos/workspaces/MEMORY.md << 'EOF'
# MEMORY.md

## 关于人类
- **名字:** Dongsheng Lu
- **称呼:** dongsheng

## 关于我
- **名字:** ClawOS Mobile
- **身份:** 移动办公节点

## 黄金规则
1. 随时沟通
2. 子任务不等待
3. 不沉默
EOF

echo "✅ 基础配置完成"
```

---

### 步骤 2: 在主脑生成 token

在 Mac mini 上执行：

```bash
# 生成 token
openclaw federation token generate --node mobile

# 会输出类似：
# FED_TOKEN_mobile_x7k2m9p4q1
```

**记录这个 token**。

---

### 步骤 3: 在 MacBook 上配置 Federation

在 MacBook 上创建 federation.json：

```bash
# 创建 federation.json
cat > ~/clawos/config/federation.json << EOF
{
  "nodeId": "mobile",
  "federation": "ClawOS",
  "brain": {
    "url": "http://dongsheng-mac-mini.local:3000",
    "token": "这里粘贴刚才生成的 token"
  },
  "sync": {
    "blackboard": "~/clawos/blackboard/",
    "memory": "~/clawos/memory/"
  },
  "agents": ["assistant", "platform-pm", "connector-research"],
  "model": "zai/glm-5"
}
EOF

echo "✅ Federation 配置完成"
```

---

## 验证

在 MacBook 上执行：

```bash
# 测试网络
ping dongsheng-mac-mini.local

# 安装 OpenClaw（如果还没装）
brew install openclaw

# 测试连接
openclaw federation ping
```

---

## 测试对话

在 MacBook 上对 assistant 说：

```
"你好，测试移动节点"
```

预期响应：

```
移动节点 (mobile) 已上线！
当前节点: MacBook
主脑状态: 已连接
```

---

## ⏱️ 预计时间

- 步骤 1: 1 分钟
- 步骤 2: 1 分钟
- 步骤 3: 1 分钟
- **总计**: 3 分钟

---

## 🚨 故障排查

### 问题 1: ping 不通

**解决**:
- 确认 MacBook 和 Mac mini 在同一网络
- 确认 Mac mini 防火墙允许连接
- 尝试用 IP 地址代替主机名

### 问题 2: token 无效

**解决**:
- 在主脑重新生成 token
- 确认复制时没有多余空格

### 问题 3: OpenClaw 未安装

**解决**:
```bash
brew install openclaw
openclaw init --node mobile
```

---

**状态**: ✅ 准备就绪
**下一步**: 在 MacBook 上执行配置
