# GM 任务 - 验证全面优化

**时间**: 2026-02-26 08:45
**来源**: assistant
**类型**: 优化验证

---

## 任务

收集 ClawOS 系统状态摘要 + 验证优化效果。

---

## 🚨 严格规则（已在 SOUL 中）

### GM (Opus) 铁律

1. **单次输入 <5k tokens**
2. **只能读取 summary.md + decisions.md**
3. **输出 <2k tokens**
4. **需要更多信息 → 指派 research-pm**

### research-pm 规则

1. **输出 <3k tokens**
2. **格式：核心发现 + 数据摘要 + 建议**
3. **详细内容放完整报告链接**

---

## 流程

```
GM（收到任务，~500 tokens）
    ↓
指派 research-pm
    ↓
research-pm 读 summary.md（~1000 tokens）
    ↓
research-pm 整理摘要（<3k tokens）
    ↓
返回给 GM（<3k tokens）
    ↓
GM 输出总结（<2k tokens）
```

**总 tokens**: <5k ✅

---

## 期望输出

```markdown
# ClawOS 系统状态

## 节点运行
| 节点 | 状态 |
|------|------|
| Alpha | ✅ |

## 近期完成
- 任务1
- 任务2

## 建议
1. xxx
2. xxx
```

**长度**: <2k tokens

---

**Status**: ⏳ Pending
