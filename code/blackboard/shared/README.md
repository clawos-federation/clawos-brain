# ClawOS Shared Context

共享上下文目录，用于 Agent 间共享数据。

## 用途

- 跨 Agent 的共享配置
- 全局状态
- 临时协作数据

## 规则

1. 所有 Agent 可读
2. 只有写入者可写
3. 定期清理过期数据
