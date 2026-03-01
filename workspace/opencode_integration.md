# OpenCode 集成指南

## 概述

OpenCode 是一个强大的 AI 编码助手框架，配合 oh-my-opencode 插件，提供了多 Agent 编排能力。

## 架构

### OpenCode (v1.1.53)
- **位置**: `~/.opencode/bin/opencode`
- **用途**: AI 编码助手框架

### Oh-My-OpenCode
- **配置**: `~/.config/opencode/oh-my-opencode.json`
- **用途**: 16 个专用 Agent + 12 个类别路由

## 可用的 Agents

| Agent | 主模型 | 用途 |
|-------|--------|------|
| **reflex** | GLM-4.7 | 快速格式化、linting、简单重构 |
| **sisyphus** | GLM-4.7 | 主编排器，复杂任务规划与并行执行 |
| **oracle** | GPT-5.2 | 架构设计、代码审查、战略分析 |
| **researcher** | Gemini 3 Pro High | 深度调研 |
| **fact-checker** | Gemini 3 Pro High | 事实核查 |
| **writer** | Gemini 3 Pro High | 内容创作 |
| **document-writer** | GLM-4.7 | 技术文档 |
| **frontend-ui-ux-engineer** | Gemini 3 Flash | 前端开发 |
| **multimodal-looker** | Gemini 3 Flash | 多模态分析 |
| **chief** | Claude Opus 4.5 | 主编（探索+协调） |
| **deputy** | GLM-4.7 | 副主编，执行委派任务 |
| **librarian** | GLM-4.7 | 知识检索 |
| **explore** | GLM-4.7 | 探索模式 |
| **archivist** | GLM-4.7 | 知识库管理 |
| **editor** | GLM-4.7 | 编辑优化 |
| **extractor** | Gemini 3 Flash | PDF/图片提取 |

## 快速使用

### 基本命令

```bash
# 启动 TUI（默认）
~/.opencode/bin/opencode

# 使用特定 agent 启动
~/.opencode/bin/opencode --agent reflex

# 使用特定模型启动
~/.opencode/bin/opencode --model zhipu-coding/glm-4.7

# 快速执行单条命令（交互式）
~/.opencode/bin/opencode run --agent reflex "将 'hello' 转换为大写"

# 启动 Web 界面
~/.opencode/bin/opencode web

# 列出所有可用模型
~/.opencode/bin/opencode models
```

### OpenCode Wrapper 工具

工作区已创建 `opencode_wrapper.py`，列出 agents 和类别：

```bash
# 列出可用 agents
python3 opencode_wrapper.py --list-agents

# 列出可用类别
python3 opencode_wrapper.py --list-categories
```

## 集成到 OpenClaw

### 推荐的工作流

**1. 简单任务（快速代码操作）**
- Henry 直接处理（快速响应）
- 模型：GLM-4.7 或 Kimi

**2. 中等任务（代码重构、小功能）**
- 使用 OpenCode 的 reflex agent
- 适合：格式化、linting、简单重构

**3. 复杂任务（架构设计、大功能）**
- 使用 OpenCode 的 sisyphus 或 oracle agent
- 或者通过 EVA 系统处理（多 AI 编排）

### 如何选择 Agent

| 场景 | 推荐工具 |
|------|----------|
| 快速代码修改 | Henry (GLM-4.7) |
| 格式化、linting | OpenCode --agent reflex |
| 架构设计 | OpenCode --agent oracle |
| 代码审查 | OpenCode --agent oracle |
| 深度调研 | OpenCode --agent researcher |
| 技术文档 | OpenCode --agent document-writer |
| 前端开发 | OpenCode --agent frontend-ui-ux-engineer |
| 多模态分析 | OpenCode --agent multimodal-looker |
| 复杂编排 | EVA 或 OpenCode --agent sisyphus |

## 调用建议

由于 OpenCode `run` 命令是交互式的，推荐的使用方式：

1. **使用 OpenCode Wrapper 列出 agents**：
   ```bash
   python3 opencode_wrapper.py --list-agents
   ```

2. **对于具体任务**：
   - 启动 OpenCode TUI：`~/.opencode/bin/opencode --agent <agent>`
   - 在 TUI 中输入任务

3. **对于自动化场景**：
   - 考虑使用 MCP 或 ACP 协议（需要额外配置）
   - 或者通过文件系统接口（OpenClaw 写入任务，外部脚本读取执行）

## 测试验证

### 测试 1: 列出 agents
```bash
python3 opencode_wrapper.py --list-agents
```
预期：列出 16 个 agents

### 测试 2: 列出类别
```bash
python3 opencode_wrapper.py --list-categories
```
预期：列出 12 个类别

### 测试 3: 启动 OpenCode TUI
```bash
~/.opencode/bin/opencode --agent reflex
```
预期：启动交互式 TUI 界面

### 测试 4: 启动 Web 界面
```bash
~/.opencode/bin/opencode web
```
预期：在浏览器中打开 Web 界面

## 总结

- ✅ OpenCode 安装正常（v1.1.53）
- ✅ Oh-My-OpenCode 配置完成（16 agents, 12 categories）
- ✅ OpenCode Wrapper 工具已创建（可以列出 agents 和 categories）
- ⚠️ `opencode run` 命令是交互式的，不适合非交互式自动调用
- ✅ 推荐使用 TUI 或 Web 界面进行交互

## 下一步

如果需要更紧密的集成，可以考虑：

1. 配置 MCP 服务器，通过标准协议调用
2. 使用 ACP 服务器，通过 HTTP API 调用
3. 创建文件系统接口，实现异步任务队列
