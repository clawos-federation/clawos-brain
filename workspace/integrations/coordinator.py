#!/usr/bin/env python3
"""
OpenClaw Coordinator - 协调系统
Henry (助理) + GM Agent (总经理) 协同工作
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# 导入 wrapper
sys.path.insert(0, '/Users/henry/openclaw-system/workspace/integrations')
from henry_wrapper import HenryAssistant
from gm_agent_wrapper import GMAgent


class OpenClawCoordinator:
    """
    OpenClaw 协调器
    
    职责：
    1. 接收用户请求
    2. 通过 Henry 进行初步筛选
    3. 简单任务：Henry 直接处理
    4. 复杂任务：Henry 上报 → GM Agent 深度处理 → GM Agent 质量把关 → Henry 汇总
    """
    
    def __init__(self):
        self.henry = HenryAssistant()
        self.gm_agent = GMAgent()
        self.simple_threshold = 3  # 步骤数阈值
    
    def process_request(self, task: str, verbose: bool = True) -> dict:
        """
        处理用户请求的主入口
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"🚀 OpenClaw Enterprise System")
            print(f"{'='*60}")
            print(f"📩 用户请求: {task}")
            print(f"{'='*60}\n")
        
        # Step 1: Henry 初步筛选
        if verbose:
            print(f"👔 Step 1: Henry 初步筛选")
            print(f"{'─'*60}")
        
        henry_result = self._henry_initial_screening(task, verbose)
        
        # Step 2: 根据复杂度决定处理路径
        if henry_result["classification"]["is_simple"]:
            # 简单任务路径：Henry 直接处理
            if verbose:
                print(f"\n✅ 路径: Henry 直接处理 (简单任务)")
            
            final_result = self._handle_simple_task(task, henry_result, verbose)
        else:
            # 复杂任务路径：Henry → GM Agent → 专业 Agents
            if verbose:
                print(f"\n🔄 路径: 复杂任务 - Henry 上报 → GM Agent")
            
            final_result = self._handle_complex_task(task, henry_result, verbose)
        
        # Step 3: Henry 汇总输出
        if verbose:
            print(f"\n{'='*60}")
            print(f"📝 Step 3: Henry 最终汇总")
            print(f"{'='*60}")
        
        summary = self._henry_summary(final_result, verbose)
        
        return summary
    
    def _henry_initial_screening(self, task: str, verbose: bool) -> dict:
        """
        Henry 初步筛选
        """
        # 1. 快速理解
        understanding = self.henry.quick_understand(task)
        
        # 2. 任务分类
        classification = self.henry.classify_task(task)
        
        if verbose:
            print(f"   🔍 快速理解: {understanding['core_problem']}")
            print(f"   📊 复杂度: {classification['estimated_steps']} 步骤")
            print(f"   🎯 处理者: {classification['recommended_handler']}")
        
        return {
            "understanding": understanding,
            "classification": classification
        }
    
    def _handle_simple_task(self, task: str, henry_result: dict, verbose: bool) -> dict:
        """
        处理简单任务（Henry 直接处理）
        """
        print(f"\n{'─'*60}")
        print(f"👔 Step 2a: Henry 处理简单任务")
        print(f"{'─'*60}")
        
        # Henry 执行任务
        result = self.henry.handle_simple_task(task)
        
        if verbose:
            print(f"   ✅ 执行完成")
            print(f"   🔧 使用工具: {result['result']['tool_used']}")
            print(f"   ✓ 质量检查: {'通过' if result['quality']['passed'] else '未通过'}")
        
        return {
            "type": "simple",
            "handler": "Henry",
            "henry_result": result,
            "status": "completed"
        }
    
    def _handle_complex_task(self, task: str, henry_result: dict, verbose: bool) -> dict:
        """
        处理复杂任务（GM Agent 深度处理）
        """
        print(f"\n{'─'*60}")
        print(f"🤵 Step 2b: GM Agent 深度处理")
        print(f"{'─'*60}")
        
        # 1. 深度第一性原理分析
        if verbose:
            print(f"   🔬 深度分析...")
        analysis = self.gm_agent.deep_first_principles(task)
        
        # 2. 战略规划
        if verbose:
            print(f"   📊 战略规划...")
        plan = self.gm_agent.strategic_planning(analysis)
        
        # 3. 识别专业 Agents
        if verbose:
            print(f"   👥 识别 Agents: {', '.join(plan.get('agents', []))}")
        agents = self.gm_agent.identify_agents(analysis)
        
        # 4. 任务分配
        if verbose:
            print(f"   📋 任务分配...")
        distributions = self.gm_agent.distribute_tasks(plan, agents)
        
        # 5. 模拟执行（实际场景中会并行执行）
        if verbose:
            print(f"   ⚙️ 模拟专业 Agents 执行...")
        agent_results = self._simulate_agent_execution(distributions, verbose)
        
        # 6. 强制质量把关
        if verbose:
            print(f"   🔒 强制质量把关...")
        quality_results = self._gm_quality_gate(agent_results, verbose)
        
        # 7. 战略创新洞察
        if verbose:
            print(f"   💡 寻找创新机会...")
        innovation_insights = self.gm_agent.strategic_innovation(agent_results)
        
        return {
            "type": "complex",
            "handler": "GM Agent",
            "analysis": analysis,
            "plan": plan,
            "agents": agents,
            "distributions": distributions,
            "agent_results": agent_results,
            "quality_results": quality_results,
            "innovation_insights": innovation_insights,
            "status": "completed"
        }
    
    def _simulate_agent_execution(self, distributions: dict, verbose: bool) -> List[dict]:
        """
        模拟专业 Agents 执行（实际场景中使用真实的 agent 调用）
        """
        results = []
        
        for agent_name, assignment in distributions.items():
            # 模拟执行结果
            mock_result = {
                "agent": agent_name,
                "tasks_completed": assignment["tasks"],
                "output": f"{agent_name} 完成任务",
                "quality_estimate": 7.5 + (hash(agent_name) % 20) / 10  # 模拟评分 7.5-9.5
            }
            results.append(mock_result)
            
            if verbose:
                print(f"      ✓ {agent_name}: 完成 {len(assignment['tasks'])} 项任务")
        
        return results
    
    def _gm_quality_gate(self, agent_results: List[dict], verbose: bool) -> List[dict]:
        """
        GM Agent 质量把关
        """
        quality_results = []
        
        for result in agent_results:
            # 创建模拟工作产品
            work_product = {
                "content": result["output"],
                "agent": result["agent"],
                "quality_estimate": result.get("quality_estimate", 7.0)
            }
            
            # GM Agent 质量检查
            quality = self.gm_agent.mandatory_quality_gate(work_product, result["agent"])
            quality_results.append(quality)
            
            if verbose:
                status = "✅" if quality["passed"] else "❌"
                print(f"      {status} {result['agent']}: {quality['score']}/10 - {quality['badge']}")
        
        return quality_results
    
    def _henry_summary(self, result: dict, verbose: bool) -> dict:
        """
        Henry 汇总输出给用户
        """
        if result["type"] == "simple":
            # 简单任务汇总
            summary = {
                "status": "completed",
                "task_type": "simple",
                "handler": "Henry",
                "quality": result["henry_result"]["quality"],
                "result": result["henry_result"]["result"],
                "next_steps": []
            }
        else:
            # 复杂任务汇总
            all_passed = all(q["passed"] for q in result["quality_results"])
            avg_score = sum(q["score"] for q in result["quality_results"]) / len(result["quality_results"])
            
            summary = {
                "status": "completed" if all_passed else "needs_revision",
                "task_type": "complex",
                "handler": "GM Agent",
                "agents_involved": result["agents"],
                "quality_summary": {
                    "all_passed": all_passed,
                    "average_score": round(avg_score, 1),
                    "badges": [q["badge"] for q in result["quality_results"]]
                },
                "innovation_insights": result["innovation_insights"],
                "next_steps": self._generate_next_steps(result)
            }
        
        if verbose:
            print(f"\n   📊 任务完成")
            print(f"   ✅ 状态: {summary['status']}")
            
            if summary['task_type'] == 'complex':
                print(f"   🏆 平均质量分: {summary['quality_summary']['average_score']}/10")
                print(f"   💡 创新洞察: {len(summary['innovation_insights'])} 项")
            
            print(f"   📝 建议行动: {', '.join(summary['next_steps']) if summary['next_steps'] else '无需后续行动'}")
        
        return summary
    
    def _generate_next_steps(self, result: dict) -> List[str]:
        """生成后续建议"""
        steps = []
        
        # 检查是否有未通过的
        failed_agents = [
            i for i, q in enumerate(result["quality_results"])
            if not q["passed"]
        ]
        
        if failed_agents:
            steps.append(f"修订未通过的 {len(failed_agents)} 个 agent 的工作")
        
        # 检查创新洞察
        if result["innovation_insights"]:
            steps.append("评估创新机会并实施可行的优化")
        
        return steps or ["任务完成，无需后续行动"]


def main():
    """协调系统主入口"""
    if len(sys.argv) < 2:
        print("Usage: coordinator.py <task>")
        print("Examples:")
        print("  Simple: coordinator.py 'write a README file'")
        print("  Complex: coordinator.py 'build a customer portal with AI features'")
        sys.exit(1)
    
    task = sys.argv[1]
    
    # 创建协调器
    coordinator = OpenClawCoordinator()
    
    # 处理请求
    result = coordinator.process_request(task, verbose=True)
    
    # 输出最终结果
    print(f"\n{'='*60}")
    print(f"📦 最终输出")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"{'='*60}\n")
    
    return result


if __name__ == "__main__":
    main()
