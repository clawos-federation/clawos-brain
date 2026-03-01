---
name: blackboard
description: 统一的黑板读写操作，支持从共享黑板读取和写入数据（带文件锁）
---

# Blackboard Skill

统一的黑板读写操作，用于管理 `~/clawos/blackboard/` 目录下的共享数据。

---

## 目录

1. [概述](#概述)
2. [READ 操作](#read-操作)
3. [WRITE 操作](#write-操作)
4. [命名约定](#命名约定)
5. [安全机制](#安全机制)

---

## 概述

Blackboard 是 Agent 间共享数据的核心机制。所有 Agent 通过统一的路径读写数据：

```
~/clawos/blackboard/
├── tasks/{taskId}/
│   ├── status.md          # 任务状态
│   ├── validation.md      # 验证结果
│   └── escalation.md      # 上报记录
├── gm/
│   └── gm-decisions.md    # GM 决策日志
└── shared/
    └── context.md         # 共享上下文
```

---

## READ 操作

从黑板读取共享数据。

### 使用方法

```bash
blackboard read <path>
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 相对于 `blackboard/` 的路径 |

### 示例

```bash
# 读取任务状态
blackboard read tasks/123/status.md

# 读取 GM 决策日志
blackboard read gm/gm-decisions.md

# 读取共享上下文
blackboard read shared/context.md
```

### 返回值

- 成功：返回文件内容（Markdown 格式）
- 失败：返回错误信息（文件不存在 / 无权限）

---

## WRITE 操作

向黑板写入数据，使用文件锁保证并发安全。

### 使用方法

```bash
blackboard write <path> --mode <overwrite|append> --content "<content>"
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 相对于 `blackboard/` 的路径 |
| `content` | string | ✅ | 写入内容 |
| `mode` | string | ✅ | `overwrite`（覆盖）或 `append`（追加） |

### 示例

```bash
# 覆盖写入任务状态
blackboard write tasks/123/status.md --mode overwrite --content "## Status: IN_PROGRESS"

# 追加决策记录
blackboard write gm/gm-decisions.md --mode append --content "- 2026-02-24: Approved task #123"
```

---

## 命名约定

| 路径模式 | 用途 | 读写频率 |
|----------|------|----------|
| `tasks/{taskId}/status.md` | 任务状态 | 高频读写 |
| `tasks/{taskId}/validation.md` | 验证结果 | 中频写入 |
| `tasks/{taskId}/escalation.md` | 上报记录 | 低频写入 |
| `gm/gm-decisions.md` | GM 决策日志 | 中频追加 |
| `shared/context.md` | 共享上下文 | 中频读写 |

### 路径规范

- 使用小写字母和连字符
- 任务 ID 使用数字
- 文件扩展名统一使用 `.md`

---

## 安全机制

### 文件锁（WRITE 操作）

写入操作使用 `flock` 文件锁防止并发冲突：

```
1. 获取文件锁
2. 备份上一版本到 .bak
3. 写入新内容
4. 释放文件锁
```

### 自动备份

每次写入前自动备份上一版本：

```
tasks/123/status.md     → tasks/123/status.md.bak
gm/gm-decisions.md      → gm/gm-decisions.md.bak
```

### 权限控制

- 所有 Agent 可读取
- 只有授权 Agent 可写入（由 PM 层控制）

---

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 文件不存在（READ） | 返回 `404 NOT_FOUND` |
| 文件锁超时（WRITE） | 等待 5 秒后重试，最多 3 次 |
| 权限不足 | 返回 `403 FORBIDDEN` |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-02-24 | 合并 blackboard-read 和 blackboard-write 为统一 Skill |
| 1.0.0 | 2026-02-20 | 初始版本（分离的 read/write） |
