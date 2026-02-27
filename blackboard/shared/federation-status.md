# ClawOS Federation 状态

**更新时间**: 2026-02-27 09:23

---

## 仓库状态

| 仓库 | 状态 | 用途 |
|------|------|------|
| clawos-core | ✅ 活跃 | 框架 + 协议 |
| clawos-brain | ✅ 活跃 | 黑板 + 记忆 |
| clawos-souls | ✅ 活跃 | Agent 人格 |
| clawos-actions | ✅ 活跃 | GitHub Actions |
| clawos-node-server | ✅ 已配置 | Mac mini 主脑 |
| clawos-node-coding | ✅ 已配置 | MacBook 编码 |
| clawos-node-quant | ✅ 已配置 | Codespace 量化 |
| clawos-node-writing | ✅ 已配置 | 写作（计划中） |

---

## 自动化任务

| Workflow | 频率 | 状态 |
|----------|------|------|
| blackboard-backup | 每 4 小时 | ✅ 已配置 |
| memory-sync | 每 6 小时 | ✅ 已有 |
| daily-harvest | 每日 03:00 | ✅ 已有 |
| health-check | 按需 | ✅ 已有 |

---

## 同步脚本

位置: `~/clawos/scripts/sync-brain.sh`

```bash
# 推送本地到 GitHub
./sync-brain.sh push

# 从 GitHub 拉取
./sync-brain.sh pull

# 查看状态
./sync-brain.sh status
```

---

## 下一步

- [ ] MacBook 配置自动同步
- [ ] Codespace 配置自动同步
- [ ] 测试跨节点协作

---

🦞 ClawOS Federation
