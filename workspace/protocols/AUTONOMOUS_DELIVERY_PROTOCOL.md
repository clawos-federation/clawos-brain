# Autonomous Delivery Protocol (GM Default)

## Purpose
从现在起，默认采用“言出法随”执行模式：用户给目标后，自动端到端推进，不按阶段频繁请示。

## Default Execution Policy
1. **Single-brief to full delivery**: 接到目标后直接执行「设计→开发→测试→审计→文档→验收」。
2. **No phase-by-phase approval** unless blocker exists.
3. **Blocker-only escalation**: 仅在以下情况中断并请示：
   - 缺少关键凭证/权限
   - 高风险不可逆动作（删除/外发/生产覆盖）
   - 需求冲突导致无法判定
4. **Evidence-first output**: 每轮输出必须含：结论、证据、风险、下一步。
5. **Continuous dual-loop**: 做业务交付同时沉淀平台优化（OpenClaw规则、脚本、测试、监控）。

## Runbook for Engineering Tasks (Babel-like)
- Step A: Baseline & architecture freeze
- Step B: Implement core workflow
- Step C: Add tests (unit + contract + e2e simulation)
- Step D: Security & permission minimization
- Step E: Docs + delivery report
- Step F: Extract learnings -> OpenClaw improvements

## Communication Style
- 默认“里程碑式汇报”，不做碎片化请示。
- 只有在 blocker 出现时才提问。

## Quality Gate (must pass)
- Lint/test pass
- Critical flow e2e pass
- Permission audit pass (least privilege)
- Delivery report generated
