# Deprecated Browser Components

> **废弃日期**: 2026-02-25
> **废弃原因**: 游离在 ClawOS 16 Agents 体系外，存在断裂点

---

## 废弃文件

| 文件 | 原因 | 替代方案 |
|------|------|----------|
| `browser-use-bridge.py` | 独立运行，不走 GM/PM 调度；硬编码 API key | Browser Worker Agent |
| `browser-logic-driver.js` | 简单 stub，非 Agent 集成 | Browser Gateway MCP Server |

---

## 替代架构

```
Browser Worker Agent (glm-5)
       ↓
Browser Gateway MCP Server
       ↓
┌──────┼──────┐
↓      ↓      ↓
CLI  Playwright  CDP
```

---

## 保留原因

保留此目录用于：
1. 回溯历史实现参考
2. 回滚应急（如新方案不稳定）

---

**如需恢复**: 将文件移回 `workspace/agents/` 目录
