#!/usr/bin/env python3
"""
Henry Wrapper - Chairman's Assistant
快速理解 → 任务路由 → 简单任务处理
"""

import json
import sys
from datetime import datetime

class HenryAssistant:
    """Henry - 董事长助理"""
    
    def __init__(self):
        self.model = "opencode/kimi-k2.5-free"
        self.name = "Henry"
    
    def quick_understand(self, task: str) -> dict:
        """
        快速理解用户意图（第一性原理 x3）
        """
        print(f"\n🔍 Henry: 快速分析任务...")
        
        # 快速理解（3个关键问题）
        understanding = {
            "core_problem": self._extract_core_problem(task),
            "success_criteria": self._extract_success_criteria(task),
            "constraints": self._extract_constraints(task)
        }
        
        return understanding
    
    def classify_task(self, task: str) -> dict:
        """
        任务分类：简单 vs 复杂
        """
        # 简单任务标准：≤3 步骤
        simple_indicators = [
            "write a file",
            "read a file", 
            "search the web",
            "send a message",
            "create a simple script"
        ]
        
        # 检查是否为简单任务
        task_lower = task.lower()
        is_simple = any(indicator in task_lower for indicator in simple_indicators)
        
        # 估算步骤数
        estimated_steps = self._estimate_steps(task)
        
        return {
            "is_simple": is_simple or estimated_steps <= 3,
            "estimated_steps": estimated_steps,
            "recommended_handler": "Henry" if estimated_steps <= 3 else "GM Agent"
        }
    
    def handle_simple_task(self, task: str) -> dict:
        """
        处理简单任务
        """
        print(f"\n✅ Henry: 处理简单任务")
        print(f"   任务: {task}")
        
        # 1. 快速理解
        understanding = self.quick_understand(task)
        
        # 2. 执行任务（使用 OpenClaw tools）
        result = self._execute_task(task)
        
        # 3. 简单质量检查
        quality_check = self._basic_quality_check(result)
        
        return {
            "status": "success" if quality_check["passed"] else "needs_revision",
            "understanding": understanding,
            "result": result,
            "quality": quality_check
        }
    
    def escalate_to_gm(self, task: str, context: dict) -> dict:
        """
        上报复杂任务给 GM Agent
        """
        print(f"\n🔄 Henry: 上报复杂任务给 GM Agent")
        
        escalation = {
            "original_task": task,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "recommended_action": "GM Agent Review Required"
        }
        
        return escalation
    
    def _extract_core_problem(self, task: str) -> str:
        """提取核心问题"""
        # 简单关键词提取
        core_keywords = ["build", "create", "write", "fix", "analyze", "find", "search"]
        for keyword in core_keywords:
            if keyword in task.lower():
                return f"需要{keyword}相关的内容"
        return "需要进一步理解"
    
    def _extract_success_criteria(self, task: str) -> str:
        """提取成功标准"""
        return "完成任务要求"
    
    def _extract_constraints(self, task: str) -> list:
        """提取约束条件"""
        constraints = []
        
        if "fast" in task.lower() or "quick" in task.lower():
            constraints.append("需要快速完成")
        
        if "cheap" in task.lower() or "free" in task.lower():
            constraints.append("预算有限")
        
        return constraints
    
    def _estimate_steps(self, task: str) -> int:
        """估算步骤数"""
        step_count = 1
        
        if "and" in task.lower():
            step_count += task.lower().count("and")
        
        if " with " in task.lower() or " using " in task.lower():
            step_count += 1
        
        if "test" in task.lower():
            step_count += 1
        
        return min(step_count, 10)  # 最多10步
    
    def _execute_task(self, task: str) -> dict:
        """执行任务（模拟）"""
        return {
            "executed": True,
            "tool_used": self._select_tool(task),
            "result": f"完成: {task}"
        }
    
    def _select_tool(self, task: str) -> str:
        """选择工具"""
        task_lower = task.lower()
        
        if "file" in task_lower or "write" in task_lower or "create" in task_lower:
            return "write"
        elif "read" in task_lower or "show" in task_lower:
            return "read"
        elif "search" in task_lower or "find" in task_lower:
            return "web_search"
        elif "run" in task_lower or "execute" in task_lower:
            return "exec"
        else:
            return "general"
    
    def _basic_quality_check(self, result: dict) -> dict:
        """基础质量检查"""
        return {
            "passed": result.get("executed", False),
            "checks": {
                "executed": result.get("executed", False),
                "has_result": result.get("result") is not None
            }
        }


def main():
    """Henry 主入口"""
    if len(sys.argv) < 2:
        print("Usage: henry_wrapper.py <task>")
        print("Example: henry_wrapper.py 'write a README file'")
        sys.exit(1)
    
    task = sys.argv[1]
    
    henry = HenryAssistant()
    
    # 1. 快速理解
    understanding = henry.quick_understand(task)
    print(f"   理解: {understanding}")
    
    # 2. 任务分类
    classification = henry.classify_task(task)
    print(f"   分类: {classification}")
    
    # 3. 处理或上报
    if classification["is_simple"]:
        result = henry.handle_simple_task(task)
    else:
        result = henry.escalate_to_gm(task, understanding)
    
    print(f"\n📊 结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    main()
