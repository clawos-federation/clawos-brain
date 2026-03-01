#!/usr/bin/env python3
"""
Agent 透明度显示系统 - Agent Transparency Display
为用户提供 Agent 工作透明度，让用户知道谁在处理任务
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json


class AgentTransparency:
    """Agent 透明度显示器"""
    
    def __init__(self):
        # Agent 配置文件
        self.agent_profiles = {
            "Henry": {
                "name": "Henry",
                "role": "董事长助理",
                "avatar": "🤖",
                "model": "Kimi/G-Free (轻量快速)",
                "capabilities": [
                    "快速协调",
                    "简单任务处理",
                    "文件操作",
                    "信息搜索",
                    "基本质量检查"
                ],
                "mode_descriptions": {
                    "solo": "独立处理（快速模式）- Henry 独立完成任务",
                    "assisted": "辅助处理（带审查）- Henry 处理，GM Agent 最终审查",
                    "managed": "管理处理（深度模式）- 完全由 GM Agent 管理"
                },
                "estimated_time": {
                    "solo": "< 2 分钟",
                    "assisted": "3-5 分钟",
                    "managed": "N/A (此模式下不使用)"
                },
                "performance": {
                    "avg_response_time": "30秒",
                    "success_rate": "92%",
                    "user_satisfaction": "4.7/5.0",
                    "avg_tasks_per_session": "15-20"
                }
            },
            "GM Agent": {
                "name": "GM Agent",
                "role": "总经理",
                "avatar": "👔",
                "model": "Claude Opus 4.6 (深度强大)",
                "capabilities": [
                    "战略规划",
                    "深度需求分析",
                    "质量把关",
                    "多Agent 协调",
                    "风险预判",
                    "战略创新洞察"
                ],
                "mode_descriptions": {
                    "managed": "完整管理（深度模式）- GM Agent 全面管理和把控"
                },
                "estimated_time": {
                    "managed": "5-20 分钟（取决于任务复杂度）"
                },
                "performance": {
                    "avg_response_time": "3-10秒",
                    "success_rate": "97%",
                    "user_satisfaction": "4.8/5.0",
                    "avg_tasks_per_session": "3-5（复杂任务）"
                }
            },
            # 其他 Agents 占位
            "CodeAgent": {
                "name": "CodeAgent",
                "role": "代码生成专家",
                "avatar": "💻",
                "model": "GLM-4.7 (代码优化)",
                "capabilities": ["代码生成", "重构", "技术实现"],
                "estimated_time": "5-15 分钟"
            },
            "CodeReviewAgent": {
                "name": "CodeReviewAgent",
                "role": "代码审查专家",
                "avatar": "🔍",
                "model": "Claude Opus 4.6 (深度审查)",
                "capabilities": ["代码审查", "安全检查", "最佳实践"],
                "estimated_time": "3-10 分钟"
            }
        }
        
        # 活跃任务跟踪
        self.active_tasks = {}
    
    def show_agent_info(self, handler: str, task: str, mode: str = "solo") -> str:
        """
        显示 Agent 信息（用户界面）
        
        Args:
            handler: Agent 名称
            task: 任务描述
            mode: 处理模式
        
        Returns:
            格式化的 Agent 信息字符串
        """
        profile = self.agent_profiles.get(handler)
        
        if not profile:
            return f"❌ Agent '{handler}' 未找到"
        
        # 获取模式描述
        mode_desc = profile.get("mode_descriptions", {}).get(
            mode, "标准处理模式"
        )
        
        # 获取时间估算
        time_estimate = profile.get("estimated_time", {}).get(
            mode, "未知"
        )
        
        # 获取性能信息
        perf = profile.get("performance", {})
        
        return f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {profile['avatar']}  {profile['name']} - {profile['role']}                                ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📋 任务信息                                                          ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║     任务: {task[:50]}{'...' if len(task) > 50 else ''}                      ║
║     处理模式: {mode_desc}                      ║
║     预计完成: {time_estimate}                              ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🤖 Agent 信息                                                        ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║     角色: {profile['role']}                                         ║
║     模型: {profile['model']}                              ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║                                                                      ║
║  💪 核心能力                                                        ║
"""
        
        # 添加能力列表
        capabilities = profile.get("capabilities", [])
        for i, capability in enumerate(capabilities, 1):
            bullet = "  ✅ " if i == 1 else "     "
            cap_line = f"║     {bullet}{capability:<40}                      ║"
            agent_info += cap_line + "\n"
        
        # 添加性能信息（如果有）
        if perf:
            agent_info += f"""║                                                                      ║
║  📊 性能数据                                                        ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
"""
            if perf.get("avg_response_time"):
                agent_info += f"""║     平均响应: {perf['avg_response_time']:<30}                      ║
"""
            if perf.get("success_rate"):
                agent_info += f"""║     成功率: {perf['success_rate']:<30}                      ║
"""
            if perf.get("user_satisfaction"):
                agent_info += f"""║     用户评价: {perf['user_satisfaction']:<30}                      ║
"""
        
        agent_info += f"""╚════════════════════════════════════════════════════════════════╝

⏰ 任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 提示: 您可以随时查看任务进度或取消任务（如果任务允许）
"""
        
        return agent_info
    
    def register_active_task(self, task_id: str, handler: str, 
                         task: str, mode: str) -> Dict:
        """
        注册活跃任务
        
        Args:
            task_id: 任务ID
            handler: 处理者
            task: 任务描述
            mode: 处理模式
        
        Returns:
            注册结果
        """
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "handler": handler,
            "task": task,
            "mode": mode,
            "status": "in_progress",
            "started_at": datetime.now(),
            "steps": [],
            "current_step": 0,
            "total_steps": 1
        }
        
        return {
            "success": True,
            "task_id": task_id,
            "registered_at": datetime.now().isoformat()
        }
    
    def show_progress_update(self, task_id: str, step_info: Dict) -> str:
        """
        显示进度更新
        
        Args:
            task_id: 任务ID
            step_info: 步骤信息
        
        Returns:
            格式化的进度更新字符串
        """
        task = self.active_tasks.get(task_id)
        
        if not task:
            return f"❌ 任务 '{task_id}' 未找到"
        
        # 更新步骤
        task["steps"].append(step_info)
        task["current_step"] += 1
        task["total_steps"] = max(task["total_steps"], task["current_step"])
        
        # 计算进度百分比
        progress_pct = (task["current_step"] / task["total_steps"]) * 100
        
        # 计算已用时间
        elapsed = datetime.now() - task["started_at"]
        elapsed_str = self._format_duration(elapsed)
        
        # 估算剩余时间
        avg_time_per_step = elapsed / task["current_step"] if task["current_step"] > 0 else timedelta()
        remaining_steps = task["total_steps"] - task["current_step"]
        remaining_time = avg_time_per_step * remaining_steps
        
        profile = self.agent_profiles.get(task["handler"])
        avatar = profile.get("avatar", "🤖") if profile else "🤖"
        
        return f"""
╔════════════════════════════════════════════════════════════════╗
║  📊 任务进度更新                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  任务ID: {task_id:<50}                           ║
║  处理者: {avatar} {task['handler']:<45}                           ║
║  当前步骤: {task['current_step']:>2}/{task['total_steps']:<2} ({progress_pct:>5.1f}%)                    ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ⚙️ 当前操作                                                         ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║     操作: {step_info.get('operation', 'N/A'):<30}                ║
║     详情: {step_info.get('detail', 'N/A')[:40]:<40}...                 ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ⏱️ 时间信息                                                         ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║     已用时间: {elapsed_str:<25}                            ║
║     预计剩余: {self._format_duration(remaining_time):<25}                          ║
║     开始时间: {task['started_at'].strftime('%Y-%m-%d %H:%M:%S'):<25}                ║
║                                                                      ║
╚════════════════════════════════════════════════════════════════╝

"""
    
    def show_task_completion(self, task_id: str, result: Dict) -> str:
        """
        显示任务完成信息
        
        Args:
            task_id: 任务ID
            result: 任务结果
        
        Returns:
            格式化的完成信息字符串
        """
        task = self.active_tasks.get(task_id)
        
        if not task:
            return f"❌ 任务 '{task_id}' 未找到"
        
        # 更新状态
        task["status"] = "completed"
        task["completed_at"] = datetime.now()
        task["result"] = result
        
        # 计算总时长
        duration = task["completed_at"] - task["started_at"]
        duration_str = self._format_duration(duration)
        
        profile = self.agent_profiles.get(task["handler"])
        avatar = profile.get("avatar", "🤖") if profile else "🤖"
        
        # 获取质量评分
        quality_score = result.get("quality_score", 0)
        passed = result.get("passed", True)
        
        # 质量徽章
        if quality_score >= 9.0:
            quality_badge = "🌟 EXCELLENT"
        elif quality_score >= 8.0:
            quality_badge = "✅ GOOD"
        elif quality_score >= 7.0:
            quality_badge = "⚠️ ACCEPTABLE"
        elif passed:
            quality_badge = "✅ PASSED"
        else:
            quality_badge = "❌ FAILED"
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  ✅ 任务完成                                                          ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  任务ID: {task_id:<50}                           ║
║  处理者: {avatar} {task['handler']:<45}                           ║
║  总耗时: {duration_str:<40}                              ║
║  完成时间: {task['completed_at'].strftime('%Y-%m-%d %H:%M:%S'):<30}                    ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📊 质量评分                                                         ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
║     质量等级: {quality_badge:<40}                            ║
║     质量评分: {quality_score:.1f}/10.0                                   ║
║     通过状态: {'✅ 通过' if passed else '❌ 未通过'}                                ║
║                                                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  📋 结果摘要                                                         ║
║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━      ║
"""
        
        # 添加结果摘要
        summary_lines = []
        if result.get("summary"):
            summary_lines.append(f"║     {result['summary']:<65} ║")
        elif result.get("content"):
            content = result['content'][:60] + "..." if len(result['content']) > 60 else result['content']
            summary_lines.append(f"║     {content:<65} ║")
        else:
            summary_lines.append("║     (无详细摘要)                                                      ║")
        
        for line in summary_lines:
            agent_completion += line + "\n"
        
        agent_completion += f"""║                                                                      ║
