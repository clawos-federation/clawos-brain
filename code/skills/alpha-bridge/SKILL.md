# SKILL.md - alpha-bridge

> 本地与 Alpha 量化系统的通信桥梁 Skill

---

## 概述

| 属性 | 值 |
|------|-----|
| **ID** | alpha-bridge |
| **版本** | 3.0.0 |
| **类别** | Communication |
| **Alpha 系统位置** | `~/clawos-alpha/` |
| **权限级别** | 低（只读 Alpha 数据） |

---

## 系统架构

```
openclaw-system/          # 主系统 (本系统)
├── clawos/
│   └── skills/alpha-bridge/  ← 本 Skill
└── ...

        ↕ alpha-bridge 通信

clawos-alpha/             # Alpha 量化系统 (独立)
├── strategies/           # 28 代策略
├── souls/                # 7 个 Alpha agents
├── blackboard/alpha/     # 信号输出
└── alpha-openclaw.json   # 独立配置
```

---

## 功能

### 核心能力

| 能力 | 命令示例 | 说明 |
|------|----------|------|
| **信号读取** | `cat ~/clawos-alpha/blackboard/alpha/signals/` | 读取预测信号 |
| **策略列表** | `ls ~/clawos-alpha/strategies/` | 查看策略文件 |
| **状态检查** | `cat ~/clawos-alpha/blackboard/alpha/reports/` | 查看运行报告 |

---

## 使用场景

### 场景 1: 获取涨停预测信号

```bash
# 读取最新涨停预测
cat ~/clawos-alpha/blackboard/alpha/signals/limit_up_prediction.json
```

### 场景 2: 查看策略列表

```bash
# 列出所有策略
ls -la ~/clawos-alpha/strategies/

# 查看最新策略
cat ~/clawos-alpha/strategies/limit_up_hunter_v1.py
```

### 场景 3: 获取 Alpha 系统配置

```bash
# 查看 Alpha 配置
cat ~/clawos-alpha/alpha-openclaw.json
```

### 场景 4: 同步信号到主系统

```bash
# 将 Alpha 信号同步到主系统 blackboard
cp ~/clawos-alpha/blackboard/alpha/signals/limit_up_prediction.json \
   ~/.openclaw/clawos/clawos/blackboard/alpha/signals/latest.json
```

---

## 命令模板

```bash
# Alpha 系统路径
ALPHA_HOME=~/clawos-alpha
ALPHA_SIGNALS=$ALPHA_HOME/blackboard/alpha/signals
ALPHA_STRATEGIES=$ALPHA_HOME/strategies

# 读取信号
cat $ALPHA_SIGNALS/limit_up_prediction.json

# 运行策略
cd $ALPHA_HOME && python3 strategies/limit_up_hunter_v1.py

# 查看配置
cat $ALPHA_HOME/alpha-openclaw.json
```

---

## 输出格式

### 涨停预测信号

```json
{
  "strategy": "limit_up_hunter_v1",
  "version": "1.0.0",
  "date": "2026-02-27",
  "total_candidates": 10,
  "limit_up_today": 75,
  "predictions": [
    {
      "code": "000899",
      "name": "赣能股份",
      "score": 0.74,
      "change_pct": 10.02,
      "reasons": ["换手率3.7%适中", "涨幅10.02%接近涨停"]
    }
  ]
}
```

---

## 错误处理

| 错误 | 处理 |
|------|------|
| Alpha 目录不存在 | 返回错误，提示检查 clawos-alpha 安装 |
| 信号文件不存在 | 返回空结果，提示运行策略 |
| 权限不足 | 返回错误，检查文件权限 |

---

## 配置

### 环境变量

```bash
# 可选：在 ~/.zshrc 中配置
export CLAWOS_ALPHA_HOME=~/clawos-alpha
```

### 主系统 node-status.json

```json
{
  "nodes": {
    "quant": {
      "path": "~/clawos-alpha",
      "bridge": "alpha-bridge"
    }
  }
}
```

---

## 与其他 Skills 的关系

| Skill | 关系 |
|-------|------|
| `blackboard` | 本 Skill 读取 Alpha 数据后写入主系统 blackboard |
| `git-operations` | 可用于同步两套系统的变更 |

---

## Alpha 系统信息

| 项目 | 值 |
|------|-----|
| **位置** | `~/clawos-alpha/` |
| **决策层模型** | Opus (TITAN) |
| **执行层模型** | GLM-5 |
| **策略数量** | 28 代 |
| **数据源** | AkShare |

---

*此 Skill 是 alpha-bridge Agent 的专用通信工具，用于连接主系统与独立的 Alpha 量化系统。*
