# 模型路由配置分析

## 当前配置

### 自定义 Provider 配置
```json
"models": {
  "mode": "merge",
  "providers": {
    "zai": {
      "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
      "api": "openai-completions",
      "models": [
        {"id": "glm-5", ...},
        {"id": "glm-5-flash", ...},
        {"id": "glm-5-flashx", ...}
      ]
    },
    "opencode": {
      "baseUrl": "https://api.opencode.ai/v1",
      "api": "openai-completions",
      "models": [
        {"id": "kimi-k2.5-free", ...},
        {"id": "minimax-m2.5-free", ...}
      ]
    }
  }
}
```

## 审计警告

### ⚠️ OpenCode Zen 覆盖
- **警告**: `models.providers.opencode` 覆盖了内建的 OpenCode Zen catalog
- **影响**: 可能影响路由/计费逻辑
- **建议**: 评估是否需要保留

## 配置用途分析

### ZAI Provider（智谱）
- **用途**: 提供国产 GLM 系列模型
- **优势**: 免费使用，大上下文窗口（204k）
- **建议**: ✅ 保留（核心配置）

### OpenCode Provider
- **用途**: 提供 Kimi 和 MiniMax 免费模型
- **优势**: 免费，大上下文窗口（200k）
- **问题**: 覆盖了内建 catalog
- **建议**: ⚠️ 需要评估

## 决策选项

### 选项 1：保留并添加注释（推荐）
- 保留当前配置
- 在配置文件中添加注释说明用途
- 定期检查是否有冲突

### 选项 2：移除 OpenCode Provider
- 只保留 ZAI provider
- 使用内建的 OpenCode catalog
- 可能失去一些免费模型选项

### 选项 3：完全重置
- 移除所有自定义 provider
- 使用完全内建的配置
- 重新配置需要的模型

## 推荐方案

建议采用**选项 1**：
1. 保留 ZAI provider（核心需求）
2. 保留 OpenCode provider（但添加注释）
3. 在配置文件中添加说明文档

---
**生成时间**: 2026-02-19
**需要决策**: 是否保留 OpenCode provider
