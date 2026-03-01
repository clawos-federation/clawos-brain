#!/usr/bin/env python3
"""
OpenCode Wrapper - 调用 OpenCode CLI 的封装工具

支持：
- 通过 agent 参数指定使用 oh-my-opencode 的 agent
- 设置超时时间
- 捕获输出
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Optional

OPENCODE_BIN = Path.home() / ".opencode" / "bin" / "opencode"
DEFAULT_TIMEOUT = 60  # 默认超时 60 秒


class OpenCodeError(Exception):
    """OpenCode 调用错误"""
    pass


class OpenCodeWrapper:
    """OpenCode CLI 封装"""

    def __init__(
        self,
        opencode_bin: Optional[Path] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.opencode_bin = opencode_bin or OPENCODE_BIN
        self.timeout = timeout

        if not self.opencode_bin.exists():
            raise OpenCodeError(f"OpenCode binary not found: {self.opencode_bin}")

    def run(
        self,
        message: str,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        format: str = "default",  # default | json
        thinking: bool = False,
        cwd: Optional[Path] = None,
    ) -> str:
        """
        运行 OpenCode 命令

        Args:
            message: 要发送的消息
            agent: 使用的 agent（来自 oh-my-opencode）
            model: 使用的模型（provider/model 格式）
            format: 输出格式（default | json）
            thinking: 是否显示思考过程
            cwd: 工作目录

        Returns:
            输出内容

        Raises:
            OpenCodeError: 调用失败
        """
        cmd = [
            str(self.opencode_bin),
            "run",
            "--format", format,
        ]

        if agent:
            cmd.extend(["--agent", agent])

        if model:
            cmd.extend(["--model", model])

        if thinking:
            cmd.append("--thinking")

        # 消息作为参数传递
        cmd.extend([message])

        cwd_path = cwd or Path.cwd()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd_path,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                raise OpenCodeError(
                    f"OpenCode failed (exit {result.returncode}):\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            return result.stdout

        except subprocess.TimeoutExpired:
            raise OpenCodeError(f"OpenCode timeout after {self.timeout} seconds")

    def list_agents(self) -> list[str]:
        """列出可用的 agents（从 oh-my-opencode.json）"""
        config_path = Path.home() / ".config" / "opencode" / "oh-my-opencode.json"

        if not config_path.exists():
            return []

        with open(config_path) as f:
            config = json.load(f)

        return list(config.get("agents", {}).keys())

    def list_categories(self) -> list[str]:
        """列出可用的类别（从 oh-my-opencode.json）"""
        config_path = Path.home() / ".config" / "opencode" / "oh-my-opencode.json"

        if not config_path.exists():
            return []

        with open(config_path) as f:
            config = json.load(f)

        return list(config.get("categories", {}).keys())


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenCode Wrapper")
    parser.add_argument("message", nargs="?", help="要发送的消息")
    parser.add_argument("--agent", "-a", help="使用的 agent")
    parser.add_argument("--model", "-m", help="使用的模型")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="超时时间（秒）")
    parser.add_argument("--format", "-f", choices=["default", "json"], default="default", help="输出格式")
    parser.add_argument("--thinking", action="store_true", help="显示思考过程")
    parser.add_argument("--list-agents", action="store_true", help="列出可用 agents")
    parser.add_argument("--list-categories", action="store_true", help="列出可用类别")

    args = parser.parse_args()

    wrapper = OpenCodeWrapper(timeout=args.timeout)

    # 列出 agents 和类别不需要 message
    if args.list_agents or args.list_categories:
        pass
    elif not args.message:
        parser.error("message is required unless --list-agents or --list-categories is used")

    if args.list_agents:
        agents = wrapper.list_agents()
        print("Available agents:")
        for agent in agents:
            print(f"  - {agent}")
        return

    if args.list_categories:
        categories = wrapper.list_categories()
        print("Available categories:")
        for category in categories:
            print(f"  - {category}")
        return

    try:
        output = wrapper.run(
            message=args.message,
            agent=args.agent,
            model=args.model,
            format=args.format,
            thinking=args.thinking,
        )
        print(output, end='')
    except OpenCodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
