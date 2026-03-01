# ClawOS Persistence Layer

持久化层，用于长期存储和历史记录。

## 目录结构

```
persistence/
├── archive/        # 归档任务
├── snapshots/      # 状态快照
├── history/        # 历史日志
└── metrics/        # 统计指标
```

## 规则

1. 归档任务保留 90 天
2. 快照每日自动创建
3. 历史日志按月归档
4. 指标数据保留 1 年
