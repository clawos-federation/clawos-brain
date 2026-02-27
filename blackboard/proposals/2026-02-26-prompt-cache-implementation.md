# Prompt Cache 配置指南（实用版）

**目标**: 减少 90% token 消耗
**当前状态**: 系统已支持（有 cacheRead/cacheWrite 成本定义）
**需要做的**: 启用缓存配置

---

## 快速配置（推荐）

### 方法 1: 在 provider 配置中启用

编辑 `~/openclaw-system/clawos/openclaw.json`，在 `vectorengine-claude` provider 中添加：

```json
"vectorengine-claude": {
  "baseUrl": "https://api.vectorengine.ai/v1",
  "api": "openai-completions",
  "cache": {
    "enabled": true,
    "ttl": 3600,
    "type": "ephemeral"
  },
  "models": [...]
}
```

### 方法 2: 在 agent 配置中启用

在 `gm` 和 `validator` agent 配置中添加：

```json
{
  "id": "gm",
  "name": "ClawOS GM",
  "model": {
    "primary": "vectorengine-claude/claude-opus-4-6-thinking",
    "cache": {
      "system": true,
      "soul": true,
      "config": true
    }
  },
  ...
}
```

---

## 配置选项

| 选项 | 说明 | 推荐值 |
|------|------|--------|
| enabled | 是否启用 | true |
| ttl | 缓存时间（秒） | 3600（1小时）|
| type | 缓存类型 | ephemeral |
| system | 缓存系统提示 | true |
| soul | 缓存 SOUL 文件 | true |
| config | 缓存配置文件 | true |

---

## 简单配置（最保险）

如果你不确定，可以先在 `openclaw.json` 的 `models.providers.vectorengine-claude` 下添加：

```json
"cache": {
  "enabled": true
}
```

这样最简单，风险最小。

---

## 验证方法

配置后重启 OpenClaw，然后测试：

```bash
# 重启
openclaw gateway restart

# 第一次调用（会缓存）
openclaw agent run gm --task "测试任务1"

# 第二次调用（使用缓存）
openclaw agent run gm --task "测试任务2"

# 查看 token 消耗
openclaw stats tokens | grep gm
```

**预期**: 第二次调用 tokens 应该比第一次少 90%

---

## ⚠️ 注意事项

1. **VectorEngine 支持**: 需要确认 VectorEngine API 支持 `cache_control`
2. **成本**: 缓存写入有成本（$18.75/1M tokens），但读取便宜（$1.5/1M）
3. **TTL**: 默认 1 小时，可以根据需要调整

---

## 🚨 如果不确定

**最安全的方法**: 先不要改配置，等待 OpenClaw 官方文档确认 Prompt Cache 支持情况。

**或者**: 先在测试环境试验。

---

## 当前建议

鉴于直接修改配置文件有风险，我建议：

1. **先备份当前配置**
2. **添加简单的 cache 配置**
3. **测试验证**
4. **如果有效，再详细配置**

要现在开始配置吗？还是先备份？
