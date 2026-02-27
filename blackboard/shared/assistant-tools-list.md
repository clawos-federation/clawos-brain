# Assistant 可用工具列表

**身份**: ClawOS Assistant（移动节点）
**时间**: 2026-02-26 22:18

---

## 📁 文件操作

### read
- **用途**: 读取文件内容
- **支持**: 文本文件和图片（jpg, png, gif, webp）
- **限制**: 最多 2000 行或 50KB
- **示例**: `read("/path/to/file.md")`

### write
- **用途**: 创建或覆盖文件
- **特点**: 自动创建父目录
- **示例**: `write({path: "/path/to/file.md", content: "内容"})`

### edit
- **用途**: 精确编辑文件（替换文本）
- **要求**: oldText 必须完全匹配
- **示例**: `edit({path: "file.md", oldText: "旧", newText: "新"})`

---

## 💻 命令执行

### exec
- **用途**: 执行 shell 命令
- **支持**: pty（伪终端）、后台运行
- **超时**: 默认 10 秒，可调整
- **示例**: `exec({command: "ls -la"})`

### process
- **用途**: 管理后台进程
- **动作**: list, poll, log, write, send-keys, kill
- **示例**: `process({action: "list"})`

---

## 🌐 网络和浏览器

### browser
- **用途**: 控制浏览器
- **动作**: status, start, stop, open, snapshot, screenshot, act
- **支持**: Chrome 扩展、OpenClaw 浏览器
- **示例**: `browser({action: "open", url: "https://..."})`

### web_fetch
- **用途**: 获取网页内容（提取为 Markdown/文本）
- **内置**: Jina AI Reader
- **示例**: `web_fetch({url: "https://..."})`

### web_search
- **用途**: 网页搜索（Brave API）
- **要求**: 需要 API key（当前缺失）
- **示例**: `web_search({query: "查询内容"})`

---

## 🎨 Canvas 和节点

### canvas
- **用途**: 控制 Canvas
- **动作**: present, hide, navigate, eval, snapshot
- **示例**: `canvas({action: "present", url: "..."})`

### nodes
- **用途**: 管理配对节点
- **动作**: status, describe, camera, screen, location, run
- **示例**: `nodes({action: "status"})`

---

## 🤖 Agent 管理

### sessions_spawn
- **用途**: 生成子 agent（subagent）
- **模式**: run（一次性）或 session（持久）
- **示例**: `sessions_spawn({agentId: "gm", task: "..."})`

### subagents
- **用途**: 管理子 agent
- **动作**: list, kill, steer
- **示例**: `subagents({action: "list"})`

### sessions_list
- **用途**: 列出所有会话
- **示例**: `sessions_list()`

### sessions_history
- **用途**: 获取会话历史
- **示例**: `sessions_history({sessionKey: "..."})`

### sessions_send
- **用途**: 向其他会话发送消息
- **示例**: `sessions_send({sessionKey: "...", message: "..."})`

### agents_list
- **用途**: 列出可用的 agent IDs
- **示例**: `agents_list()`

---

## 💬 消息和通知

### message
- **用途**: 发送消息
- **渠道**: Telegram, WhatsApp, Discord, Slack, Signal, iMessage 等
- **动作**: send, broadcast, reaction, poll
- **示例**: `message({action: "send", to: "...", message: "..."})`

### tts
- **用途**: 文字转语音
- **注意**: 调用后需回复 `NO_REPLY`
- **示例**: `tts({text: "语音内容"})`

---

## 🧠 记忆系统

### memory_search
- **用途**: 语义搜索记忆
- **范围**: MEMORY.md + memory/*.md
- **强制**: 回答历史问题前必须调用
- **示例**: `memory_search({query: "查询内容"})`

### memory_get
- **用途**: 安全读取记忆文件
- **限制**: 只能读 MEMORY.md 和 memory/*.md
- **示例**: `memory_get({path: "memory/2026-02-26.md"})`

---

## 📊 系统和状态

### session_status
- **用途**: 显示会话状态（tokens、成本等）
- **示例**: `session_status()`

### gateway
- **用途**: 管理 Gateway
- **动作**: restart, config.get, config.apply, update.run
- **示例**: `gateway({action: "restart"})`

### cron
- **用途**: 管理定时任务
- **动作**: status, list, add, update, remove, run, wake
- **示例**: `cron({action: "list"})`

---

## 🖼️ 图像处理

### image
- **用途**: 分析图片
- **支持**: 单图或多图（最多 20 张）
- **示例**: `image({prompt: "描述", image: "/path/to/image.jpg"})`

---

## 📚 特殊技能

### 技能系统
- **说明**: 根据任务自动加载技能
- **位置**: `/opt/homebrew/lib/node_modules/openclaw/skills/`
- **触发**: <available_skills> 中描述匹配时自动加载

---

## ❌ 不可用工具

以下工具当前**不可用**：

- `web_search` - 缺少 Brave API key
- 其他未列出的工具

---

## 📊 工具统计

| 类别 | 数量 |
|------|------|
| 文件操作 | 3 |
| 命令执行 | 2 |
| 网络浏览器 | 3 |
| Canvas/节点 | 2 |
| Agent 管理 | 6 |
| 消息通知 | 2 |
| 记忆系统 | 2 |
| 系统状态 | 3 |
| 图像处理 | 1 |
| **总计** | **24** |

---

**更新时间**: 2026-02-26 22:18
**身份**: ClawOS Mobile 📱
