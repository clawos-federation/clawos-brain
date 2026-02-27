# Web Search 免费替代方案

**问题**: Brave API key 缺失
**解决**: 免费替代方案

---

## 推荐方案

### 1. DuckDuckGo Instant Answer API（免费）

**优点**:
- 完全免费
- 无需 API key
- 即时答案

**缺点**:
- 结果较少
- 非完整搜索

**配置**:
```bash
# 无需配置，直接使用
curl "https://api.duckduckgo.com/?q=查询内容&format=json"
```

---

### 2. SerpAPI（免费额度）

**免费额度**: 100 次/月
**网址**: https://serpapi.com/

**配置**:
```bash
# 获取免费 API key
# https://serpapi.com/users/sign_up

openclaw configure --section web
# 输入 SerpAPI key
```

---

### 3. Google Custom Search API（免费额度）

**免费额度**: 100 次/天
**网址**: https://developers.google.com/custom-search/v1/overview

**配置步骤**:
1. 创建 Google Cloud 项目
2. 启用 Custom Search API
3. 获取 API key
4. 配置到 OpenClaw

---

### 4. Jina AI Reader（推荐）⭐

**优点**:
- 完全免费
- 直接读取网页内容
- 转换为 Markdown

**用法**:
```bash
# 直接读取 URL
curl "https://r.jina.ai/http://example.com"
```

**集成到 OpenClaw**:
使用 `web_fetch` 工具（已经内置）

---

### 5. SearXNG（开源自托管）

**优点**:
- 完全开源
- 可自托管
- 聚合多个搜索引擎

**GitHub**: https://github.com/searxng/searxng

**部署**:
```bash
docker run -p 8888:8080 searxng/searxng
```

---

## 🎯 推荐配置

### 最佳方案（立即可用）

**使用 Jina AI Reader + web_fetch**

已经内置，无需额外配置：

```python
# 使用 web_fetch 工具
# 自动使用 Jina AI Reader
```

---

### 完整搜索方案

1. **DuckDuckGo** - 快速查询
2. **web_fetch** - 深度读取
3. **SerpAPI** - 精确搜索（100次/月）

---

## 📝 配置步骤（SerpAPI）

```bash
# 1. 注册获取 API key
# https://serpapi.com/users/sign_up

# 2. 配置到 OpenClaw
openclaw configure --section web

# 3. 测试
openclaw test web-search "test query"
```

---

## ✅ 当前状态

- ❌ Brave API key 缺失
- ✅ DuckDuckGo 可用（免费）
- ✅ web_fetch 可用（内置 Jina）
- ⏳ SerpAPI 待配置（100次/月免费）

---

## 🚀 立即可做

### 方案 A: 使用内置工具

直接用 `web_fetch` 读取网页内容：

```
对 assistant 说："读取 https://example.com 的内容"
```

### 方案 B: 配置 SerpAPI

1. 注册 SerpAPI（免费 100 次/月）
2. 配置到 OpenClaw
3. 启用 web_search

---

**推荐**: 先用内置 `web_fetch`，需要精确搜索时再配置 SerpAPI

🦞
