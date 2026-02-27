# ClawOS 移动节点配置清单

**节点ID**: mobile
**设备**: MacBook
**状态**: 🚧 配置中

---

## ✅ 配置清单

### 在主脑 (Mac mini) 上完成

- [ ] 更新 `config/meta.json`，添加 mobile 节点
- [ ] 生成 Federation Token
- [ ] 配置 Blackboard 共享权限

### 在 MacBook 上完成

- [ ] 安装 OpenClaw
- [ ] 创建节点工作空间
- [ ] 配置 IDENTITY.md
- [ ] 配置 federation.json
- [ ] 测试连接

---

## 实施步骤

### Step 1: 主脑配置

我将执行以下操作：

1. 更新 meta.json 添加 mobile 节点
2. 生成 token
3. 提供 MacBook 配置指令

### Step 2: MacBook 安装

你需要提供：
- MacBook 的 IP 地址或主机名
- 或者直接在 MacBook 上执行命令

---

## 配置详情

### mobile 节点配置

```json
{
  "id": "mobile",
  "name": "移动节点",
  "device": "MacBook",
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
```

---

**Status**: ⏳ 等待 MacBook 访问方式
