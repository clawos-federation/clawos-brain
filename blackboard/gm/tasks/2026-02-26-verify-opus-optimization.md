# GM 任务 - 验证 Opus 优化

**时间**: 2026-02-26 08:38
**来源**: assistant
**类型**: 验证测试

---

## 任务

收集 ClawOS 当前状态摘要。

---

## 严格规则（已在 GM SOUL 中）

1. **禁止读取原始文件**
2. **只能读取 summary.md**
3. **输入 <5k tokens**
4. **输出 <2k tokens**
5. **需要更多信息？指派 research-pm**

---

## 流程

```
GM → 指派 research-pm
       ↓
research-pm → 读 summary.md → 整理摘要（<5k）
       ↓
返回给 GM（<5k）
       ↓
GM → 基于摘要做决策 → 输出（<2k）
```

---

**Status**: ⏳ Pending
