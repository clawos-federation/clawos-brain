#!/usr/bin/env python3
"""L2 Task History - SQLite-based task history (~1GB)

This layer provides persistent storage for task history and decisions.
Uses SQLite for efficient querying and indexing.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager


class L2TaskHistory:
    """Task history - SQLite-based persistent storage.

    Capacity: ~1GB
    Purpose: Long-term task and decision history
    Persistence: SQLite database file
    """

    DEFAULT_DB_PATH = Path.home() / "clawos/memory/l2/history.db"

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize task history.

        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    type TEXT,
                    description TEXT,
                    status TEXT,
                    score REAL,
                    created TEXT NOT NULL,
                    completed TEXT,
                    result TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    task_id TEXT,
                    agent_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reasoning TEXT,
                    outcome TEXT,
                    created TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );
                
                CREATE TABLE IF NOT EXISTS agent_stats (
                    agent_id TEXT PRIMARY KEY,
                    total_tasks INTEGER DEFAULT 0,
                    successful_tasks INTEGER DEFAULT 0,
                    avg_score REAL DEFAULT 0,
                    last_activity TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type);
                CREATE INDEX IF NOT EXISTS idx_decisions_agent ON decisions(agent_id);
                CREATE INDEX IF NOT EXISTS idx_decisions_task ON decisions(task_id);
            """)
            conn.commit()

    def record_task(self, task: Dict[str, Any]) -> None:
        """Record a task in history.

        Args:
            task: Task dict with id, agent_id, type, description, status, etc.
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks 
                (id, agent_id, type, description, status, score, created, completed, result, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task["id"],
                    task.get("agent_id"),
                    task.get("type"),
                    task.get("description"),
                    task.get("status"),
                    task.get("score"),
                    task.get("created", datetime.now().isoformat()),
                    task.get("completed"),
                    json.dumps(task.get("result")) if task.get("result") else None,
                    json.dumps(task.get("metadata")) if task.get("metadata") else None,
                ),
            )

            # Update agent stats
            self._update_agent_stats(conn, task.get("agent_id"), task.get("status"))
            conn.commit()

    def _update_agent_stats(
        self, conn: sqlite3.Connection, agent_id: str, status: Optional[str]
    ):
        """Update agent statistics."""
        if not agent_id:
            return

        # Get current stats
        row = conn.execute(
            "SELECT * FROM agent_stats WHERE agent_id = ?", (agent_id,)
        ).fetchone()

        if row:
            total = row["total_tasks"] + 1
            successful = row["successful_tasks"] + (1 if status == "completed" else 0)

            # Calculate new average score
            score_row = conn.execute(
                "SELECT AVG(score) as avg FROM tasks WHERE agent_id = ? AND score IS NOT NULL",
                (agent_id,),
            ).fetchone()
            avg_score = score_row["avg"] if score_row["avg"] is not None else 0

            conn.execute(
                """
                UPDATE agent_stats 
                SET total_tasks = ?, successful_tasks = ?, avg_score = ?, last_activity = ?
                WHERE agent_id = ?
            """,
                (total, successful, avg_score, datetime.now().isoformat(), agent_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO agent_stats (agent_id, total_tasks, successful_tasks, last_activity)
                VALUES (?, 1, ?, ?)
            """,
                (
                    agent_id,
                    1 if status == "completed" else 0,
                    datetime.now().isoformat(),
                ),
            )

    def record_decision(self, decision: Dict[str, Any]) -> None:
        """Record a decision in history.

        Args:
            decision: Decision dict with id, task_id, agent_id, decision, reasoning
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO decisions
                (id, task_id, agent_id, decision, reasoning, outcome, created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    decision["id"],
                    decision.get("task_id"),
                    decision.get("agent_id"),
                    decision.get("decision"),
                    decision.get("reasoning"),
                    decision.get("outcome"),
                    decision.get("created", datetime.now().isoformat()),
                ),
            )
            conn.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task dict or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            return self._row_to_dict(row) if row else None

    def get_agent_history(
        self, agent_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get task history for an agent.

        Args:
            agent_id: Agent ID to query
            limit: Maximum number of tasks to return

        Returns:
            List of task dicts
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks 
                WHERE agent_id = ? 
                ORDER BY created DESC 
                LIMIT ?
            """,
                (agent_id, limit),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_recent_tasks(
        self, limit: int = 50, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent tasks across all agents.

        Args:
            limit: Maximum number of tasks
            status: Optional status filter

        Returns:
            List of task dicts
        """
        with self._get_connection() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT * FROM tasks 
                    WHERE status = ?
                    ORDER BY created DESC 
                    LIMIT ?
                """,
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM tasks 
                    ORDER BY created DESC 
                    LIMIT ?
                """,
                    (limit,),
                ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an agent.

        Args:
            agent_id: Agent ID to query

        Returns:
            Stats dict or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agent_stats WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            return dict(row) if row else None

    def search_tasks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search tasks by description.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching tasks
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks 
                WHERE description LIKE ?
                ORDER BY created DESC 
                LIMIT ?
            """,
                (f"%{query}%", limit),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dict."""
        result = {
            "id": row["id"],
            "agent_id": row["agent_id"],
            "type": row["type"],
            "description": row["description"],
            "status": row["status"],
            "score": row["score"],
            "created": row["created"],
            "completed": row["completed"],
        }

        # Parse JSON fields
        if row["result"]:
            try:
                result["result"] = json.loads(row["result"])
            except json.JSONDecodeError:
                result["result"] = row["result"]

        if row["metadata"]:
            try:
                result["metadata"] = json.loads(row["metadata"])
            except json.JSONDecodeError:
                result["metadata"] = row["metadata"]

        return result

    def get_db_size(self) -> int:
        """Get database file size in bytes."""
        return self.db_path.stat().st_size if self.db_path.exists() else 0

    def vacuum(self) -> None:
        """Vacuum database to reclaim space."""
        with self._get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()
