#!/usr/bin/env python3
"""
ClawOS 角色记忆管理器
实现记忆归还机制：任务完成 → 经验提炼 → 写回角色记忆
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# 记忆数据结构
# ============================================================================

@dataclass
class MemoryCell:
    """记忆单元"""
    id: str
    timestamp: str
    task_id: str
    role_id: str
    experience_type: str  # success, failure, insight, pattern
    content: str
    context: Dict[str, Any]
    value_score: float  # 0.0 - 1.0
    
    def to_dict(self):
        return asdict(self)

@dataclass  
class RoleMemory:
    """角色记忆"""
    role_id: str
    total_tasks: int
    avg_score: float
    experiences: List[MemoryCell]
    patterns: List[Dict[str, Any]]
    last_updated: str
    
    def to_dict(self):
        return {
            "role_id": self.role_id,
            "total_tasks": self.total_tasks,
            "avg_score": self.avg_score,
            "experiences": [e.to_dict() for e in self.experiences],
            "patterns": self.patterns,
            "last_updated": self.last_updated
        }

# ============================================================================
# 记忆提炼器
# ============================================================================

class MemoryExtractor:
    """从任务执行中提炼记忆"""
    
    def extract(self, task_result: Dict) -> List[MemoryCell]:
        """
        从任务结果中提炼有价值的记忆
        
        Args:
            task_result: 任务执行结果
        
        Returns:
            提炼出的记忆单元列表
        """
        cells = []
        task_id = task_result.get("taskId", "unknown")
        role_id = task_result.get("roleId", "unknown")
        
        # 1. 提取成功经验
        if task_result.get("success"):
            cell = MemoryCell(
                id=self._generate_id(),
                timestamp=datetime.now().isoformat(),
                task_id=task_id,
                role_id=role_id,
                experience_type="success",
                content=self._extract_success_pattern(task_result),
                context={"score": task_result.get("score", 0)},
                value_score=0.7
            )
            cells.append(cell)
        
        # 2. 提取失败教训
        if task_result.get("errors"):
            for error in task_result["errors"]:
                cell = MemoryCell(
                    id=self._generate_id(),
                    timestamp=datetime.now().isoformat(),
                    task_id=task_id,
                    role_id=role_id,
                    experience_type="failure",
                    content=f"避免: {error}",
                    context={},
                    value_score=0.8  # 失败经验价值更高
                )
                cells.append(cell)
        
        # 3. 提取洞察
        if task_result.get("insights"):
            for insight in task_result["insights"]:
                cell = MemoryCell(
                    id=self._generate_id(),
                    timestamp=datetime.now().isoformat(),
                    task_id=task_id,
                    role_id=role_id,
                    experience_type="insight",
                    content=insight,
                    context={},
                    value_score=0.6
                )
                cells.append(cell)
        
        # 4. 提取模式
        if task_result.get("patterns"):
            for pattern in task_result["patterns"]:
                cell = MemoryCell(
                    id=self._generate_id(),
                    timestamp=datetime.now().isoformat(),
                    task_id=task_id,
                    role_id=role_id,
                    experience_type="pattern",
                    content=pattern,
                    context={},
                    value_score=0.5
                )
                cells.append(cell)
        
        return cells
    
    def _extract_success_pattern(self, task_result: Dict) -> str:
        """提取成功模式"""
        approach = task_result.get("approach", "")
        tools_used = task_result.get("tools_used", [])
        
        pattern = f"成功方法: {approach}"
        if tools_used:
            pattern += f" (工具: {', '.join(tools_used)})"
        
        return pattern
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]

# ============================================================================
# 记忆管理器
# ============================================================================

class RoleMemoryManager:
    """角色记忆管理器"""
    
    def __init__(self, memory_base_path: str = "~/openclaw-system/clawos/memory"):
        self.base_path = Path(memory_base_path).expanduser()
        self.workers_path = self.base_path / "workers"
        self.workers_path.mkdir(parents=True, exist_ok=True)
        
        self.extractor = MemoryExtractor()
    
    def return_memory(self, task_result: Dict) -> bool:
        """
        任务完成后归还记忆
        
        Args:
            task_result: 任务执行结果
        
        Returns:
            是否成功
        """
        role_id = task_result.get("roleId")
        if not role_id:
            return False
        
        # 1. 提炼记忆
        new_cells = self.extractor.extract(task_result)
        
        if not new_cells:
            return True  # 无需记忆
        
        # 2. 加载现有角色记忆
        role_memory = self._load_role_memory(role_id)
        
        # 3. 合并新记忆
        role_memory.experiences.extend(new_cells)
        role_memory.total_tasks += 1
        
        # 4. 更新平均分
        score = task_result.get("score", 0)
        if score > 0:
            old_avg = role_memory.avg_score
            old_count = role_memory.total_tasks - 1
            role_memory.avg_score = (old_avg * old_count + score) / role_memory.total_tasks
        
        # 5. 更新模式
        self._update_patterns(role_memory)
        
        # 6. 压缩记忆（保留高价值）
        self._compress_memory(role_memory)
        
        # 7. 更新时间戳
        role_memory.last_updated = datetime.now().isoformat()
        
        # 8. 保存
        self._save_role_memory(role_memory)
        
        return True
    
    def get_role_memory(self, role_id: str) -> Optional[RoleMemory]:
        """
        获取角色记忆（用于实例化时注入）
        
        Args:
            role_id: 角色ID
        
        Returns:
            角色记忆
        """
        return self._load_role_memory(role_id)
    
    def get_role_memory_summary(self, role_id: str) -> str:
        """
        获取角色记忆摘要（用于注入系统提示）
        
        Args:
            role_id: 角色ID
        
        Returns:
            记忆摘要文本
        """
        memory = self._load_role_memory(role_id)
        
        if not memory.experiences:
            return "这是一个新角色，尚无历史经验。"
        
        lines = [
            f"## 角色经验 ({role_id})",
            f"- 完成任务: {memory.total_tasks}",
            f"- 平均评分: {memory.avg_score:.1f}",
            "",
            "### 关键经验:"
        ]
        
        # 按价值排序，取前10条
        sorted_exp = sorted(
            memory.experiences, 
            key=lambda x: x.value_score, 
            reverse=True
        )[:10]
        
        for exp in sorted_exp:
            lines.append(f"- [{exp.experience_type}] {exp.content}")
        
        if memory.patterns:
            lines.append("")
            lines.append("### 已识别模式:")
            for p in memory.patterns[:5]:
                lines.append(f"- {p.get('description', '')}")
        
        return "\n".join(lines)
    
    def _load_role_memory(self, role_id: str) -> RoleMemory:
        """加载角色记忆"""
        memory_file = self.workers_path / f"{role_id}.mem.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                experiences = [
                    MemoryCell(**e) for e in data.get("experiences", [])
                ]
                
                return RoleMemory(
                    role_id=role_id,
                    total_tasks=data.get("total_tasks", 0),
                    avg_score=data.get("avg_score", 0.0),
                    experiences=experiences,
                    patterns=data.get("patterns", []),
                    last_updated=data.get("last_updated", "")
                )
            except:
                pass
        
        # 返回空记忆
        return RoleMemory(
            role_id=role_id,
            total_tasks=0,
            avg_score=0.0,
            experiences=[],
            patterns=[],
            last_updated=""
        )
    
    def _save_role_memory(self, memory: RoleMemory):
        """保存角色记忆"""
        memory_file = self.workers_path / f"{memory.role_id}.mem.json"
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 同时保存 Markdown 版本（人类可读）
        md_file = self.workers_path / f"{memory.role_id}.mem.md"
        self._save_as_markdown(memory, md_file)
    
    def _save_as_markdown(self, memory: RoleMemory, path: Path):
        """保存为 Markdown 格式"""
        lines = [
            f"# 角色记忆: {memory.role_id}",
            "",
            f"- **完成任务**: {memory.total_tasks}",
            f"- **平均评分**: {memory.avg_score:.1f}",
            f"- **最后更新**: {memory.last_updated}",
            "",
            "## 经验记录",
            ""
        ]
        
        for exp in sorted(memory.experiences, key=lambda x: x.timestamp, reverse=True)[:50]:
            lines.append(f"### {exp.timestamp}")
            lines.append(f"- **类型**: {exp.experience_type}")
            lines.append(f"- **内容**: {exp.content}")
            lines.append(f"- **价值**: {exp.value_score:.1f}")
            lines.append("")
        
        if memory.patterns:
            lines.append("## 已识别模式")
            lines.append("")
            for p in memory.patterns:
                lines.append(f"- {p.get('description', '')}")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    
    def _update_patterns(self, memory: RoleMemory):
        """更新模式识别"""
        # 简化实现：统计经验类型
        type_counts = {}
        for exp in memory.experiences:
            t = exp.experience_type
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # 识别高频模式
        for t, count in type_counts.items():
            if count >= 3:
                pattern = {
                    "type": t,
                    "count": count,
                    "description": f"频繁出现的{t}模式"
                }
                
                # 检查是否已存在
                exists = any(
                    p.get("type") == t for p in memory.patterns
                )
                if not exists:
                    memory.patterns.append(pattern)
    
    def _compress_memory(self, memory: RoleMemory, max_items: int = 100):
        """压缩记忆，保留高价值"""
        if len(memory.experiences) <= max_items:
            return
        
        # 按价值排序，保留前 max_items
        memory.experiences = sorted(
            memory.experiences,
            key=lambda x: x.value_score,
            reverse=True
        )[:max_items]

# ============================================================================
# 记忆队列（待归还）
# ============================================================================

class MemoryReturnQueue:
    """记忆归还队列"""
    
    def __init__(self, queue_path: str = "~/clawos/blackboard/roles/memory-queue.json"):
        self.queue_path = Path(queue_path).expanduser()
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
    
    def enqueue(self, task_result: Dict):
        """加入归还队列"""
        queue = self._load_queue()
        queue.append({
            "taskId": task_result.get("taskId"),
            "roleId": task_result.get("roleId"),
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        })
        self._save_queue(queue)
    
    def process_queue(self, manager: RoleMemoryManager) -> int:
        """处理队列中的所有待归还记忆"""
        queue = self._load_queue()
        processed = 0
        
        for item in queue:
            if item["status"] == "pending":
                # 这里需要从 blackboard 加载完整的 task_result
                # 简化实现
                item["status"] = "completed"
                processed += 1
        
        self._save_queue(queue)
        return processed
    
    def _load_queue(self) -> List[Dict]:
        if self.queue_path.exists():
            with open(self.queue_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_queue(self, queue: List[Dict]):
        with open(self.queue_path, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS 角色记忆管理")
    parser.add_argument("--role", help="角色ID")
    parser.add_argument("--summary", action="store_true", help="显示记忆摘要")
    parser.add_argument("--return", dest="return_mem", help="归还记忆（JSON文件）")
    parser.add_argument("--list", action="store_true", help="列出所有角色记忆")
    
    args = parser.parse_args()
    
    manager = RoleMemoryManager()
    
    if args.role and args.summary:
        summary = manager.get_role_memory_summary(args.role)
        print(summary)
    
    elif args.return_mem:
        with open(args.return_mem, 'r', encoding='utf-8') as f:
            task_result = json.load(f)
        success = manager.return_memory(task_result)
        print(f"记忆归还: {'成功' if success else '失败'}")
    
    elif args.list:
        for mem_file in manager.workers_path.glob("*.mem.md"):
            print(f"  {mem_file.stem}")
    
    else:
        parser.print_help()
