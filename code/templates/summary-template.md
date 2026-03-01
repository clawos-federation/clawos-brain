# Summary 模板

每个任务完成后，Worker 需要写入此摘要，供 GM 快速查询。

---

## 模板

```markdown
# {任务名称} - 摘要

**任务ID**: {taskId}
**完成时间**: {YYYY-MM-DD HH:MM}
**Worker**: {worker角色}
**状态**: ✅ 完成 / ❌ 失败

---

## 一句话总结

{50 字以内描述任务结果}

---

## 关键产出

| 产出物 | 路径 |
|--------|------|
| {文件1} | /path/to/file1 |
| {文件2} | /path/to/file2 |

---

## 核心发现/变更

- {发现1}
- {发现2}
- {变更1}

---

## 下一步建议

1. {建议1}
2. {建议2}

---

## 完整报告

详见: /path/to/full/report.md
```

---

## 示例

```markdown
# BabelPrompt v4.1.0 交付 - 摘要

**任务ID**: babel-delivery
**完成时间**: 2026-02-26 07:16
**Worker**: coder-frontend
**状态**: ✅ 完成

---

## 一句话总结

BabelPrompt Chrome 扩展完成 v4.1.0 更新，工作流自动化 + UI 重设计。

---

## 关键产出

| 产出物 | 路径 |
|--------|------|
| 扩展包 | blackboard/tasks/babel-delivery/babelprompt-v4.1.0.zip |
| 交付报告 | blackboard/tasks/babel-delivery/DELIVERY_REPORT.md |

---

## 核心发现/变更

- 工作流：输入 → Enter → 全自动 → 结果
- UI：从 AI 风格改为 Chrome 原生风格
- 代码：CSS 从 1038 行精简到 180 行

---

## 下一步建议

1. 用户测试反馈收集
2. 考虑添加快捷键支持

---

## 完整报告

详见: blackboard/tasks/babel-delivery/DELIVERY_REPORT.md
```

---

**位置**: 保存到 `blackboard/tasks/{taskId}/summary.md`
