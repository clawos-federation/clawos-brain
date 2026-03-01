#!/usr/bin/env python3
"""
进度追踪机制 - Progress Tracking System
实时追踪任务进度，提供可视化反馈和状态更新
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 等待中
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消
    PAUSED = "paused"             # 已暂停


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self):
        # 活跃任务存储
        self.active_tasks: Dict[str, Dict] = {}
        
        # 历史任务存储
        self.history: Dict[str, Dict] = {}
        
        # 进度回调函数
        self.callbacks: Dict[str, List[callable]] = {
            "on_step": [],
            "on_progress": [],
            "on_complete": [],
            "on_error": []
        }
    
    def create_task(self, task_id: str, handler: str, task: str,
                   steps: List[Dict], context: Dict = None) -> Dict:
        """
        创建新任务
        
        Args:
            task_id: 任务唯一ID
            handler: 处理者名称
            task: 任务描述
            steps: 步骤列表 [{"step": "步骤1", "description": "详情"}, ...]
            context: 额外上下文
        
        Returns:
            任务创建结果
        """
        if context is None:
            context = {}
        
        # 检查任务是否已存在
        if task_id in self.active_tasks:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 已存在"
            }
        
        # 创建任务
        task_data = {
            "task_id": task_id,
            "handler": handler,
            "task": task,
            "context": context,
            "steps": steps,
            "total_steps": len(steps),
            "current_step": 0,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "failed_at": None,
            "error": None,
            "progress": 0.0,
            "step_history": [],
            "metadata": {
                "cancellable": True,
                "pausable": True,
                "estimated_duration": None
            }
        }
        
        # 估算持续时间
        task_data["metadata"]["estimated_duration"] = self._estimate_duration(steps)
        
        self.active_tasks[task_id] = task_data
        
        # 触发回调
        self._trigger_callbacks("on_progress", {
            "task_id": task_id,
            "status": "created",
            "progress": 0.0
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "estimated_duration": task_data["metadata"]["estimated_duration"],
            "created_at": task_data["created_at"].isoformat()
        }
    
    def start_task(self, task_id: str) -> Dict:
        """开始任务"""
        task = self.active_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不存在"
            }
        
        if task["status"] != TaskStatus.PENDING.value:
            return {
                "success": False,
                "message": f"任务状态为 '{task['status']}'，无法开始"
            }
        
        task["status"] = TaskStatus.IN_PROGRESS.value
        task["started_at"] = datetime.now()
        
        return {
            "success": True,
            "task_id": task_id,
            "started_at": task["started_at"].isoformat()
        }
    
    def update_step(self, task_id: str, step_index: int, 
                   result: Dict = None) -> Dict:
        """
        更新步骤状态
        
        Args:
            task_id: 任务ID
            step_index: 步骤索引（0-based）
            result: 步骤结果
        
        Returns:
            更新结果
        """
        task = self.active_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不存在"
            }
        
        if step_index >= len(task["steps"]):
            return {
                "success": False,
                "message": f"步骤索引 {step_index} 超出范围"
            }
        
        # 更新步骤
        step = task["steps"][step_index]
        step["status"] = "completed"
        step["completed_at"] = datetime.now().isoformat()
        if result:
            step["result"] = result
        
        # 记录步骤历史
        task["step_history"].append({
            "step_index": step_index,
            "step": step.get("step", f"步骤{step_index + 1}"),
            "description": step.get("description", ""),
            "completed_at": step["completed_at"],
            "result": result
        })
        
        # 更新当前步骤
        task["current_step"] = step_index + 1
        
        # 计算进度
        task["progress"] = (task["current_step"] / task["total_steps"]) * 100
        
        # 触发回调
        self._trigger_callbacks("on_step", {
            "task_id": task_id,
            "step_index": step_index,
            "step": step,
            "progress": task["progress"]
        })
        
        self._trigger_callbacks("on_progress", {
            "task_id": task_id,
            "progress": task["progress"],
            "current_step": step_index + 1,
            "total_steps": task["total_steps"]
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "step_index": step_index,
            "progress": task["progress"]
        }
    
    def complete_task(self, task_id: str, result: Dict = None) -> Dict:
        """完成任务"""
        task = self.active_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不存在"
            }
        
        # 更新状态
        task["status"] = TaskStatus.COMPLETED.value
        task["completed_at"] = datetime.now()
        task["progress"] = 100.0
        if result:
            task["result"] = result
        
        # 计算持续时间
        if task["started_at"]:
            task["duration"] = (task["completed_at"] - task["started_at"]).total_seconds()
        
        # 移动到历史
        self.history[task_id] = task.copy()
        del self.active_tasks[task_id]
        
        # 触发回调
        self._trigger_callbacks("on_complete", {
            "task_id": task_id,
            "duration": task.get("duration"),
            "result": result
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "completed_at": task["completed_at"].isoformat(),
            "duration": task.get("duration")
        }
    
    def fail_task(self, task_id: str, error: str) -> Dict:
        """标记任务失败"""
        task = self.active_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不存在"
            }
        
        task["status"] = TaskStatus.FAILED.value
        task["failed_at"] = datetime.now()
        task["error"] = error
        
        # 计算持续时间
        if task["started_at"]:
            task["duration"] = (task["failed_at"] - task["started_at"]).total_seconds()
        
        # 移动到历史
        self.history[task_id] = task.copy()
        del self.active_tasks[task_id]
        
        # 触发回调
        self._trigger_callbacks("on_error", {
            "task_id": task_id,
            "error": error,
            "failed_at": task["failed_at"].isoformat()
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "error": error,
            "failed_at": task["failed_at"].isoformat()
        }
    
    def cancel_task(self, task_id: str) -> Dict:
        """取消任务"""
        task = self.active_tasks.get(task_id)
        
        if not task:
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不存在"
            }
        
        if not task["metadata"].get("cancellable", False):
            return {
                "success": False,
                "message": f"任务 '{task_id}' 不可取消"
            }
        
        task["status"] = TaskStatus.CANCELLED.value
        task["cancelled_at"] = datetime.now()
        
        # 计算持续时间
        if task["started_at"]:
            task["duration"] = (task["cancelled_at"] - task["started_at"]).total_seconds()
        
        # 移动到历史
        self.history[task_id] = task.copy()
        del self.active_tasks[task_id]
        
        return {
            "success": True,
            "task_id": task_id,
            "cancelled_at": task["cancelled_at"].isoformat()
        }
    
    def get_progress(self, task_id: str) -> Optional[Dict]:
        """获取任务进度"""
        task = self.active_tasks.get(task_id)
        
        if not task:
            return None
        
        # 计算统计信息
        elapsed = None
        remaining = None
        eta = None
        
        if task["started_at"]:
            elapsed = datetime.now() - task["started_at"]
            
            if task["current_step"] > 0:
                avg_time_per_step = elapsed / task["current_step"]
                remaining_steps = task["total_steps"] - task["current_step"]
                remaining = avg_time_per_step * remaining_steps
                eta = datetime.now() + remaining
        
        return {
            "task_id": task_id,
            "handler": task["handler"],
            "task": task["task"],
            "status": task["status"],
            "progress": task["progress"],
            "current_step": task["current_step"],
            "total_steps": task["total_steps"],
            "current_step_name": task["steps"][task["current_step"]]["step"] if task["current_step"] < len(task["steps"]) else "完成",
            "elapsed": str(elapsed) if elapsed else "未开始",
            "remaining": str(remaining) if remaining else "未知",
            "eta": eta.isoformat() if eta else "未知",
            "estimated_duration": task["metadata"].get("estimated_duration"),
            "step_history": task["step_history"]
        }
    
    def get_all_active_tasks(self) -> List[Dict]:
        """获取所有活跃任务"""
        tasks = []
        for task_id, task in self.active_tasks.items():
            progress = self.get_progress(task_id)
            if progress:
                tasks.append(progress)
        return tasks
    
    def get_task_history(self, limit: int = 20) -> List[Dict]:
        """获取任务历史"""
        history = list(self.history.values())
        
        # 按完成时间倒序排序
        history.sort(
            key=lambda t: t.get("completed_at") or t.get("failed_at") or t.get("cancelled_at") or datetime.min,
            reverse=True
        )
        
        return history[:limit]
    
    def register_callback(self, event: str, callback: callable):
        """注册回调函数"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, data: Dict):
        """触发回调"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _estimate_duration(self, steps: List[Dict]) -> Dict:
        """估算任务持续时间"""
        # 基于步骤数量和复杂度估算
        total_steps = len(steps)
        
        # 每步骤平均时间（秒）
        avg_time_per_step = 30  # 默认30秒
        
        # 根据步骤类型调整
        for step in steps:
            step_type = step.get("type", "normal")
            if step_type == "complex":
                avg_time_per_step += 30
            elif step_type == "simple":
                avg_time_per_step -= 10
            elif step_type == "heavy":
                avg_time_per_step += 60
        
        total_seconds = total_steps * max(avg_time_per_step, 10)
        
        # 格式化
        if total_seconds < 60:
            return {
                "total_seconds": total_seconds,
                "formatted": f"{total_seconds}秒"
            }
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return {
                "total_seconds": total_seconds,
                "formatted": f"{minutes}分钟"
            }
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return {
                "total_seconds": total_seconds,
                "formatted": f"{hours}小时{minutes}分钟"
            }


class ProgressVisualizer:
    """进度可视化器"""
    
    @staticmethod
    def render_progress_bar(progress: float, width: int = 50) -> str:
        """渲染进度条"""
        filled = int((progress / 100) * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {progress:.1f}%"
    
    @staticmethod
    def render_step_list(steps: List[Dict], current_step: int) -> str:
        """渲染步骤列表"""
        lines = []
        for i, step in enumerate(steps):
            status_icon = "✓" if i < current_step else "→" if i == current_step else "○"
            status_color = "green" if i < current_step else "yellow" if i == current_step else "gray"
            
            lines.append(f"  {status_icon} {step.get('step', f'Step {i+1}')}")
            lines.append(f"     {step.get('description', '')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_full_progress(progress: Dict) -> str:
        """渲染完整进度信息"""
        output = []
        
        output.append(f"╔════════════════════════════════════════════════════════════════╗")
        output.append(f"║  📊 任务进度                                                      ║")
        output.append(f"╠════════════════════════════════════════════════════════════════╣")
        output.append(f"║                                                                  ║")
        output.append(f"  任务ID: {progress['task_id']:<50}                ║")
        output.append(f"  处理者: {progress['handler']:<50}                 ║")
        output.append(f"  状态: {progress['status'].upper():<50}                     ║")
        output.append(f"                                                                  ║")
        
        # 进度条
        progress_bar = ProgressVisualizer.render_progress_bar(progress['progress'])
        output.append(f"  进度: {progress_bar}")
        output.append(f"        {progress['current_step']} / {progress['total_steps']} 步骤")
        output.append(f"                                                                  ║")
        
        # 时间信息
        output.append(f"  ⏱️  时间信息                                                      ║")
        output.append(f"     已用时间: {progress['elapsed']:<40}              ║")
        output.append(f"     剩余时间: {progress['remaining']:<40}              ║")
        output.append(f"     预计完成: {progress['eta']:<40}                 ║")
        output.append(f"                                                                  ║")
        
        output.append(f"╚════════════════════════════════════════════════════════════════╝")
        
        return "\n".join(output)


def main():
    """测试进度追踪系统"""
    tracker = ProgressTracker()
    
    print("=" * 80)
    print("进度追踪系统测试")
    print("=" * 80)
    
    # 创建任务
    task_id = "task-test-001"
    steps = [
        {"step": "步骤1", "description": "读取项目文件", "type": "simple"},
        {"step": "步骤2", "description": "分析代码结构", "type": "normal"},
        {"step": "步骤3", "description": "生成代码", "type": "complex"},
        {"step": "步骤4", "description": "运行测试", "type": "normal"},
        {"step": "步骤5", "description": "生成报告", "type": "simple"}
    ]
    
    result = tracker.create_task(
        task_id=task_id,
        handler="Henry",
        task="创建一个 URL Shortener 类",
        steps=steps
    )
    
    print(f"\n✅ 任务创建成功")
    print(f"   任务ID: {result['task_id']}")
    print(f"   预计耗时: {result['estimated_duration']['formatted']}")
    
    # 开始任务
    tracker.start_task(task_id)
    print(f"\n▶️  任务开始")
    
    # 模拟执行步骤
    print(f"\n执行步骤...")
    for i in range(len(steps)):
        time.sleep(0.5)  # 模拟处理时间
        tracker.update_step(task_id, i, {"output": f"步骤{i+1} 完成"})
        
        # 显示进度
        progress = tracker.get_progress(task_id)
        visual = ProgressVisualizer.render_full_progress(progress)
        print(f"\n{visual}")
    
    # 完成任务
    result = tracker.complete_task(task_id, {
        "summary": "成功创建 URL Shortener 类",
        "quality_score": 8.5
    })
    
    print(f"\n✅ 任务完成")
    print(f"   完成时间: {result['completed_at']}")
    print(f"   总耗时: {result['duration']:.2f}秒")
    
    # 显示任务历史
    print(f"\n📋 任务历史:")
    history = tracker.get_task_history(limit=5)
    for task in history:
        print(f"   - {task['task_id']}: {task['status']} ({task['duration']:.1f}s)")


if __name__ == "__main__":
    main()
