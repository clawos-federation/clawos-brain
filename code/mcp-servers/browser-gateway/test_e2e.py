#!/usr/bin/env python3
"""
Browser Gateway MCP Server 端到端测试

测试场景：
1. 启动 Playwright 浏览器
2. 导航到测试页面
3. 截图
4. 关闭浏览器
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SCREENSHOT_DIR = Path("/tmp/openclaw/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


async def test_playwright_direct():
    """直接使用 Playwright 测试"""
    print("=== 测试 1: Playwright 直接调用 ===")

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True, args=["--ignore-certificate-errors"]
            )
            page = await browser.new_page()

            print("  → 创建本地测试页面...")
            await page.set_content(
                "<html><head><title>Test Page</title></head><body><h1>Hello ClawOS</h1></body></html>"
            )

            screenshot_path = SCREENSHOT_DIR / "test_playwright.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"  ✅ 截图保存: {screenshot_path}")

            title = await page.title()
            print(f"  ✅ 页面标题: {title}")

            await browser.close()
            print("  ✅ 浏览器关闭")

        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False


def test_mcp_tools_definition():
    """测试 MCP Server 工具定义"""
    print("\n=== 测试 2: MCP Server 工具定义 ===")

    try:
        from server import create_server

        server = create_server()
        print("  ✅ MCP Server 创建成功")

        expected_tools = [
            "browser_navigate",
            "browser_click",
            "browser_type",
            "browser_screenshot",
            "browser_snapshot",
            "browser_fill",
            "browser_wait",
            "browser_evaluate",
            "browser_tabs",
            "browser_close",
        ]
        print(f"  ✅ 预定义工具数: {len(expected_tools)}")

        for tool in expected_tools:
            print(f"     - {tool}")

        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False


async def test_browser_worker_config():
    """测试 Browser Worker 配置"""
    print("\n=== 测试 3: Browser Worker 配置 ===")

    try:
        # 检查 agent.json
        agent_path = Path(
            "/Users/dongshenglu/openclaw-system/workspace/agents/browser-worker/agent.json"
        )
        with open(agent_path) as f:
            agent = json.load(f)
        print(f"  ✅ Agent: {agent['name']} v{agent['version']}")

        # 检查 SOUL.md
        soul_path = Path(
            "/Users/dongshenglu/openclaw-system/clawos/souls/browser-worker/SOUL.md"
        )
        if soul_path.exists():
            print(f"  ✅ SOUL.md 存在")

        # 检查 registry
        registry_path = Path(
            "/Users/dongshenglu/openclaw-system/workspace/agents/registry.json"
        )
        with open(registry_path) as f:
            registry = json.load(f)

        if "browser-worker" in registry["agents"]:
            bw = registry["agents"]["browser-worker"]
            print(f"  ✅ Registry: {bw['name']}")
            print(f"     模型: {bw['primaryModel']}")
            print(f"     管理者: {bw['managedBy']}")

        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False


async def main():
    print("=" * 60)
    print("  Browser Gateway MCP Server 端到端测试")
    print("=" * 60)

    results = []

    results.append(await test_playwright_direct())

    results.append(test_mcp_tools_definition())

    results.append(await test_browser_worker_config())

    # 总结
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  测试结果: {passed}/{total} 通过")
    print("=" * 60)

    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
