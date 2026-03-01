# MCP (Model Context Protocol) 研究报告

**研究时间**: 2026-02-10 10:10
**研究对象**: OpenCode 的 MCP 集成

---

## 📚 MCP 简介

**MCP (Model Context Protocol)** 是一个标准化协议，用于连接 AI 助手与外部工具和服务。

### MCP 的核心概念

1. **MCP Server**: 提供 MCP 工具和资源的进程
2. **MCP Client**: 消费 MCP 工具和资源的应用（如 OpenCode）
3. **MCP Tools**: 通过 MCP 提供的功能（如文件系统、Git 操作等）
4. **MCP Resources**: 通过 MCP 提供的数据（如文件内容、环境变量等）

### MCP 传输类型

1. **stdio**: 标准输入/输出传输（最常用）
2. **SSE (Server-Sent Events)**: HTTP 流式传输
3. **HTTP**: 标准 HTTP 请求/响应

---

## 🔍 发现的 MCP 配置

### Claude Code 的 MCP 配置

位置: `~/.claude.json`

**配置格式**:
```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {}
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {}
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"],
      "env": {}
    }
  }
}
```

### 常用的 MCP Servers

| Server | 功能 | 包名 |
|---------|--------|-------|
| **filesystem** | 文件系统操作 | `@modelcontextprotocol/server-filesystem` |
| **github** | GitHub 操作 | `@modelcontextprotocol/server-github` |
| **memory** | 记忆管理 | `@modelcontextprotocol/server-memory` |
| **chrome-devtools** | Chrome 浏览器操作 | `chrome-devtools-mcp@latest` |
| **fetch** | HTTP 请求 | `@kazuph/mcp-fetch@latest` |
| **context7** | 上下文管理 | `@upstash/context7-mcp` |
| **playwright** | 浏览器自动化 | `@playwright/mcp` |

---

## 🔧 OpenCode 的 MCP 集成

### 当前状态

```bash
$ ~/.opencode/bin/opencode mcp list
┌  MCP Servers
│
▲  No MCP servers configured
│
└  Add servers with: opencode mcp add
```

### OpenCode MCP 命令

| 命令 | 功能 |
|--------|------|
| `opencode mcp add` | 添加 MCP 服务器（交互式） |
| `opencode mcp list` | 列出 MCP 服务器和状态 |
| `opencode mcp auth [name]` | OAuth 认证 |
| `opencode mcp logout [name]` | 退出认证 |
| `opencode mcp debug <name>` | 调试连接 |

### 添加 MCP 服务器的步骤

```bash
# 1. 启动交互式添加向导
~/.opencode/bin/opencode mcp add

# 2. 按照提示操作：
#    - 选择 MCP 服务器类型
#    - 输入命令和参数
#    - 配置环境变量（可选）
#    - 测试连接
```

---

## 💡 建议的 MCP 服务器配置

### 1. Filesystem MCP
提供文件系统操作能力：

```json
{
  "name": "filesystem",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": {}
}
```

**功能**:
- 文件读取
- 文件写入
- 目录浏览
- 文件搜索

### 2. GitHub MCP
提供 GitHub 仓库操作能力：

```json
{
  "name": "github",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {}
}
```

**功能**:
- 仓库克隆
- 提交历史查询
- Issue 和 PR 操作
- 代码搜索

### 3. Memory MCP
提供持久化记忆功能：

```json
{
  "name": "memory",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "env": {}
}
```

**功能**:
- 存储和检索记忆
- 记忆分类
- 搜索记忆

### 4. Fetch MCP
提供 HTTP 请求能力：

```json
{
  "name": "fetch",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@kazuph/mcp-fetch@latest"],
  "env": {}
}
```

**功能**:
- HTTP GET/POST 请求
- API 调用
- 网页获取

---

## 🚀 测试 MCP 配置

### 方案 1: 交互式配置

```bash
# 启动添加向导
~/.opencode/bin/opencode mcp add
```

**问题**:
- 需要用户交互
- 不适合自动化配置

### 方案 2: 手动配置文件

OpenCode 可能在 `~/.config/opencode/` 中存储 MCP 配置。

```bash
# 查找可能的配置文件
ls ~/.config/opencode/*.json

# 创建 MCP 配置
cat > ~/.config/opencode/mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {}
    },
    "fetch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@kazuph/mcp-fetch@latest"],
      "env": {}
    }
  }
}
EOF
```

### 方案 3: 项目级配置

在项目目录创建 `.mcp.json`：

```bash
# 在工作区创建
cat > /Users/henry/openclaw-system/workspace/.mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {}
    },
    "fetch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@kazuph/mcp-fetch@latest"],
      "env": {}
    }
  }
}
EOF
```

---

## 🎯 结论

### MCP 的优势

1. **标准化协议** - 通用的工具集成标准
2. **丰富的生态** - 大量现成的 MCP 服务器
3. **灵活的传输** - 支持 stdio、SSE、HTTP

### 对 OpenCode 的适用性

| 方面 | 评估 |
|--------|------|
| **支持** | ✅ OpenCode 支持 MCP |
| **配置方式** | ⚠️ 需要进一步研究（交互式向导） |
| **自动化** | ⚠️ 交互式配置，不适合自动添加 |
| **工具生态** | ✅ 大量现成 MCP 服务器 |
| **HTTP API** | ⚠️ MCP 本身不是 HTTP API，需要通过 MCP 服务器间接调用 |

### 推荐行动

**短期**:
1. 尝试交互式添加 MCP 服务器
2. 测试基本的 MCP 工具（filesystem、fetch）
3. 验证 MCP 对 OpenCode 的增强效果

**中期**:
1. 研究非交互式 MCP 配置方式
2. 创建常用 MCP 服务器的预配置
3. 编写 MCP 工具调用脚本

**长期**:
1. 开发自定义 MCP 服务器
2. 集成到 EVA 系统
3. 实现统一的 MCP 调用接口

---

## 📚 参考资料

- **MCP Registry**: https://github.com/mcp
- **OpenCode Docs**: https://github.com/anomalyco/opencode
- **Claude Code MCP Docs**: https://docs.claude.com/en/docs/claude-code/mcp
- **Model Context Protocol Spec**: https://modelcontextprotocol.io

---

**状态**: 📚 **研究完成，待测试**

**下一步**: 尝试配置并测试 MCP 服务器
