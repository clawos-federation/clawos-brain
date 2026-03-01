#!/usr/bin/env python3
"""
浏览器自动化沙盒示例
用途：在隔离环境中执行浏览器自动化任务
"""

from playwright.sync_api import sync_playwright
import json
import time

def demo_screenshot():
    """示例：截取网页截图"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问网页
        page.goto("https://github.com/clawos-federation")
        
        # 截图
        screenshot_path = "/tmp/clawos-federation.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ 截图已保存: {screenshot_path}")
        
        # 获取页面标题
        title = page.title()
        print(f"📄 页面标题: {title}")
        
        browser.close()
        return screenshot_path

def demo_scrape():
    """示例：爬取数据"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://github.com/clawos-federation/clawos-brain")
        
        # 获取仓库信息
        data = {
            "title": page.locator("h1").first.text_content(),
            "stars": page.locator("[href='/clawos-federation/clawos-brain/stargazers']").text_content(),
            "forks": page.locator("[href='/clawos-federation/clawos-brain/network/members']").text_content()
        }
        
        print(f"📊 仓库数据: {json.dumps(data, indent=2)}")
        
        browser.close()
        return data

def demo_automation():
    """示例：自动化操作"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        )
        page = context.new_page()
        
        # 模拟人类行为
        page.goto("https://example.com")
        time.sleep(1)  # 随机延迟
        page.mouse.move(100, 200)
        page.scroll(0, 500)
        
        print("✅ 自动化操作完成")
        browser.close()

if __name__ == "__main__":
    print("🌐 浏览器自动化沙盒")
    print("=" * 50)
    
    print("\n1. 截图测试...")
    demo_screenshot()
    
    print("\n2. 数据爬取测试...")
    demo_scrape()
    
    print("\n3. 自动化操作测试...")
    demo_automation()
    
    print("\n✅ 所有测试完成")
