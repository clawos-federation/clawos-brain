#!/usr/bin/env python3
"""
P0 优化系统集成 - P0 System Integration
整合所有 P0 优化组件，提供统一的接口
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# 导入 P0 组件
from task_classifier import AdvancedTaskClassifier
from henry_self_checker import HenrySelfChecker
from agent_transparency import AgentTransparency
from progress_tracker import ProgressTracker, TaskStatus, ProgressVisualizer


class P0System:
    """P0 优化系统统一接口"""
    
    def __init__(self):
        # 初始化 P0 组件
        self.classifier = AdvancedTaskClassifier()
        self.self_checker = HenrySelfChecker()
        self.transparency = AgentTransparency()
        self.progress = ProgressTracker()
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "henry_tasks": 0,
            "gm_agent_tasks": 0,
            "assisted_tasks": 0,
            "cancelled_tasks": 0,
            "failed_tasks": 0,
            "avg_response_time": 0.0
        }
    
    def process_task(self, task: str, context: Dict = None, 
                     handler_override: str = None) -> Dict:
        """
        处理任务（完整流程）
        
        Args:
            task: 任务描述
            context: 上下文信息（可选）
            handler_override: 强制指定处理者（可选）
        
        Returns:
            处理结果
        """
        if context is None:
            context = {}
        
        start_time = datetime.now()
        
        # 1. 任务分类
        classification = self.classifier.classify(task, context)
        
        # 如果有强制指定处理者，则覆盖
        if handler_override:
            classification["decision"]["handler"] = handler_override
        
        handler = classification["decision"]["handler"]
        mode = classification["decision"]["mode"]
        
        # 2. 显示 Agent 信息（透明度）
        agent_info = self.transparency.show_agent_info(
            handler, task, mode
        )
        
        # 3. 创建进度跟踪任务
        task_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 生成任务步骤
        steps = self._generate_steps(task, handler, mode, classification)
        
        self.progress.create_task(
            task_id=task_id,
            handler=handler,
            task=task,
            steps=steps,
            context=context
        )
        
        # 4. 开始任务
        self.progress.start_task(task_id)
        
        # 5. 根据 handler 处理任务
        result = {
            "task_id": task_id,
            "task": task,
            "handler": handler,
            "mode": mode,
            "classification": classification,
            "agent_info": agent_info,
            "transparency": True
        }
        
        # 模拟处理（实际应由各 Agent 执行）
        execution_result = self._simulate_execution(task, handler, mode, task_id)
        result["execution"] = execution_result
        
        # 6. 如果是 Henry，执行自我质量检查
        if handler == "Henry":
            self_check = self.self_checker.check(
                execution_result, task, context
            )
            result["self_check"] = self_check
            
            # 如果检查未通过，上报 GM Agent
            if not self_check["passed"]:
                result["escalated"] = True
                result["escalation_reason"] = "质量检查未通过"
                # 这里可以触发 GM Agent 接管
        else:
            result["self_check"] = {"not_applicable": True}
        
        # 7. 完成任务
        self.progress.complete_task(task_id, result)
        
        # 8. 显示完成信息
        completion_info = self.transparency.show_task_completion(
            task_id, {
                "passed": result.get("self_check", {}).get("passed", True),
                "quality_score": result.get("execution", {}).get("quality_score", 0),
                "summary": execution_result.get("summary", "任务完成")
            }
        )
        result["completion_info"] = completion_info
        
        # 9. 更新统计
        duration = (datetime.now() - start_time).total_seconds()
        self._update_stats(handler, mode, duration)
        
        return result
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        progress = self.progress.get_progress(task_id)
        
        if progress:
            return {
                **progress,
                "visual": ProgressVisualizer.render_full_progress(progress)
            }
        
        return None
    
    def get_all_active_tasks(self) -> List[Dict]:
        """获取所有活跃任务"""
        return self.progress.get_all_active_tasks()
    
    def cancel_task(self, task_id: str) -> Dict:
        """取消任务"""
        return self.progress.cancel_task(task_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "uptime": str(datetime.now() - datetime(2026, 2, 10)),  # 假设启动时间
            "components": {
                "task_classifier": "✅ 活跃",
                "henry_self_checker": "✅ 活跃",
                "agent_transparency": "✅ 活跃",
                "progress_tracker": "✅ 活跃"
            }
        }
    
    def _generate_steps(self, task: str, handler: str, mode: str, 
                       classification: Dict) -> List[Dict]:
        """生成任务步骤"""
        steps = []
        
        # 通用步骤
        if handler == "Henry":
            if mode == "solo":
                steps = [
                    {"step": "理解任务", "description": "分析任务要求", "type": "simple"},
                    {"step": "执行任务", "description": "快速处理任务", "type": "normal"},
                    {"step": "质量检查", "description": "自我质量检查", "type": "simple"},
                    {"step": "输出结果", "description": "格式化并输出结果", "type": "simple"}
                ]
            elif mode == "assisted":
                steps = [
                    {"step": "理解任务", "description": "初步分析任务", "type": "simple"},
                    {"step": "执行任务", "description": "处理任务", "type": "normal"},
                    {"step": "质量检查", "description": "Henry 自我检查", "type": "simple"},
                    {"step": "上报审查", "description": "提交 GM Agent 审查", "type": "normal"},
                    {"step": "输出结果", "description": "最终输出", "type": "simple"}
                ]
        elif handler == "GM Agent":
            steps = [
                {"step": "深度分析", "description": "第一性原理深度分析", "type": "complex"},
                {"step": "需求确认", "description": "苏格拉底式提问确认需求", "type": "normal"},
                {"step": "资源规划", "description": "规划专业 Agents", "type": "normal"},
                {"step": "任务分配", "description": "分配任务给专业 Agents", "type": "complex"},
                {"step": "质量把关", "description": "执行质量把关（7/10阈值）", "type": "complex"},
                {"step": "风险预判", "description": "风险分析和预防", "type": "normal"},
                {"step": "结果整合", "description": "整合并输出结果", "type": "normal"}
            ]
        
        return steps
    
    def _simulate_execution(self, task: str, handler: str, 
                            mode: str, task_id: str) -> Dict:
        """模拟任务执行（实际应由各 Agent 执行）"""
        import time
        import random
        
        # 模拟执行时间
        if handler == "Henry":
            if mode == "solo":
                time.sleep(0.5)
                quality_score = random.uniform(7.5, 9.0)
            else:
                time.sleep(1.0)
                quality_score = random.uniform(8.0, 9.5)
        else:  # GM Agent
            time.sleep(2.0)
            quality_score = random.uniform(8.5, 9.8)
        
        # 更新进度
        steps = self.progress.active_tasks[task_id]["steps"]
        for i, step in enumerate(steps):
            time.sleep(0.2)
            self.progress.update_step(task_id, i, {"output": f"{step['step']} 完成"})
        
        # 返回模拟结果
        return {
            "success": True,
            "quality_score": quality_score,
            "summary": f"任务完成：{task[:50]}...",
            "details": {
                "handler": handler,
                "mode": mode,
                "steps_completed": len(steps),
                "estimated_efficiency": "高"
            }
        }
    
    def _update_stats(self, handler: str, mode: str, duration: float):
        """更新统计信息"""
        self.stats["total_tasks"] += 1
        
        if handler == "Henry":
            self.stats["henry_tasks"] += 1
        elif handler == "GM Agent":
            self.stats["gm_agent_tasks"] += 1
        
        if mode == "assisted":
            self.stats["assisted_tasks"] += 1
        
        # 更新平均响应时间
        current_avg = self.stats["avg_response_time"]
        total = self.stats["total_tasks"]
        self.stats["avg_response_time"] = (
            (current_avg * (total - 1) + duration) / total
        )


def main():
    """测试 P0 系统"""
    system = P0System()
    
    print("=" * 80)
    print("P0 优化系统测试")
    print("=" * 80)
    
    # 测试案例
    test_tasks = [
        "创建一个 README 文件",
        "创建一个用户认证系统（带 OAuth）",
        "构建完整的电商后端系统",
        "搜索最新的 AI 新闻",
        "修复生产环境的关键 Bug"
    ]
    
    print(f"\n{'=' * 80}")
    print(f"测试 {len(test_tasks)} 个任务")
    print(f"{'=' * 80}\n")
    
    results = []
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'─' * 80}")
        print(f"任务 {i}/{len(test_tasks)}: {task}")
        print(f"{'─' * 80}\n")
        
        result = system.process_task(task)
        results.append(result)
        
        print(f"\n✅ 处理完成")
        print(f"   处理者: {result['handler']}")
        print(f"   模式: {result['mode']}")
        print(f"   质量评分: {result['execution']['quality_score']:.1f}/10")
        print(f"   自我检查: {'通过' if result.get('self_check', {}).get('passed', True) else '未通过'}")
        print(f"   任务ID: {result['task_id']}")
    
    # 显示统计
    print(f"\n{'=' * 80}")
    print("系统统计")
    print(f"{'=' * 80}")
    
    stats = system.get_stats()
    print(f"\n总任务数: {stats['total_tasks']}")
    print(f"Henry 处理: {stats['henry_tasks']}")
    print(f"GM Agent 处理: {stats['gm_agent_tasks']}")
    print(f"辅助模式: {stats['assisted_tasks']}")
    print(f"平均响应时间: {stats['avg_response_time']:.2f}秒")
    print(f"\n组件状态:")
    for component, status in stats['components'].items():
        print(f"  - {component}: {status}")


if __name__ == "__main__":
    main()
