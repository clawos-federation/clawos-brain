#!/usr/bin/env python3
"""
ClawOS Browser Gateway MCP Server

统一的浏览器能力网关，将 openclaw browser CLI 暴露为 MCP tools。

架构:
    MCP Client (Agent)
           ↓
    Browser Gateway MCP Server
           ↓
    openclaw browser CLI (40+ 命令)
           ↓
    Chrome/Chromium (CDP)

版本: 1.0.0
"""

import asyncio
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: mcp package not installed. Run: pip install mcp")

# 配置
SCREENSHOT_DIR = Path(os.getenv("BROWSER_SCREENSHOT_DIR", "/tmp/openclaw/screenshots"))
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))


@dataclass
class BrowserResult:
    """浏览器操作结果"""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    screenshot: str | None = None


async def run_openclaw_browser(
    *args: str, timeout: int = DEFAULT_TIMEOUT
) -> BrowserResult:
    """
    执行 openclaw browser 命令

    Args:
        *args: 命令参数
        timeout: 超时时间（毫秒）

    Returns:
        BrowserResult
    """
    cmd = ["openclaw", "browser", *args]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout / 1000
        )

        if proc.returncode == 0:
            try:
                data = json.loads(stdout.decode()) if stdout else {}
            except json.JSONDecodeError:
                data = {"raw": stdout.decode()}

            return BrowserResult(success=True, data=data)
        else:
            return BrowserResult(
                success=False,
                error=stderr.decode() or f"Command failed with code {proc.returncode}",
            )

    except asyncio.TimeoutError:
        return BrowserResult(success=False, error=f"Timeout after {timeout}ms")

    except Exception as e:
        return BrowserResult(success=False, error=str(e))


# ============== MCP Tools ==============


async def tool_navigate(url: str, wait_until: str = "load") -> BrowserResult:
    """导航到 URL"""
    return await run_openclaw_browser("navigate", url, "--wait-until", wait_until)


async def tool_click(ref: str, double: bool = False) -> BrowserResult:
    """点击元素"""
    args = ["click", ref]
    if double:
        args.append("--double")
    return await run_openclaw_browser(*args)


async def tool_type(ref: str, text: str, submit: bool = False) -> BrowserResult:
    """输入文本"""
    args = ["type", ref, text]
    if submit:
        args.append("--submit")
    return await run_openclaw_browser(*args)


