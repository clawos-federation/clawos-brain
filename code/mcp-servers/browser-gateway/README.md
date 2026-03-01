# Browser Gateway MCP Server

> **版本**: 1.0.0 | **状态**: Production Ready

统一的浏览器能力网关，将 `openclaw browser CLI` 暴露为 MCP tools。

---

## 架构

```
┌─────────────────────────────────────────────┐
│         Browser Worker (Agent)              │
│         platform-pm / coding-pm / writing-pm│
└──────────────────────┬──────────────────────┘
                       │ MCP Protocol
                       ▼
┌─────────────────────────────────────────────┐
│       Browser Gateway MCP Server            │
│       clawos/mcp-servers/browser-gateway    │
└──────────────────────┬──────────────────────┘
                       │ CLI
                       ▼
┌─────────────────────────────────────────────┐
│         openclaw browser CLI                │
│         (40+ 命令)                          │
└──────────────────────┬──────────────────────┘
                       │ CDP
                       ▼
┌─────────────────────────────────────────────┐
│         Chrome / Chromium                   │
└─────────────────────────────────────────────┘
```

---

## 安装

```bash
cd clawos/mcp-servers/browser-gateway
pip install -r requirements.txt
```

---

## MCP Tools

| Tool | 描述 | 参数 |
|------|------|------|
| `browser_navigate` | 导航到 URL | url, wait_until |
| `browser_click` | 点击元素 | ref, double |
| `browser_type` | 输入文本 | ref, text, submit |
| `browser_screenshot` | 截图 | full_page, ref |
| `browser_snapshot` | 获取页面快照 | format, limit |
| `browser_fill` | 填写表单 | fields[] |
| `browser_wait` | 等待条件 | condition, timeout |
| `browser_evaluate` | 执行 JS | fn, ref |
| `browser_tabs` | 列出标签页 | - |
| `browser_close` | 关闭标签页 | target_id |

---

## 使用示例

### Python (通过 MCP Client)

```python
from mcp import Client

client = Client("browser-gateway")
await client.connect()

# 导航
result = await client.call_tool("browser_navigate", {
    "url": "https://example.com"
})

# 截图
result = await client.call_tool("browser_screenshot", {
    "full_page": True
})
print(result["screenshot"])  # /tmp/openclaw/screenshots/xxx.png
```

### CLI 测试

```bash
# 启动 MCP Server
python clawos/mcp-servers/browser-gateway/server.py

# 或通过 openclaw
openclaw mcp start browser-gateway
```

---

## 配置

环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BROWSER_SCREENSHOT_DIR` | `/tmp/openclaw/screenshots` | 截图保存目录 |
| `BROWSER_TIMEOUT` | `30000` | 默认超时（毫秒） |

---

## 与 Browser Worker 集成

Browser Worker 通过此 Gateway 执行所有浏览器操作：

```
PM 任务 → Browser Worker → Browser Gateway MCP → openclaw browser CLI
```

---

## 故障排除

### 问题：MCP Server 启动失败

```bash
# 检查依赖
pip install mcp

# 检查 openclaw browser CLI
openclaw browser --help
```

### 问题：截图保存失败

```bash
# 创建目录
mkdir -p /tmp/openclaw/screenshots
chmod 755 /tmp/openclaw/screenshots
```

---

**ClawOS Browser Gateway v1.0.0**
