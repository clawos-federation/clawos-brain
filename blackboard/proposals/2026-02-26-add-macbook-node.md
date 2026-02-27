# 添加 MacBook 到 ClawOS Federation

**时间**: 2026-02-26 09:35
**设备**: MacBook (另一台)
**状态**: 🚧 待配置

---

## 节点选项

### 选项 A: 移动办公节点 (推荐)

```json
{
  "mobile": {
    "id": "mobile",
    "name": "移动节点",
    "device": "MacBook Air/Pro",
    "specialization": "mobile-office",
    "model": "zai/glm-5",
    "memory": ["SimpleMem", "EverMemOS"],
    "agents": ["assistant", "platform-pm", "connector-research"],
    "onlineHours": "on-demand",
    "features": [
      "随时响应用户需求",
      "轻量级任务处理",
      "信息收集和汇总",
      "与其他节点协作"
    ]
  }
}
```

**优点**：
- 随身携带，随时在线
- 成本低（用 GLM-5）
- 轻量级，快速响应

---

### 选项 B: 个人助理节点

```json
{
  "personal": {
    "id": "personal",
    "name": "个人助理节点",
    "device": "MacBook",
    "specialization": "personal-assistant",
    "model": "zai/glm-5",
    "memory": ["SimpleMem", "EverMemOS"],
    "agents": ["assistant", "analyst-research", "executor-test"],
    "onlineHours": "workdays",
    "features": [
      "日程管理",
      "邮件处理",
      "提醒通知",
      "信息整合"
    ]
  }
}
```

**优点**：
- 专注个人效率
- 自动化日常任务
- 整合多源信息

---

### 选项 C: 研究节点

```json
{
  "research": {
    "id": "research",
    "name": "研究节点",
    "device": "MacBook",
    "specialization": "research-analysis",
    "model": "zai/glm-5",
    "memory": ["SimpleMem", "EverMemOS", "MemOS"],
    "agents": ["research-pm", "analyst-research", "connector-research", "critic-research"],
    "onlineHours": "workdays",
    "features": [
      "信息采集",
      "数据分析",
      "报告生成",
      "趋势监控"
    ]
  }
}
```

**优点**：
- 强大的信息处理
- 支持其他节点的研究需求
- 跨节点协作

---

## 实施步骤

### 1. 在 MacBook 上安装 OpenClaw

```bash
# SSH 到 MacBook 或直接在 MacBook 上执行
brew install openclaw

# 初始化
openclaw init
```

### 2. 配置节点身份

创建 `~/clawos/workspaces/IDENTITY.md`：

```markdown
# IDENTITY.md

- **Name:** {节点名} (比如: ClawOS Mobile)
- **Node ID:** mobile
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
```

### 3. 配置 Federation 连接

编辑 `~/clawos/config/federation.json`：

```json
{
  "nodeId": "mobile",
  "federation": "ClawOS",
  "brain": {
    "url": "https://your-server-url",
    "token": "{从主脑获取}"
  },
  "sync": {
    "blackboard": "cloudflare-r2://clawos-blackboard",
    "memory": "github://clawos-federation/memory"
  }
}
```

### 4. 在主脑注册节点

在 Mac mini (当前机器) 上，更新 `config/meta.json`：

```json
{
  "nodes": {
    // ... 现有节点 ...
    "mobile": {
      "id": "mobile",
      "name": "移动节点",
      "device": "MacBook",
      // ... 配置 ...
    }
  }
}
```

### 5. 测试连接

```bash
# 在 MacBook 上测试
openclaw federation ping

# 在主脑上检查
openclaw federation status
```

---

## 同步机制

### Blackboard 共享

```
MacBook → Cloudflare R2 ← Mac mini
         (blackboard/)
```

### 记忆同步

```
MacBook 任务完成 → EverMemOS 提炼 → GitHub memory 分支
                                          ↓
Mac mini 每天拉取 ← ← ← ← ← ← ← ← ← ← ← ←
```

---

## 下一步

1. **选择节点定位** - 你想要 A/B/C 哪个？
2. **提供 MacBook 信息** - IP/SSH 访问方式？
3. **开始配置** - 我来帮你完成

---

**Status**: ⏳ 等待用户选择
