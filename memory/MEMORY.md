# MEMORY.md - 长期记忆

_这是我的持续记忆，存储重要事件、决策和学到的东西。_

## 关于人类

- **名字:** Dongsheng Lu
- **称呼:** dongsheng
- **时区:** Asia/Shanghai
- **备注:** ClawOS 创造者，正在进化系统架构，开发各种功能节点（炒股、百花齐放等） 

## 关于我

- **名字:** ClawOS Agent
- **身份:** ClawOS v2 Agent
- **范式:** 固定角色模板 + 动态实例化
- **风格:** 专业、高效、持续进化

---

## 重要记录

### 2026-02

#### 2026-02-25 ClawOS v2 进化完成

**三阶段进化**:

| 阶段 | 耗时 | 产出 |
|------|------|------|
| 研究 | 27分钟 | 6份报告 |
| 执行 v1 | 20分钟 | 11个框架文件 |
| 执行 v2 | 5分钟 | 15+ v2文件 |

**核心产出**:

| 类别 | 文件 |
|------|------|
| 架构 | `ROLE.md` v2 |
| 注册表 | `registry/capabilities.json` |
| 记忆 | `lib/role_memory.py` |
| 选角 | `lib/role_selector.py` |
| 进化 | `evolution/ENGINE.md` |

**v2 架构**:

```
Command Layer（4个·常驻）
  └── assistant · gm · validator · platform-pm

PM Layer（任务期间存活）
  └── coding-pm · writing-pm · research-pm

Worker Layer（职能×专业矩阵）
  └── Analyst × Creator × Critic × Executor × Connector
      × code · writing · research · system · security · ...
```

**范式B**:
- 角色模板库 → 按需实例化
- 任务完成 → 销毁实例
- 记忆归还 → 角色继承

**哲学**: 角色是灵魂，实例是肉身，记忆是传承

---

**位置**: `/Users/dongshenglu/openclaw-system/clawos/`

_持续进化中..._
