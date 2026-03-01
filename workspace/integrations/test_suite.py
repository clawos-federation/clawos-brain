#!/usr/bin/env python3
"""
OpenClaw Enterprise System - Test Suite
测试套件：简单任务和复杂任务
"""

import json
import sys
sys.path.insert(0, '/Users/henry/openclaw-system/workspace/integrations')

from coordinator import OpenClawCoordinator


class OpenClawTestSuite:
    """测试套件"""
    
    def __init__(self):
        self.coordinator = OpenClawCoordinator()
        self.results = []
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("🧪 OpenClaw Enterprise System - Test Suite")
        print("="*70)
        
        # 测试简单任务
        self.test_simple_tasks()
        
        # 测试复杂任务
        self.test_complex_tasks()
        
        # 打印测试报告
        self.print_test_report()
    
    def test_simple_tasks(self):
        """测试简单任务"""
        print("\n" + "-"*70)
        print("📌 测试简单任务 (Henry 直接处理)")
        print("-"*70)
        
        simple_tasks = [
            "write a README file",
            "read the current directory",
            "search for Python best practices",
            "create a simple script",
            "send a test message"
        ]
        
        for i, task in enumerate(simple_tasks, 1):
            print(f"\n  Test {i}: {task}")
            print(f"  {'─'*60}")
            
            try:
                result = self.coordinator.process_request(task, verbose=False)
                
                success = result["task_type"] == "simple" and result["handler"] == "Henry"
                
                self.results.append({
                    "task": task,
                    "type": "simple",
                    "expected_handler": "Henry",
                    "actual_handler": result["handler"],
                    "passed": success
                })
                
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {status} - Handler: {result['handler']}, Status: {result['status']}")
                
            except Exception as e:
                print(f"  ❌ ERROR - {str(e)}")
                self.results.append({
                    "task": task,
                    "type": "simple",
                    "error": str(e),
                    "passed": False
                })
    
    def test_complex_tasks(self):
        """测试复杂任务"""
        print("\n" + "-"*70)
        print("📌 测试复杂任务 (GM Agent 处理)")
        print("-"*70)
        
        complex_tasks = [
            "build a customer portal with AI features and user authentication",
            "develop a full-stack e-commerce platform with payment integration",
            "create a multi-agent system for automated content generation",
            "build a legal document management system with compliance checking",
            "develop a marketing automation platform with analytics"
        ]
        
        for i, task in enumerate(complex_tasks, 1):
            print(f"\n  Test {i}: {task[:60]}...")
            print(f"  {'─'*60}")
            
            try:
                result = self.coordinator.process_request(task, verbose=False)
                
                success = result["task_type"] == "complex" and result["handler"] == "GM Agent"
                
                self.results.append({
                    "task": task[:60] + "...",
                    "type": "complex",
                    "expected_handler": "GM Agent",
                    "actual_handler": result["handler"],
                    "agents_involved": result.get("agents_involved", []),
                    "quality_score": result.get("quality_summary", {}).get("average_score", 0),
                    "passed": success
                })
                
                status = "✅ PASS" if success else "❌ FAIL"
                agents = ", ".join(result.get("agents_involved", [])[:3])
                score = result.get("quality_summary", {}).get("average_score", 0)
                
                print(f"  {status} - Handler: {result['handler']}")
                print(f"         Agents: {agents}")
                print(f"         Quality: {score}/10")
                
            except Exception as e:
                print(f"  ❌ ERROR - {str(e)}")
                self.results.append({
                    "task": task[:60] + "...",
                    "type": "complex",
                    "error": str(e),
                    "passed": False
                })
    
    def print_test_report(self):
        """打印测试报告"""
        print("\n" + "="*70)
        print("📊 Test Report")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("passed", False))
        failed = total - passed
        
        # 按类型统计
        simple_results = [r for r in self.results if r["type"] == "simple"]
        complex_results = [r for r in self.results if r["type"] == "complex"]
        
        print(f"\n  Total Tests: {total}")
        print(f"  ✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"  ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        
        print(f"\n  Simple Tasks: {sum(1 for r in simple_results if r.get('passed', False))}/{len(simple_results)} passed")
        print(f"  Complex Tasks: {sum(1 for r in complex_results if r.get('passed', False))}/{len(complex_results)} passed")
        
        # 详细结果
        print("\n" + "-"*70)
        print("Detailed Results:")
        print("-"*70)
        
        for r in self.results:
            status = "✅" if r.get("passed", False) else "❌"
            task_type = r["type"].upper()
            
            if "error" in r:
                print(f"  {status} [{task_type}] {r['task'][:50]}... - ERROR: {r['error'][:30]}")
            else:
                print(f"  {status} [{task_type}] {r['task'][:50]}...")
        
        print("\n" + "="*70)
        
        # 返回统计
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed/total*100 if total > 0 else 0
        }


def quick_demo():
    """快速演示"""
    print("\n" + "="*70)
    print("🎯 Quick Demo - OpenClaw Enterprise System")
    print("="*70)
    
    coordinator = OpenClawCoordinator()
    
    # Demo 1: 简单任务
    print("\n" + "─"*70)
    print("Demo 1: 简单任务 - 'write a README file'")
    print("─"*70)
    
    result = coordinator.process_request("write a README file", verbose=True)
    
    print(f"\n  结果类型: {result['task_type']}")
    print(f"  处理者: {result['handler']}")
    print(f"  状态: {result['status']}")
    
    # Demo 2: 复杂任务
    print("\n" + "─"*70)
    print("Demo 2: 复杂任务 - 'build a customer portal with AI features'")
    print("─"*70)
    
    result = coordinator.process_request(
        "build a customer portal with AI features", 
        verbose=True
    )
    
    print(f"\n  结果类型: {result['task_type']}")
    print(f"  处理者: {result['handler']}")
    print(f"  状态: {result['status']}")
    
    if result.get("agents_involved"):
        print(f"  涉及 Agents: {', '.join(result['agents_involved'])}")
    
    if result.get("quality_summary"):
        print(f"  平均质量分: {result['quality_summary']['average_score']}/10")
    
    print("\n" + "="*70)


def main():
    """主入口"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        quick_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        suite = OpenClawTestSuite()
        suite.run_all_tests()
    else:
        print("\nOpenClaw Enterprise System - Test Suite")
        print("\nUsage:")
        print("  python test_suite.py --demo    # 快速演示")
        print("  python test_suite.py --test    # 运行测试套件")
        print("\n或者运行单个任务:")
        print("  python coordinator.py 'your task here'")


if __name__ == "__main__":
    main()