╚════════════════════════════════════════════════════════════════╝

💡 提示: 您可以查看详细结果或提供反馈

"""
        
        return agent_completion
    
    def _format_duration(self, duration: timedelta) -> str:
        """格式化持续时间"""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}分{seconds}秒"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}小时{minutes}分"


def main():
    """测试 Agent 透明度系统"""
    transparency = AgentTransparency()
    
    print("=" * 80)
    print("Agent 透明度显示系统测试")
    print("=" * 80)
    
    # 测试1：显示 Agent 信息
    print("\n测试1: 显示 Henry 信息")
    print("-" * 80)
    agent_info = transparency.show_agent_info(
        "Henry", 
        "Create a simple README file for the project",
        "solo"
    )
    print(agent_info)
    
    # 测试2：显示 GM Agent 信息
    print("\n测试2: 显示 GM Agent 信息")
    print("-" * 80)
    agent_info = transparency.show_agent_info(
        "GM Agent",
        "Build a complete user authentication system with OAuth",
        "managed"
    )
    print(agent_info)
    
    # 测试3：注册并跟踪任务
    print("\n测试3: 任务注册和进度跟踪")
    print("-" * 80)
    
    task_id = "task-20260210-001"
    transparency.register_active_task(
        task_id,
        "Henry",
        "Create a README file with installation instructions",
        "solo"
    )
    
    # 模拟进度更新
    steps = [
        {"operation": "读取项目结构", "detail": "扫描文件系统，了解项目布局"},
        {"operation": "生成内容", "detail": "根据项目结构生成 README 内容"},
        {"operation": "写入文件", "detail": "将内容写入 README.md 文件"},
        {"operation": "格式化", "detail": "检查并优化格式"}
    ]
    
    for step in steps:
        progress_update = transparency.show_progress_update(task_id, step)
        print(progress_update)
    
    # 模拟完成
    completion = transparency.show_task_completion(task_id, {
        "passed": True,
        "quality_score": 8.5,
        "summary": "成功创建 README.md 文件，包含完整的项目说明"
    })
    print(completion)


if __name__ == "__main__":
    main()
