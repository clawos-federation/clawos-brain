# OpenClaw 全面审计报告（2026-02-21）

## 审计范围
- `openclaw status --deep`
- `openclaw security audit --deep`
- `openclaw update status`
- `openclaw health --json`
- `agents_list()`
- `cron list (includeDisabled=true)`
- `browser status (profile=chrome)`

## 总结结论
系统当前整体健康、可用，核心编排权限已恢复（GM 可调度专业 agent）。无 critical 安全问题。存在 1 个安全告警与 1 个浏览器联调阻塞点。

## 关键发现

### 1) 运行健康
- Gateway 正常（local loopback，reachable）
- iMessage 渠道正常
- 默认 agent 为 `gm`
- 当前版本有更新可用（2026.2.19-2）

### 2) 安全状态
- 结果：`0 critical / 1 warning / 1 info`
- Warning：`gateway.trustedProxies` 未配置
  - 当前为 loopback，本地风险可控
  - 若未来经反向代理暴露控制面，需要补配 trustedProxies

### 3) 编排与权限
- `agents_list()`：`allowAny=false`（白名单模式）
- `gm` 当前可见并可调度：`devagent, testagent, researchagent, legalagent`
- 结论：GM -> 专业 agent 路由链路已恢复

### 4) 定时任务（Cron）
- 原有关键任务（metrics sync / canary / guards）均启用且最近状态为 `ok`
- 已新增治理自检任务：
  - 名称：`orchestration:gm-routing-selfcheck`
  - 频率：每 24 小时
  - 目标：验证 GM 路由关键 agent（dev/test/research）可用性
  - 投递：announce 到 iMessage

### 5) 浏览器联调状态
- `profile=chrome` 当前 `running=false`
- 影响：真实网站 E2E（尤其 Babel 链路）仍需先连接 Chrome Relay 标签页

## 与组织分工的一致性检查
- 已满足：GM 作为执行总调度中枢
- 已满足：Henry 作为交互协调层（策略文件已落地）
- 建议持续观察：status 中偶发 bootstrapping 计数（若长期存在再专项排查）

## 优化建议（后续）
1. 若启用反向代理，优先配置 `gateway.trustedProxies`
2. 保持白名单模式（`allowAny=false`）并定期验证 GM 路由
3. 进行一次 Chrome Relay 连接后的 Babel 实站 E2E 验收
4. 评估是否在非工作时段降低非关键 cron 频率，减少系统噪音

---

审计执行时间：2026-02-21（Asia/Shanghai）
