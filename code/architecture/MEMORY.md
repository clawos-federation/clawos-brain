# MEMORY-ARCHITECTURE.md - ClawOS 分层记忆架构

**版本**: 1.0.0
**更新时间**: 2026-02-25
**状态**: ✅ 已定义

---

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   L4: 程序记忆                          │
│            (Procedural Memory - Skills)                │
│              持久化 | 只读 | 共享                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                   L3: 长期记忆                          │
│           (Long-term Memory - 向量库)                   │
│          持久化 | 语义搜索 | 10GB+                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                   L2: 中期记忆                          │
│          (Medium-term Memory - 数据库)                  │
│          持久化 | 结构化查询 | 1GB                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                   L1: 短期记忆                          │
│           (Short-term Memory - 内存)                    │
│          易失 | 快速访问 | 100MB                        │
└─────────────────────────────────────────────────────────┘
```

---

## 四层记忆详解

### L1: 短期记忆 (Short-term Memory)

**存储**: 内存 (RAM)
**容量**: ~100MB
**生命周期**: 会话期间

**用途**:
- 当前对话上下文
- 正在处理的任务数据
- 临时计算结果

**数据结构**:
```json
{
  "sessionId": "session-uuid",
  "createdAt": "2026-02-25T18:50:00+08:00",
  "ttl": 3600,
  "data": {
    "currentTask": {...},
    "context": [...],
    "workingMemory": {...}
  }
}
```

**操作**:
| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 读 | O(1) | 直接内存访问 |
| 写 | O(1) | 直接内存写入 |
| 清理 | O(n) | TTL 过期清理 |

**实现**:
```python
class ShortTermMemory:
    def __init__(self, session_id):
        self.session_id = session_id
        self.data = {}
        self.context = []
        self.max_context = 100  # 最大上下文条目

    def add_context(self, item):
        self.context.append(item)
        if len(self.context) > self.max_context:
            self.context.pop(0)  # FIFO

    def get_context(self, limit=None):
        if limit:
            return self.context[-limit:]
        return self.context
```

---

### L2: 中期记忆 (Medium-term Memory)

**存储**: SQLite / 文件系统
**容量**: ~1GB
**生命周期**: 数天到数周

**用途**:
- 任务历史记录
- 会话摘要
- 用户偏好
- 临时学习结果

**数据结构**:
```sql
-- 任务历史
CREATE TABLE task_history (
    id TEXT PRIMARY KEY,
    type TEXT,
    description TEXT,
    status TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    metadata JSON
);

-- 会话摘要
CREATE TABLE session_summaries (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    date DATE,
    summary TEXT,
    key_points JSON,
    embeddings BLOB
);

