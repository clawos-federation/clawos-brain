# VectorEngine 中转 Claude - System Prompt 问题

**问题描述**: 
GM subagent 通过 VectorEngine（中转 API）调用 Claude 时，没有正确加载 SOUL 文件，导致 agent 认为自己是 Claude 而不是 ClawOS GM。

---

## 根本原因

VectorEngine 是 OpenAI 兼容 API，OpenClaw 通过它调用 Claude。但：

1. **System prompt 传递方式**: OpenAI 格式 vs Anthropic 格式
2. **SOUL 文件加载**: OpenClaw 需要正确将 SOUL 注入到 system prompt
3. **中转 API 兼容性**: VectorEngine 可能不完全支持所有参数

---

## 解决方案

### 方案 1: 检查 OpenClaw 配置

```bash
# 查看 agent 配置
cat ~/openclaw-system/clawos/openclaw.json | grep -A20 '"gm"'

# 确认 SOUL 路径
ls -la ~/clawos/workspaces/gm/SOUL.md
```

**关键**: SOUL.md 必须是符号链接或实际文件

---

### 方案 2: 使用 Anthropic 直接 API（推荐）

**问题**: VectorEngine 可能不完全兼容 system prompt 传递

**解决**: 直接使用 Anthropic API

```json
{
  "providers": {
    "anthropic": {
      "baseUrl": "https://api.anthropic.com/v1",
      "api": "anthropic",
      "models": [
        {
          "id": "claude-opus-4-6-20250219",
          "name": "Claude Opus 4.6"
        }
      ]
    }
  }
}
```

**优点**:
- 完全兼容 system prompt
- 支持 cache_control
- 更稳定

**缺点**:
- 需要 Anthropic API key
- 可能更贵（取决于 VectorEngine 价格）

---

### 方案 3: 调整 OpenClaw 调用方式

OpenClaw 可能需要特殊配置来正确传递 system prompt 到中转 API。

**检查**:
```bash
# 查看 OpenClaw 日志
openclaw logs --follow

# 查看 agent 调用详情
openclaw agent run gm --task "测试" --verbose
```

---

### 方案 4: 联系 OpenClaw 社区

这可能是 OpenClaw 的已知问题。

**渠道**:
- GitHub Issues: https://github.com/openclaw/openclaw/issues
- Discord: https://discord.com/invite/clawd
- 文档: https://docs.openclaw.ai

---

## 临时解决方案

### 方案 A: 在任务提示中强调身份

```python
sessions_spawn({
  agentId: "gm",
  task: """
你是 ClawOS GM，全局决策中枢。
你的职责是：评估任务、任命 PM、最终验收。

【重要】你不是 Claude，你是 ClawOS GM。

任务: {实际任务}
"""
})
```

**优点**: 简单
**缺点**: 每次调用都要重复，增加 token 消耗

---

### 方案 B: 使用本地模型（GLM-5）

临时用 GLM-5 替代 Opus，等解决后再切换。

```json
{
  "id": "gm",
  "model": {
    "primary": "zai/glm-5"  // 临时改用 GLM-5
  }
}
```

**优点**: 立即可用
**缺点**: 失去 Opus 的决策能力

---

## 🎯 推荐方案

### 短期（今晚）
**方案 A**: 在任务提示中强调身份（立即可用）

### 中期（明天）
**方案 2**: 切换到 Anthropic 直接 API（彻底解决）

### 长期
**方案 4**: 向 OpenClaw 社区反馈问题

---

## ✅ 下一步

1. **立即**: 使用方案 A（在任务提示中强调身份）
2. **明天**: 研究 Anthropic 直接 API 配置
3. **后续**: 向社区反馈

---

**问题**: VectorEngine 中转 API 传递 system prompt
**影响**: GM/validator 等使用 Opus 的 agent
**解决**: 切换到 Anthropic 直接 API 或调整调用方式
