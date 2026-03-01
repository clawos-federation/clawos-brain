# ClawOS Assistant Blackboard

Assistant 是唯一的人机交互入口，负责：
- 接收用户意图
- 转交任务给 GM
- 主动汇报进度
- 处理异常通知

## 目录结构

```
assistant/
├── templates/          # 用户模板
└── {userId}/           # 每用户独立目录
```

## 状态

- **状态**: idle
- **最后更新**: 2026-02-24
