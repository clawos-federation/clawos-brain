# ClawOS 联邦：公共 vs 个性

**更新时间**: 2026-02-27 09:42

---

## 一图看清

```
┌─────────────────────────────────────────────────────────────┐
│                        公共层                                │
│  (所有节点共享，存 GitHub)                                    │
├─────────────────────────────────────────────────────────────┤
│  clawos-core     │ 框架、协议、工作流                          │
│  clawos-souls    │ Agent 人格模板                             │
│  clawos-brain    │ 黑板、记忆、决策                            │
│  clawos-actions  │ 自动化任务                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        个性层                                │
│  (每个节点独立，不同步)                                        │
├─────────────────────────────────────────────────────────────┤
│  openclaw.json   │ 节点配置（硬件、网络）                       │
│  .env / secrets  │ API 密钥、敏感数据                          │
│  logs/           │ 运行日志                                   │
│  heartbeat       │ 实时状态                                   │
│  本地缓存         │ 临时文件                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 详细分类

### 🟢 公共（同步）

| 类别 | 文件/目录 | 说明 | 存储位置 |
|------|-----------|------|----------|
| **框架** | `lib/`, `scripts/` | 核心代码 | clawos-core |
| **协议** | `protocols/` | Agent 协作规则 | clawos-core |
| **工作流** | `workflows/` | 任务流程 | clawos-core |
| **人格** | `souls/*.md` | Agent SOUL | clawos-souls |
| **黑板** | `blackboard/` | 共享状态 | clawos-brain |
| **记忆** | `memory/` | 长期记忆 | clawos-brain |
| **报告** | `reports/` | 进化报告 | clawos-brain |
| **决策** | `gm/decisions.md` | GM 决策 | clawos-brain |

**特点**：
- 任何节点修改 → 其他节点受益
- 版本控制 → 可回滚
- 冲突 → Git 合并

---

### 🔴 个性（不同步）

| 类别 | 文件/目录 | 说明 | 为什么不同步 |
|------|-----------|------|--------------|
| **节点配置** | `openclaw.json` | 硬件、网络 | 每个节点硬件不同 |
| **密钥** | `.env`, secrets | API keys | 安全考虑 |
| **实时状态** | `heartbeat-state.json` | 心跳 | 节点专属 |
| **日志** | `logs/` | 运行日志 | 节点专属 |
| **临时文件** | `*.tmp`, `cache/` | 缓存 | 不需要同步 |
| **工作空间** | `workspaces/` | Agent 工作目录 | 本地文件 |

**特点**：
- 节点独立管理
- 不影响其他节点
- 不进入 Git

---

## 边界案例（需决策）

| 类别 | 文件/目录 | 当前状态 | 建议 |
|------|-----------|----------|------|
| **任务目录** | `tasks/{taskId}/` | 同步 | 保持同步 |
| **节点状态** | `shared/node-status.json` | 同步 | 只读同步 |
| **用户配置** | `USER.md`, `IDENTITY.md` | 不同步 | 可选同步 |
| **本地工具** | `TOOLS.md` | 不同步 | 不同步 |

---

## 节点角色 vs 公共角色

```
公共角色（所有节点都能用）:
├── GM          ← clawos-souls/gm/SOUL.md
├── Validator   ← clawos-souls/validator/SOUL.md
├── coding-pm   ← clawos-souls/coding-pm/SOUL.md
├── writing-pm  ← clawos-souls/writing-pm/SOUL.md
└── ...

节点专属角色:
├── Mac mini:   assistant (主), platform-pm
├── MacBook:    coder-frontend, coder-backend
├── Codespace:  alpha-bridge
└── Writing:    writer-general
```

**规则**：
- SOUL 模板是公共的
- 哪个节点加载哪个角色是个性的

---

## 实际例子

### 主脑 (Mac mini)

```
公共（从 GitHub pull）:
├── clawos-core/       ← 框架
├── clawos-souls/      ← 人格
└── clawos-brain/      ← 黑板+记忆

个性（本地）:
├── openclaw.json      ← "我是主脑，16GB 内存"
├── .env               ← API keys
└── logs/              ← 我的运行日志
```

### MacBook

```
公共（从 GitHub pull）:
├── clawos-core/       ← 相同框架
├── clawos-souls/      ← 相同人格
└── clawos-brain/      ← 相同黑板

个性（本地）:
├── openclaw.json      ← "我是 MacBook，移动节点"
├── .env               ← 我的 API keys
└── logs/              ← 我的运行日志
```

---

## 同步规则总结

| 同步方向 | 内容 | 触发 |
|----------|------|------|
| 本地 → GitHub | blackboard/ | 手动或定时 (15m) |
| 本地 → GitHub | 记忆/决策 | 手动或定时 (15m) |
| GitHub → 本地 | 框架更新 | 手动或定时 (1h) |
| GitHub → 本地 | 人格更新 | 手动或定时 (1h) |
| **不同步** | 密钥/日志/配置 | 永不 |

---

## 一句话总结

> **公共 = 所有节点共享的"大脑"**
> **个性 = 每个节点自己的"身体"**

---

🦞 ClawOS Federation
