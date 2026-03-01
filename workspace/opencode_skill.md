# OpenCode Skill - 快速访问 OpenCode

## 概述

这个 skill 提供 OpenCode 的快速访问接口，包括：
- 列出可用的 agents
- 列出可用的类别
- 快速启动 OpenCode TUI/Web
- 获取 OpenCode 帮助信息

## 文件

- `opencode_wrapper.py` - Python 封装工具
- `opencode_integration.md` - 详细集成指南
- `OPencode_INTEGRATION_TEST_REPORT.md` - 测试报告

## 常用命令

### 列出 Agents
```bash
python3 opencode_wrapper.py --list-agents
```

### 列出类别
```bash
python3 opencode_wrapper.py --list-categories
```

### 启动 OpenCode TUI
```bash
# 使用 reflex agent（快速格式化、linting）
~/.opencode/bin/opencode --agent reflex

# 使用 oracle agent（架构设计、代码审查）
~/.opencode/bin/opencode --agent oracle

# 使用 sisyphus agent（主编排器，复杂任务）
~/.opencode/bin/opencode --agent sisyphus
```

### 启动 Web 界面
```bash
~/.opencode/bin/opencode web
```

### 列出所有模型
```bash
~/.opencode/bin/opencode models
```

## Agent 选择指南

| 任务类型 | 推荐工具 | Agent/模型 |
|----------|----------|-----------|
| 快速代码修改 | Henry | GLM-4.7 |
| 格式化、linting | OpenCode | reflex |
| 简单重构 | OpenCode | reflex |
| 架构设计 | OpenCode | oracle |
| 代码审查 | OpenCode | oracle |
| 深度调研 | OpenCode | researcher |
| 技术文档 | OpenCode | document-writer |
| 前端开发 | OpenCode | frontend-ui-ux-engineer |
| 多模态分析 | OpenCode | multimodal-looker |
| 复杂编排 | EVA | sisyphus |
| 内容创作 | OpenCode | writer |
| 编辑优化 | OpenCode | editor |

## 注意事项

⚠️ **重要**: `opencode run` 命令是交互式的，不适合非交互式自动调用。
- 使用 `opencode --agent <name>` 启动 TUI 界面
- 使用 `opencode web` 启动 Web 界面
- 不要尝试通过 `opencode run` 自动执行任务

## 状态

- ✅ OpenCode v1.1.53 安装正常
- ✅ Oh-My-OpenCode 配置完成
- ✅ 16 agents + 12 categories 可用
- ✅ Web 界面功能正常
- ⚠️ 非交互式调用需要额外配置（MCP/ACP）

## 测试结果

详见 `OPencode_INTEGRATION_TEST_REPORT.md`:
- ✅ Wrapper 工具正常
- ✅ 列出 agents 正常
- ✅ 列出类别正常
- ✅ Web 服务器启动和访问正常
- ⚠️ Run 命令非交互调用失败（预期行为）
