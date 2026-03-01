# Memory 系统状态报告

## 当前状态
- **插件状态**: memory-core 已加载
- **可用性**: ❌ 不可用 (unavailable)

## 问题原因
Memory 系统需要嵌入模型来进行向量检索，当前缺少必要的 API key：

1. **OpenAI**: 需要标准 API key（当前只有 Codex OAuth）
2. **Google**: 需要配置
3. **Voyage**: 需要配置

## 解决方案

### 方案 1：添加 OpenAI API Key（推荐）
如果有标准 OpenAI API key：
```bash
openclaw agents add gm
# 选择 openai provider，输入 API key
```

### 方案 2：配置 Google 嵌入服务
使用 Google 的嵌入模型（需要确认账号权限）

### 方案 3：暂时禁用 Memory 功能
如果暂时不需要语义记忆检索

## 影响
- ❌ 无法使用 `memory_search` 进行语义检索
- ✅ 其他功能不受影响
- ⚠️ 长期记忆依赖手动文件管理

---
**生成时间**: 2026-02-19
**状态**: 需要用户配置 API key
