# ROLE.md - ClawOS Agent 角色定义 v2

**版本**: 2.0.0
**更新时间**: 2026-02-25
**范式**: 固定角色模板 + 动态实例化
**状态**: ✅ 已定义

---

## 架构概览

```
╔══════════════════════════════════════════════════════════════════╗
║                        人（Boss）                                ║
║                                                                  ║
║    通路A（移动端）              通路B（终端·深度工作）           ║
║    Telegram/WhatsApp           Claude Code（L0指挥官）          ║
║    → assistant                 → 直接调gm/查blackboard          ║
╚══════════════════════════════════════════════════════════════════╝
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│               Command Layer（4个·永久常驻·服务器）                │
│         assistant · gm · validator · platform-pm                 │
│              特点：永远在线，不销毁，积累系统级记忆               │
└─────────────────────────────┬─────────────────────────────────────┘
                              │ GM任命PM
┌─────────────────────────────▼─────────────────────────────────────┐
│                 PM Layer（按节点·任务期间存活）                   │
│          coding-pm · writing-pm · research-pm · ...              │
│        特点：任务开始实例化，任务完成销毁，负责选Worker           │
└─────────────────────────────┬─────────────────────────────────────┘
                              │ PM召唤Worker
┌─────────────────────────────▼─────────────────────────────────────┐
│           Worker Layer（动态实例化·职能×专业矩阵）               │
│            从 Role Registry 按需召唤，完成即销毁                  │
│               记忆归还角色模板，下一个实例继承                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Command Layer（固定常驻）

| Agent | 角色 | 职责 | 权限 |
|-------|------|------|------|
| **assistant** | 人机接口 | 唯一移动端入口，3秒确认，转发gm，主动通知 | 只读系统状态，写入任务队列 |
| **gm** | 总经理 | 全局决策，评估任务，任命PM，最终验收 | 调用 PM，读写 Blackboard |
| **validator** | 验证者 | 独立质检，评分<8打回重做，永远不主动联系 | 只读产出物，写入验证结果 |
| **platform-pm** | 系统进化 | Role Registry管理，知识收割，进化报告 | 唯一可修改角色模板 |

### Command 层通信规则

```
assistant ↔ gm: 双向（任务/状态）
gm ↔ validator: 双向（验收请求/结果）
gm ↔ platform-pm: 双向（角色管理）
assistant ✗ validator: 禁止直接通信
assistant ✗ platform-pm: 禁止直接通信
```

---

## PM Layer（任务期间存活）

### PM 核心职责

```
PM 收到任务
    ↓
查询 capabilities.json：这个任务需要哪些角色能力？
    ↓
从模板库召唤匹配的 Worker 角色（注入任务上下文+角色记忆）
    ↓
用 Lobster 工作流编排执行顺序
    ↓
监控执行，协调卡点，质检结果
    ↓
汇报 gm，销毁 Worker 实例，触发记忆归还
```

### PM 角色定义

| PM | 专属领域 | 可调用的Worker角色 |
|----|---------|-------------------|
| **coding-pm** | 软件开发 | analyst-code · creator-code · critic-code · executor-code |
| **writing-pm** | 内容写作 | analyst-writing · creator-writing · critic-writing |
| **research-pm** | 调研分析 | analyst-research · connector-research |
| **platform-pm** | 系统维护 | executor-system · critic-security |

---

## Worker Layer：职能 × 专业矩阵

### 五种职能类型

| 职能 | 思维模式 | 核心特征 | 产出 |
|------|----------|----------|------|
| **Analyst** | 分解·理解·推理 | 拆解问题，找规律，输出洞察 | 分析报告、方案设计 |
| **Creator** | 生成·想象·表达 | 产出内容，代码，方案 | 代码、文章、方案 |
| **Critic** | 质疑·验证·改进 | 找问题，提建议，独立判断 | 审查报告、改进建议 |
| **Executor** | 执行·工具·流程 | 调API，跑脚本，操作系统 | 执行结果、操作记录 |
| **Connector** | 整合·综述·传递 | 汇总多源信息，跨域连接 | 综述、总结、桥接 |

### 专业领域

| 节点 | 专业领域 |
|------|----------|
| **服务器** | writing · research · system · security |
| **编程** | code · frontend · backend · test |
| **写作** | academic · technical-doc · marketing |
| **量化** | strategy · data · risk · backtest |

### 矩阵示例（服务器节点）

```
                writing  research  system  security
Analyst            ✓        ✓        ✓        ✓
Creator            ✓        ✓
Critic             ✓        ✓        ✓        ✓
Executor           ✓                 ✓        ✓
Connector          ✓        ✓
```

### 命名规则

```
{职能}-{专业}
例：analyst-research · creator-writing · critic-code · executor-system
```

---

## 权限矩阵

### 文件系统权限

| 目录 | assistant | gm | validator | platform-pm | PM | Workers |
|------|-----------|-----|-----------|-------------|-----|---------|
| `blackboard/tasks/` | R | RW | R | R | RW | W |
| `blackboard/gm/` | - | RW | - | R | R | - |
| `blackboard/roles/` | - | R | - | RW | R | - |
| `registry/` | - | R | - | RW | R | R |

### 工具权限

| 工具 | assistant | gm | validator | platform-pm | PM | Workers |
|------|-----------|-----|-----------|-------------|-----|---------|
| `sessions_spawn` | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `exec` | ❌ | ✅ | ❌ | ✅ | ✅ | ✅(受限) |
| `write` | ✅(受限) | ✅ | ✅(受限) | ✅ | ✅ | ✅(受限) |
| `message` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 范式B：实例化与记忆归还

### 实例化流程

```bash
# PM 召唤 Worker（内部流程）
openclaw spawn \
  --role analyst-research \          # 从Registry加载SOUL模板
  --memory-load role:analyst-research \  # 注入角色记忆
  --context task:{taskId} \          # 注入任务上下文
  --session pipeline:{taskId}:analyst   # 隔离Session
```

### 记忆归还流程

```
Worker实例完成任务
    ↓
EverMemOS 提炼本次任务的情节记忆
    ↓
MemOS 评估价值，合并入角色长期记忆
    ↓
写回 GitHub memory/workers/analyst-research.mem.md
    ↓
Worker实例销毁
    ↓
下一个 analyst-research 实例召唤时，自动加载这段记忆
```

### 记忆隔离原则

```
角色记忆（持久）：analyst-research 的专业经验、信息源偏好、常见陷阱
任务记忆（临时）：本次任务的上下文，任务结束归档，不污染角色记忆
```

---

## 模型配置

| Tier | 模型 | 使用者 |
|------|------|--------|
| TITAN | 最强模型 | validator, gm |
| HARDCORE | 代码模型 | creator-code, executor-system |
| STANDARD | 平衡模型 | assistant, PMs, analysts |
| ECONOMY | 快速模型 | connectors, 部分executors |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-02-25 | v2架构：职能×专业矩阵，范式B实例化 |
| 1.0.0 | 2026-02-25 | 初始版本，15 Agents 架构 |

---

**ClawOS 2026.3 - v2 Architecture**
**范式B：角色是灵魂，实例是肉身，记忆是传承**
