#!/usr/bin/env python3
"""
ClawOS 分层记忆系统
实现 L1(短期) → L2(中期) → L3(长期) → L4(程序) 四层记忆架构
"""

import json
import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

# ============================================================================
# 记忆类型
# ============================================================================

@dataclass
class MemoryEntry:
    id: str
    content: str
    memory_type: str  # experience, document, knowledge, task
    importance: float  # 0.0 - 1.0
    source: str
    timestamp: str
    metadata: Dict[str, Any]
    access_count: int = 0
    
    def to_dict(self):
        return asdict(self)

# ============================================================================
# L1: 短期记忆 (内存)
# ============================================================================

class ShortTermMemory:
    """短期记忆 - 会话期间的临时存储"""
    
    def __init__(self, session_id: str, max_items: int = 100):
        self.session_id = session_id
        self.max_items = max_items
        self.context: List[Dict] = []
        self.working_memory: Dict[str, Any] = {}
        self.created_at = datetime.now()
    
    def add_context(self, item: Dict):
        """添加上下文项"""
        self.context.append({
            **item,
            "timestamp": datetime.now().isoformat()
        })
        
        # FIFO 淘汰
        if len(self.context) > self.max_items:
            self.context.pop(0)
    
    def get_context(self, limit: Optional[int] = None) -> List[Dict]:
        """获取上下文"""
        if limit:
            return self.context[-limit:]
        return self.context.copy()
    
    def set_working(self, key: str, value: Any):
        """设置工作记忆"""
        self.working_memory[key] = value
    
    def get_working(self, key: str, default=None) -> Any:
        """获取工作记忆"""
        return self.working_memory.get(key, default)
    
    def clear(self):
        """清空短期记忆"""
        self.context.clear()
        self.working_memory.clear()
    
    def summarize(self) -> Dict:
        """生成摘要"""
        return {
            "session_id": self.session_id,
            "context_count": len(self.context),
            "working_keys": list(self.working_memory.keys()),
            "age_minutes": (datetime.now() - self.created_at).seconds / 60
        }

# ============================================================================
# L2: 中期记忆 (SQLite)
# ============================================================================