-- 用户偏好
CREATE TABLE user_preferences (
    key TEXT PRIMARY KEY,
    value JSON,
    updated_at TIMESTAMP,
    confidence REAL
);
```

**操作**:
| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 查询 | O(log n) | 索引查询 |
| 插入 | O(1) | 追加写入 |
| 压缩 | O(n) | 定期压缩 |

**实现**:
```python
class MediumTermMemory:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        self._init_tables()

    def record_task(self, task_id, task_type, description, result):
        self.db.execute("""
            INSERT INTO task_history
            VALUES (?, ?, ?, 'completed', ?, ?, ?, ?)
        """, (task_id, task_type, description, now(), now(),
              json.dumps(result), "{}"))

    def get_recent_tasks(self, limit=100):
        return self.db.execute("""
            SELECT * FROM task_history
            ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()

    def compress(self):
        """压缩旧数据"""
        # 合并相似任务
        # 删除过期数据
        # 更新索引
        pass
```

---

### L3: 长期记忆 (Long-term Memory)

**存储**: 向量数据库 (Chroma/Milvus/Pinecone)
**容量**: 10GB+
**生命周期**: 永久

**用途**:
- 语义知识存储
- 经验积累
- 文档索引
- 跨会话记忆

**数据结构**:
```json
{
  "id": "mem-uuid",
  "embedding": [0.1, 0.2, ...],  // 768维向量
  "content": "记忆内容",
  "metadata": {
    "type": "experience|document|knowledge",
    "source": "来源",
    "timestamp": "2026-02-25T18:50:00+08:00",
    "importance": 0.85,
    "access_count": 10
  }
}
```

**操作**:
| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 语义搜索 | O(log n) | 向量相似度 |
| 插入 | O(1) | 向量索引 |
| 删除 | O(log n) | 索引更新 |

**实现**:
```python
class LongTermMemory:
    def __init__(self, collection_name):
        self.collection = chromadb.Client().get_collection(collection_name)
        self.embedder = SentenceTransformer('all-mpnet-base-v2')

    def store(self, content, metadata=None):
        embedding = self.embedder.encode(content)
        self.collection.add(
            ids=[str(uuid4())],
            embeddings=[embedding.tolist()],
            documents=[content],
            metadatas=[metadata or {}]
        )

    def search(self, query, top_k=10):
        query_embedding = self.embedder.encode(query)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        return results

    def search_by_type(self, query, memory_type, top_k=10):
        results = self.search(query, top_k * 2)
        return [r for r in results if r["metadata"]["type"] == memory_type][:top_k]
```

---

### L4: 程序记忆 (Procedural Memory)

**存储**: 文件系统 (Skills)
**容量**: 无限
**生命周期**: 永久

**用途**:
- 技能和知识
- 工作流程
- 最佳实践
- Agent 定义

**数据结构**:
```
~/openclaw/skills/
├── skill-name/
│   ├── SKILL.md        # 技能说明
│   ├── scripts/        # 执行脚本
│   └── templates/      # 模板文件

~/clawos/workflows/
├── simple-task.yaml    # 工作流定义
├── coding-task.yaml
└── research-task.yaml
```

**操作**:
| 操作 | 说明 |
|------|------|
| 加载 | 启动时加载到内存 |
| 查询 | 通过 Skill 系统查询 |
| 更新 | 通过 ClawHub 更新 |

**实现**:
```python
class ProceduralMemory:
    def __init__(self, skills_path, workflows_path):
        self.skills = self._load_skills(skills_path)
        self.workflows = self._load_workflows(workflows_path)

    def get_skill(self, skill_name):
        return self.skills.get(skill_name)

    def get_workflow(self, workflow_name):
        return self.workflows.get(workflow_name)

    def list_available_skills(self):
        return list(self.skills.keys())
```

---

## 记忆流转

### 写入流程

```
输入 → L1 缓存
    ↓
重要? → L2 持久化
    ↓
长期价值? → L3 向量化
    ↓
可复用? → L4 程序化
```

**分类标准**:
| 重要性 | 存储层 | 保留时间 |
|--------|--------|----------|
| 临时 | L1 | 会话期间 |
| 普通 | L2 | 7-30 天 |
| 重要 | L2 + L3 | 永久 |
| 核心技能 | L4 | 永久 + 版本控制 |

### 读取流程

```
查询 → L1 命中? → 返回
         ↓ 未命中
      L2 命中? → 返回 + 缓存到 L1
         ↓ 未命中
      L3 语义搜索 → 返回 + 缓存到 L1/L2
         ↓ 未命中
      L4 技能查询 → 返回
```

---

## 压缩策略

### L1 压缩

```python
def compress_l1():
    """压缩短期记忆"""
    # 滑动窗口
    if len(context) > max_context:
        context = context[-max_context:]

    # 摘要压缩
    if token_count(context) > max_tokens:
        summary = summarize(context[:-keep_recent])
        context = [summary] + context[-keep_recent:]
```

### L2 压缩

```python
def compress_l2():
    """压缩中期记忆"""
    # 删除过期数据
    delete_expired()

    # 合并相似记录
    merge_similar_tasks()

    # 提取摘要
    old_sessions = get_sessions_older_than(30)
    for session in old_sessions:
        summary = summarize_session(session)
        store_summary(summary)
        delete_session(session.id)
```

### L3 优化

```python
def optimize_l3():
    """优化长期记忆"""
    # 重建索引
    rebuild_index()

    # 合并重复
    deduplicate()

    # 更新重要性评分
    recalculate_importance()
```

---

## 容量规划

| 层级 | 当前容量 | 目标容量 | 增长策略 |
|------|----------|----------|----------|
| L1 | 10MB | 100MB | 按需扩展 |
| L2 | 100MB | 1GB | 定期压缩 |
| L3 | 1GB | 10GB+ | 分布式存储 |
| L4 | 无限 | 无限 | 版本控制 |

---

## 监控指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| L1 命中率 | 短期记忆命中率 | > 80% |
| L2 命中率 | 中期记忆命中率 | > 60% |
| L3 检索延迟 | 语义搜索延迟 | < 100ms |
| 压缩效率 | 压缩后大小/原大小 | < 30% |

---

## 实现示例

```python
class HierarchicalMemory:
    def __init__(self):
        self.l1 = ShortTermMemory(session_id=get_current_session())
        self.l2 = MediumTermMemory(db_path="~/clawos/memory/medium.db")
        self.l3 = LongTermMemory(collection="clawos-memories")
        self.l4 = ProceduralMemory(
            skills_path="~/openclaw/skills",
            workflows_path="~/clawos/workflows"
        )

    def remember(self, content, importance=0.5):
        """存储记忆"""
        # 总是存入 L1
        self.l1.add_context(content)

        # 根据重要性决定存储层级
        if importance > 0.3:
            self.l2.record(content)

        if importance > 0.7:
            self.l3.store(content, {"importance": importance})

    def recall(self, query, top_k=10):
        """检索记忆"""
        results = []

        # 1. 检查 L1
        l1_results = self.l1.search(query)
        results.extend(l1_results)

        # 2. 查询 L2
        if len(results) < top_k:
            l2_results = self.l2.query(query, limit=top_k - len(results))
            results.extend(l2_results)

        # 3. 语义搜索 L3
        if len(results) < top_k:
            l3_results = self.l3.search(query, top_k=top_k - len(results))
            results.extend(l3_results)

        return results[:top_k]

    def compress(self):
        """执行压缩"""
        self.l1.compress()
        self.l2.compress()
        self.l3.optimize()
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-25 | 初始版本，定义四层记忆架构 |

---

**ClawOS 2026.3 - Hierarchical Memory Architecture**
