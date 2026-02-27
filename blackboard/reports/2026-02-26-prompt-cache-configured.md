# Prompt Cache 配置完成

**时间**: 2026-02-26 21:08
**状态**: ✅ 已配置

---

## 已完成

✅ 在 `vectorengine-claude` provider 添加：
```json
"cache": {
  "enabled": true,
  "ttl": 3600
}
```

---

## 配置说明

- **enabled**: 启用缓存
- **ttl**: 缓存时间 1 小时（3600秒）

---

## 预期效果

| 场景 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| GM 首次调用 | 30k tokens | 30k tokens | - |
| GM 第二次调用 | 30k tokens | <3k tokens | **10x** |
| **成本节省** | - | - | **90%** |

---

## 下一步

1. 重启 OpenClaw（自动生效）
2. 测试验证

---

**配置文件**: `~/openclaw-system/clawos/openclaw.json`
**生效**: 下次 GM 调用时自动启用