class MediumTermMemory:
    """中期记忆 - 持久化结构化存储"""
    
    def __init__(self, db_path: str = "~/clawos/memory/medium.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 任务历史
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    description TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    metadata TEXT
                )
            """)
            
            # 会话摘要
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_summaries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    date DATE,
                    summary TEXT,
                    key_points TEXT,
                    created_at TIMESTAMP
                )
            """)
            
            # 一般记忆
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    memory_type TEXT,
                    importance REAL,
                    source TEXT,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_type ON task_history(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON task_history(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_importance ON memories(importance)")
            
            conn.commit()
    
    def record_task(self, task_id: str, task_type: str, description: str,
                    status: str = "pending", result: Any = None, metadata: dict = None):
        """记录任务"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_history
                (id, type, description, status, created_at, completed_at, result, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, task_type, description, status,
                now, now if status == "completed" else None,
                json.dumps(result) if result else None,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def update_task(self, task_id: str, status: str, result: Any = None):
        """更新任务状态"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE task_history
                SET status = ?, completed_at = ?, result = ?
                WHERE id = ?
            """, (
                status, now,
                json.dumps(result) if result else None,
                task_id
            ))
            conn.commit()
    
    def get_recent_tasks(self, limit: int = 100, task_type: str = None) -> List[dict]:
        """获取最近的任务"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if task_type:
                rows = conn.execute("""
                    SELECT * FROM task_history
                    WHERE type = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (task_type, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM task_history
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,)).fetchall()
            
            return [dict(row) for row in rows]
    
    def store_memory(self, entry: MemoryEntry):
        """存储记忆"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories
                (id, content, memory_type, importance, source, created_at, 
                 last_accessed, access_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id, entry.content, entry.memory_type, entry.importance,
                entry.source, entry.timestamp, entry.timestamp,
                entry.access_count, json.dumps(entry.metadata)
            ))
            conn.commit()
    
    def search_memories(self, query: str, memory_type: str = None, 
                        limit: int = 10) -> List[MemoryEntry]:
        """搜索记忆 (简单文本匹配)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            search_pattern = f"%{query}%"
            
            if memory_type:
                rows = conn.execute("""
                    SELECT * FROM memories
                    WHERE content LIKE ? AND memory_type = ?
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                """, (search_pattern, memory_type, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM memories
                    WHERE content LIKE ?
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                """, (search_pattern, limit)).fetchall()
            
            results = []
            for row in rows:
                # 更新访问计数
                conn.execute("""
                    UPDATE memories
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), row["id"]))
                
                results.append(MemoryEntry(
                    id=row["id"],
                    content=row["content"],
                    memory_type=row["memory_type"],
                    importance=row["importance"],
                    source=row["source"],
                    timestamp=row["created_at"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    access_count=row["access_count"] + 1
                ))
            
            conn.commit()
            return results
    
    def save_session_summary(self, session_id: str, summary: str, key_points: List[str]):
        """保存会话摘要"""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO session_summaries
                (id, session_id, date, summary, key_points, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                hashlib.md5(session_id.encode()).hexdigest()[:12],
                session_id, now.date().isoformat(), summary,
                json.dumps(key_points), now.isoformat()
            ))
            conn.commit()
    
    def compress(self, days_old: int = 30):
        """压缩旧数据"""
        cutoff = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # 删除旧的已处理任务
            conn.execute("""
                DELETE FROM task_history
                WHERE status = 'completed' AND completed_at < ?
            """, (cutoff,))
            
            # 删除不重要的旧记忆
            conn.execute("""
                DELETE FROM memories
                WHERE importance < 0.3 AND created_at < ?
            """, (cutoff,))
            
            deleted = conn.total_changes
            conn.commit()
        
        return deleted

# ============================================================================
# L3: 长期记忆 (向量存储 - 简化版)
# ============================================================================

class LongTermMemory:
    """长期记忆 - 语义搜索存储"""
    
    def __init__(self, storage_path: str = "~/clawos/memory/longterm"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_path / "index.json"
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {"memories": [], "updated": None}
    
    def _save_index(self):
        """保存索引"""
        self.index["updated"] = datetime.now().isoformat()
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def store(self, entry: MemoryEntry, embedding: List[float] = None):
        """存储长期记忆"""
        # 保存记忆内容
        memory_file = self.storage_path / f"{entry.id}.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump({
                "entry": entry.to_dict(),
                "embedding": embedding
            }, f, indent=2, ensure_ascii=False)
        
        # 更新索引
        self.index["memories"].append({
            "id": entry.id,
            "type": entry.memory_type,
            "importance": entry.importance,
            "timestamp": entry.timestamp,
            "has_embedding": embedding is not None
        })
        self._save_index()
    
    def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[MemoryEntry]:
        """关键词搜索 (简化版，实际应使用向量搜索)"""
        results = []
        
        for mem_meta in self.index["memories"]:
            memory_file = self.storage_path / f"{mem_meta['id']}.json"
            if not memory_file.exists():
                continue
            
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = data["entry"]["content"].lower()
                
                # 简单关键词匹配
                score = sum(1 for kw in keywords if kw.lower() in content)
                if score > 0:
                    results.append({
                        "entry": MemoryEntry(**data["entry"]),
                        "score": score
                    })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["entry"] for r in results[:limit]]
    
    def get_by_type(self, memory_type: str, limit: int = 20) -> List[MemoryEntry]:
        """按类型获取记忆"""
        results = []
        
        for mem_meta in self.index["memories"]:
            if mem_meta["type"] == memory_type:
                memory_file = self.storage_path / f"{mem_meta['id']}.json"
                if memory_file.exists():
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results.append(MemoryEntry(**data["entry"]))
                        
                        if len(results) >= limit:
                            break
        
        return results

# ============================================================================
# L4: 程序记忆 (技能/工作流)
# ============================================================================

class ProceduralMemory:
    """程序记忆 - 技能和工作流"""
    
    def __init__(self, skills_path: str = "~/openclaw/skills",
                 workflows_path: str = "~/clawos/workflows"):
        self.skills_path = Path(skills_path).expanduser()
        self.workflows_path = Path(workflows_path).expanduser()
        self._cache: Dict[str, Any] = {}
    
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """获取技能"""
        if skill_name in self._cache:
            return self._cache[skill_name]
        
        skill_path = self.skills_path / skill_name / "SKILL.md"
        if not skill_path.exists():
            return None
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[skill_name] = {
            "name": skill_name,
            "path": str(skill_path),
            "content": content
        }
        
        return self._cache[skill_name]
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict]:
        """获取工作流"""
        if workflow_name in self._cache:
            return self._cache[workflow_name]
        
        workflow_path = self.workflows_path / f"{workflow_name}.yaml"
        if not workflow_path.exists():
            workflow_path = self.workflows_path / f"{workflow_name}.json"
        
        if not workflow_path.exists():
            return None
        
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[workflow_name] = {
            "name": workflow_name,
            "path": str(workflow_path),
            "content": content
        }
        
        return self._cache[workflow_name]
    
    def list_skills(self) -> List[str]:
        """列出所有可用技能"""
        if not self.skills_path.exists():
            return []
        
        return [d.name for d in self.skills_path.iterdir() 
                if d.is_dir() and (d / "SKILL.md").exists()]
    
    def list_workflows(self) -> List[str]:
        """列出所有可用工作流"""
        if not self.workflows_path.exists():
            return []
        
        return [f.stem for f in self.workflows_path.iterdir() 
                if f.suffix in [".yaml", ".json"]]

# ============================================================================
# 分层记忆管理器
# ============================================================================

class HierarchicalMemory:
    """分层记忆管理器 - 统一管理四层记忆"""
    
    def __init__(self, session_id: str):
        self.l1 = ShortTermMemory(session_id)
        self.l2 = MediumTermMemory()
        self.l3 = LongTermMemory()
        self.l4 = ProceduralMemory()
    
    def remember(self, content: str, memory_type: str = "knowledge",
                 importance: float = 0.5, source: str = "user"):
        """存储记忆 - 自动路由到合适的层级"""
        entry = MemoryEntry(
            id=hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:12],
            content=content,
            memory_type=memory_type,
            importance=importance,
            source=source,
            timestamp=datetime.now().isoformat(),
            metadata={}
        )
        
        # 总是存入 L1
        self.l1.add_context({
            "type": "memory",
            "entry_id": entry.id,
            "content": content[:200]  # 截断
        })
        
        # 根据重要性决定存储层级
        if importance >= 0.3:
            self.l2.store_memory(entry)
        
        if importance >= 0.7:
            self.l3.store(entry)
    
    def recall(self, query: str, limit: int = 10) -> List[Dict]:
        """检索记忆 - 从各层汇总"""
        results = []
        
        # 1. 检查 L1 上下文
        context = self.l1.get_context(limit=3)
        for item in context:
            if query.lower() in str(item).lower():
                results.append({
                    "source": "L1",
                    "content": item,
                    "relevance": 1.0
                })
        
        # 2. 搜索 L2
        l2_results = self.l2.search_memories(query, limit=5)
        for entry in l2_results:
            results.append({
                "source": "L2",
                "content": entry.to_dict(),
                "relevance": 0.8
            })
        
        # 3. 搜索 L3
        keywords = query.split()
        l3_results = self.l3.search_by_keywords(keywords, limit=5)
        for entry in l3_results:
            results.append({
                "source": "L3",
                "content": entry.to_dict(),
                "relevance": 0.6
            })
        
        # 按相关性排序
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
    
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """获取技能 (L4)"""
        return self.l4.get_skill(skill_name)
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict]:
        """获取工作流 (L4)"""
        return self.l4.get_workflow(workflow_name)
    
    def record_task(self, task_id: str, task_type: str, description: str):
        """记录任务"""
        self.l1.set_working("current_task", task_id)
        self.l2.record_task(task_id, task_type, description)
    
    def complete_task(self, task_id: str, result: Any):
        """完成任务"""
        self.l2.update_task(task_id, "completed", result)
    
    def compress(self):
        """压缩各层记忆"""
        # L1 压缩
        if len(self.l1.context) > 50:
            # 保留最近的 30 条
            self.l1.context = self.l1.context[-30:]
        
        # L2 压缩
        deleted = self.l2.compress(days_old=30)
        
        return {"l2_deleted": deleted}


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawOS Memory System")
    parser.add_argument("--remember", help="Store a memory")
    parser.add_argument("--recall", help="Recall memories")
    parser.add_argument("--type", default="knowledge", help="Memory type")
    parser.add_argument("--importance", type=float, default=0.5, help="Importance 0-1")
    parser.add_argument("--session", default="cli", help="Session ID")
    parser.add_argument("--compress", action="store_true", help="Compress old memories")
    parser.add_argument("--stats", action="store_true", help="Show memory stats")
    
    args = parser.parse_args()
    
    memory = HierarchicalMemory(args.session)
    
    if args.remember:
        memory.remember(args.remember, args.type, args.importance)
        print(f"Stored: {args.remember[:50]}...")
    
    elif args.recall:
        results = memory.recall(args.recall)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.compress:
        stats = memory.compress()
        print(f"Compressed: {stats}")
    
    elif args.stats:
        print("L1:", memory.l1.summarize())
        print("L4 Skills:", memory.l4.list_skills()[:5])
        print("L4 Workflows:", memory.l4.list_workflows())
    
    else:
        parser.print_help()