async def tool_screenshot(
    full_page: bool = False, ref: str | None = None
) -> BrowserResult:
    """截图"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = SCREENSHOT_DIR / filename

    args = ["screenshot", "--output", str(filepath)]
    if full_page:
        args.append("--full-page")
    if ref:
        args.extend(["--ref", ref])

    result = await run_openclaw_browser(*args)
    if result.success:
        result.screenshot = str(filepath)
    return result


async def tool_snapshot(format: str = "ai", limit: int = 200) -> BrowserResult:
    """获取页面快照"""
    return await run_openclaw_browser(
        "snapshot", "--format", format, "--limit", str(limit)
    )


async def tool_fill(fields: list[dict]) -> BrowserResult:
    """填写表单"""
    fields_json = json.dumps(fields)
    return await run_openclaw_browser("fill", "--fields", fields_json)


async def tool_wait(condition: str, timeout: int = 10000) -> BrowserResult:
    """等待条件"""
    return await run_openclaw_browser(
        "wait", "--condition", condition, "--timeout", str(timeout)
    )


async def tool_evaluate(fn: str, ref: str | None = None) -> BrowserResult:
    """执行 JavaScript"""
    args = ["evaluate", "--fn", fn]
    if ref:
        args.extend(["--ref", ref])
    return await run_openclaw_browser(*args)


async def tool_tabs() -> BrowserResult:
    """列出标签页"""
    return await run_openclaw_browser("tabs", "--json")


async def tool_close(target_id: str | None = None) -> BrowserResult:
    """关闭标签页"""
    args = ["close"]
    if target_id:
        args.append(target_id)
    return await run_openclaw_browser(*args)


# ============== MCP Server ==============


def create_server() -> "Server":
    """创建 MCP Server"""
    if not HAS_MCP:
        raise RuntimeError("MCP package not installed")

    server = Server("clawos-browser-gateway")

    # 注册 tools
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="browser_navigate",
                description="导航到指定 URL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "目标 URL"},
                        "wait_until": {
                            "type": "string",
                            "enum": ["load", "domcontentloaded", "networkidle"],
                            "default": "load",
                        },
                    },
                    "required": ["url"],
                },
            ),
            Tool(
                name="browser_click",
                description="点击页面元素",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {
                            "type": "string",
                            "description": "元素引用（从 snapshot 获取）",
                        },
                        "double": {"type": "boolean", "default": False},
                    },
                    "required": ["ref"],
                },
            ),
            Tool(
                name="browser_type",
                description="在元素中输入文本",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {"type": "string", "description": "元素引用"},
                        "text": {"type": "string", "description": "要输入的文本"},
                        "submit": {"type": "boolean", "default": False},
                    },
                    "required": ["ref", "text"],
                },
            ),
            Tool(
                name="browser_screenshot",
                description="截取页面截图",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "full_page": {"type": "boolean", "default": False},
                        "ref": {
                            "type": "string",
                            "description": "特定元素引用（可选）",
                        },
                    },
                },
            ),
            Tool(
                name="browser_snapshot",
                description="获取页面结构快照（用于元素定位）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["ai", "aria"],
                            "default": "ai",
                        },
                        "limit": {"type": "integer", "default": 200},
                    },
                },
            ),
            Tool(
                name="browser_fill",
                description="批量填写表单",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fields": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ref": {"type": "string"},
                                    "value": {"type": "string"},
                                },
                            },
                        }
                    },
                    "required": ["fields"],
                },
            ),
            Tool(
                name="browser_wait",
                description="等待条件满足",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "condition": {
                            "type": "string",
                            "description": "等待条件：selector, text, url, load-state",
                        },
                        "timeout": {"type": "integer", "default": 10000},
                    },
                    "required": ["condition"],
                },
            ),
            Tool(
                name="browser_evaluate",
                description="执行 JavaScript 代码",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fn": {"type": "string", "description": "JavaScript 函数体"},
                        "ref": {"type": "string", "description": "元素引用（可选）"},
                    },
                    "required": ["fn"],
                },
            ),
            Tool(
                name="browser_tabs",
                description="列出所有标签页",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="browser_close",
                description="关闭标签页",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_id": {
                            "type": "string",
                            "description": "标签页 ID（可选，默认当前）",
                        }
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """执行 tool"""
        result = None

        if name == "browser_navigate":
            result = await tool_navigate(
                arguments["url"], arguments.get("wait_until", "load")
            )
        elif name == "browser_click":
            result = await tool_click(arguments["ref"], arguments.get("double", False))
        elif name == "browser_type":
            result = await tool_type(
                arguments["ref"], arguments["text"], arguments.get("submit", False)
            )
        elif name == "browser_screenshot":
            result = await tool_screenshot(
                arguments.get("full_page", False), arguments.get("ref")
            )
        elif name == "browser_snapshot":
            result = await tool_snapshot(
                arguments.get("format", "ai"), arguments.get("limit", 200)
            )
        elif name == "browser_fill":
            result = await tool_fill(arguments["fields"])
        elif name == "browser_wait":
            result = await tool_wait(
                arguments["condition"], arguments.get("timeout", 10000)
            )
        elif name == "browser_evaluate":
            result = await tool_evaluate(arguments["fn"], arguments.get("ref"))
        elif name == "browser_tabs":
            result = await tool_tabs()
        elif name == "browser_close":
            result = await tool_close(arguments.get("target_id"))
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # 格式化输出
        if result.success:
            output = {
                "status": "success",
                "data": result.data,
            }
            if result.screenshot:
                output["screenshot"] = result.screenshot
        else:
            output = {"status": "error", "error": result.error}

        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    return server


async def main():
    """主入口"""
    if not HAS_MCP:
        print("Error: MCP package not installed")
        print("Install with: pip install mcp")
        return

    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
