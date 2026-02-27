# ClawOS 联邦进化关系

**更新时间**: 2026-02-27 09:40

---

## 核心问题

> 主脑进化了，其他节点会怎样？

---

## 联邦架构

```
                    GitHub
                      │
         ┌────────────┼────────────┐
         │            │            │
    clawos-brain  clawos-souls  clawos-core
    (共享数据)     (人格模板)    (框架代码)
         │            │            │
         └────────────┼────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
    │主脑   │    │MacBook│    │Codespace│
    │Mac mini│    │编码   │    │量化    │
    └───┬───┘    └───┬───┘    └───┬───┘
        │             │             │
    blackboard    blackboard    blackboard
    (本地副本)    (同步副本)    (同步副本)
```

---

## 三种"进化"

### 1️⃣ 系统进化（框架级）

**发生地**: `clawos-core` 仓库

**例子**: 新增一个 PM 角色、修改工作流

**关系**:
```
主脑升级 clawos-core → push → GitHub
                              ↓
其他节点 pull ← ← ← ← ← ← ← ←
```

**结果**: 所有节点获得相同的框架升级

---

### 2️⃣ 记忆进化（知识级）

**发生地**: `clawos-brain` 仓库

**例子**: 学到新知识、任务经验、决策记录

**关系**:
```
主脑学新东西 → blackboard 写入 → sync-brain.sh push
                                      ↓
                              clawos-brain (GitHub)
                                      ↓
其他节点 sync-brain.sh pull → blackboard 更新
```

**结果**: 所有节点共享相同的知识和经验

---

### 3️⃣ 人格进化（角色级）

**发生地**: `clawos-souls` 仓库

**例子**: 优化 GM 的 SOUL、调整 PM 的行为规则

**关系**:
```
优化 SOUL → push clawos-souls
                ↓
        所有节点 clone → 使用新 SOUL
```

**结果**: 所有节点的同名 Agent 拥有相同的人格

---

## 独立部分（不同步）

| 内容 | 位置 | 原因 |
|------|------|------|
| 本地配置 | `openclaw.json` | 节点硬件不同 |
| 临时状态 | `heartbeat-state.json` | 实时变化 |
| 运行日志 | `logs/` | 节点专属 |
| 私密数据 | `.env`, secrets | 安全考虑 |

---

## 进化传播时间线

```
T0: 主脑进化（学习/升级）
    │
T+15m: 自动 sync-brain.sh push → GitHub
    │
T+30m: MacBook pull → 获得进化
    │
T+1h: Codespace pull → 获得进化
    │
T+4h: GitHub Actions 自动备份
```

---

## 冲突处理

### 场景 1: 两个节点同时修改 blackboard

```
Mac mini: 修改 gm/decisions.md → push
MacBook:  同时修改 gm/decisions.md → push (冲突!)
```

**解决**: 后 push 的需要先 pull 再 merge

### 场景 2: 节点离线期间主脑进化

```
MacBook 离线 2 天
主脑进化 10 次
MacBook 上线 → pull → 获得所有 10 次进化
```

**解决**: Git 自动合并，冲突时保留最新

---

## 理想的进化流程

```
1. 任何节点 → 进化 → 本地测试
                    ↓
2. push 到 GitHub → clawos-brain / clawos-core
                    ↓
3. GitHub Actions → 自动验证
                    ↓
4. 其他节点 → 定时 pull → 自动进化
                    ↓
5. 问题 → git revert → 回滚
```

---

## 当前状态 vs 理想状态

| 能力 | 当前 | 理想 |
|------|------|------|
| 主脑进化同步 | ✅ 手动 | 🔄 自动定时 |
| MacBook 同步 | ⚪ 未配置 | 🔄 自动 pull |
| Codespace 同步 | ⚪ 未配置 | 🔄 自动 pull |
| 冲突自动解决 | ⚪ 手动 | 🔄 自动 merge |
| 进化验证 | ⚪ 无 | 🔄 Actions CI |

---

## 关键结论

**问**: 主脑进化了，其他节点会怎样？

**答**:
1. **会共享** - 记忆、知识、经验（通过 clawos-brain）
2. **会升级** - 框架、协议、人格（通过 clawos-core + clawos-souls）
3. **不立即** - 有 15-60 分钟延迟（取决于同步间隔）
4. **不会冲突** - Git 自动合并（大多数情况）

**但如果其他节点进化了呢？**

**答**: 同样的逻辑，push 到 GitHub → 主脑 pull → 双向同步

---

**本质**: GitHub 是"唯一真相源"，所有节点都是它的"副本"

---

🦞 ClawOS Federation
