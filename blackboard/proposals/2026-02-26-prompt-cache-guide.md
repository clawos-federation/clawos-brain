# Prompt Cache 配置指南

**目标**: 减少 90% token 消耗
**适用**: GM, validator (Opus 角色)

---

## 什么是 Prompt Cache

Prompt Cache 可以缓存：
- 系统提示
- SOUL 文件
- 配置文件
- 常用的上下文

**效果**: 缓存命中时，不重复计费，节省 90%。

---

## Anthropic Claude Opus 配置

### 方法 1: 使用 Anthropic API

```python
import anthropic

client = anthropic.Anthropic()

# 启用 Prompt Cache
response = client.messages.create(
    model="claude-opus-4-6-20250219",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "GM SOUL 内容...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "任务内容..."
        }
    ]
)
```

### 方法 2: 使用 OpenAI 兼容 API (VectorEngine)

```bash
# 检查是否支持 cache_control
curl https://api.vectorengine.ai/v1/chat/completions \
  -H "Authorization: Bearer $VECTORENGINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4-6-thinking",
    "messages": [
      {
        "role": "system",
        "content": "GM SOUL...",
        "cache_control": {"type": "ephemeral"}
      },
      {
        "role": "user",
        "content": "任务..."
      }
    ]
  }'
```

---

## OpenClaw 配置

### 1. 检查是否支持

```bash
# 检查 OpenClaw 版本
openclaw --version

# 需要版本 >= 2026.2.20
```

### 2. 启用 Prompt Cache

编辑 `~/openclaw-system/clawos/openclaw.json`：

```json
{
  "models": {
    "providers": {
      "vectorengine-claude": {
        "cache": {
          "enabled": true,
          "ttl": 3600,
          "type": "ephemeral"
        }
      }
    }
  },
  
  "agents": {
    "gm": {
      "cache": {
        "system": true,
        "soul": true,
        "config": true
      }
    },
    "validator": {
      "cache": {
        "system": true,
        "soul": true,
        "config": true
      }
    }
  }
}
```

### 3. 验证缓存

```bash
# 第一次调用（无缓存）
time openclaw agent run gm --task "测试任务"
# Token 消耗: ~30k

# 第二次调用（有缓存）
time openclaw agent run gm --task "另一个任务"
# Token 消耗: ~5k (预期)
```

---

## 缓存策略

### 缓存内容

| 内容 | 是否缓存 | TTL |
|------|----------|-----|
| 系统提示 | ✅ | 1 小时 |
| SOUL 文件 | ✅ | 1 小时 |
| 配置文件 | ✅ | 1 小时 |
| 任务描述 | ❌ | - |
| 上下文 | 部分 | 5 分钟 |

### 缓存更新

```bash
# 清除缓存
openclaw cache clear

# 重新加载 SOUL
openclaw cache reload --agent gm
```

---

## 成本对比

### 无缓存

| 角色 | 每次调用 | 每日（10次） | 每月 |
|------|----------|-------------|------|
| GM | $0.375 | $3.75 | $112.50 |
| validator | $0.187 | $1.87 | $56.10 |
| **总计** | **$0.562** | **$5.62** | **$168.60** |

### 有缓存（90% 节省）

| 角色 | 每次调用 | 每日（10次） | 每月 |
|------|----------|-------------|------|
| GM | $0.0375 | $0.375 | $11.25 |
| validator | $0.0187 | $0.187 | $5.61 |
| **总计** | **$0.0562** | **$0.562** | **$16.86** |

**节省**: $151.74/月 (90%)

---

## 故障排查

### 缓存未命中

**症状**: Token 消耗仍然很高

**检查**:
```bash
# 查看缓存状态
openclaw cache status

# 查看缓存命中率
openclaw cache stats
```

**解决**:
1. 确认 cache_control 已添加
2. 检查 TTL 是否过期
3. 重启 OpenClaw

### 缓存过期太快

**症状**: 每次都要重新缓存

**解决**:
```json
{
  "cache": {
    "ttl": 86400  // 24 小时
  }
}
```

---

## 最佳实践

### 1. 固定内容缓存

```json
{
  "cache": {
    "immutable": ["system", "soul", "config"]
  }
}
```

### 2. 动态内容不缓存

```json
{
  "cache": {
    "exclude": ["task", "context"]
  }
}
```

### 3. 定期刷新

```bash
# 每天凌晨刷新缓存
0 0 * * * openclaw cache refresh
```

---

## 下一步

1. [ ] 确认 VectorEngine 支持 Prompt Cache
2. [ ] 配置 openclaw.json
3. [ ] 测试缓存效果
4. [ ] 验证成本降低

---

**创建时间**: 2026-02-26 10:02
**状态**: ⏳ 待实施
