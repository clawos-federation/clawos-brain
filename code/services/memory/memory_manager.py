#!/usr/bin/env python3
"""Memory Manager - Coordinate L1-L4 memory layers

This module provides a unified interface to the 4-layer memory system:
- L1: Session memory (RAM-like, fast access)
- L2: Task history (SQLite, persistent)
- L3: Vector memory (experiences, searchable)
- L4: GitHub sync (cross-machine backup)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import uuid

from .l1_session import L1SessionMemory
from .l2_history import L2TaskHistory
from .l3_vector import L3VectorMemory
from .l4_github import L4GitHubMemory


class MemoryManager:
    """Unified memory manager coordinating all 4 layers.

    Usage:
        manager = MemoryManager("session-123")

        # Store task result across layers
        manager.store_task_result(
            {"id": "task-1", "agent_id": "gm", "description": "Test task"},
            {"status": "completed", "output": "Done"}
        )

        # Retrieve context
        history = manager.get_agent_history("gm")
        experiences = manager.retrieve_experiences("gm", ["task", "completed"])
    """

    def __init__(
        self,
        session_id: str,
        l2_path: Optional[Path] = None,
        l3_path: Optional[Path] = None,
        l4_path: Optional[Path] = None,
    ):
        """Initialize memory manager.

        Args:
            session_id: Unique session identifier
            l2_path: Optional custom L2 database path
            l3_path: Optional custom L3 storage path
            l4_path: Optional custom L4 repository path
        """
        self.session_id = session_id

        # Initialize all layers
        self.l1 = L1SessionMemory(session_id)
        self.l2 = L2TaskHistory(l2_path)
        self.l3 = L3VectorMemory(l3_path)
        self.l4 = L4GitHubMemory(l4_path)

    # === L1 Session Operations ===

    def set_context(
        self, key: str, value: Any, metadata: Optional[Dict] = None
    ) -> bool:
        """Store value in session context (L1).

        Args:
            key: Key to store under
            value: Value to store
            metadata: Optional metadata

        Returns:
            True if stored successfully
        """
        return self.l1.store(key, value, metadata)

    def get_context(self, key: str) -> Optional[Any]:
        """Retrieve value from session context (L1).

        Args:
            key: Key to retrieve

        Returns:
            Stored value or None
        """
        return self.l1.retrieve(key)

    def clear_session(self) -> None:
        """Clear session context (L1 only)."""
        self.l1.clear()

    # === L2 History Operations ===

    def record_task(self, task: Dict[str, Any]) -> None:
        """Record task in history (L2).

        Args:
            task: Task dict with id, agent_id, type, etc.
        """
        self.l2.record_task(task)

    def record_decision(
        self,
        task_id: str,
        agent_id: str,
        decision: str,
        reasoning: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> None:
        """Record a decision in history (L2).

        Args:
            task_id: Associated task ID
            agent_id: Agent making the decision
            decision: The decision made
            reasoning: Optional reasoning
            outcome: Optional outcome
        """
        decision_id = str(uuid.uuid4())
        self.l2.record_decision(
            {
                "id": decision_id,
                "task_id": task_id,
                "agent_id": agent_id,
                "decision": decision,
                "reasoning": reasoning,
                "outcome": outcome,
            }
        )

    def get_task_history(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get specific task from history (L2).

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task dict or None
        """
        return self.l2.get_task(task_id)

    def get_agent_history(
        self, agent_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get task history for an agent (L2).

        Args:
            agent_id: Agent ID
            limit: Maximum results

        Returns:
            List of task dicts
        """
        return self.l2.get_agent_history(agent_id, limit)

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an agent (L2).

        Args:
            agent_id: Agent ID

        Returns:
            Stats dict or None
        """
        return self.l2.get_agent_stats(agent_id)

    # === L3 Vector Operations ===

    def store_experience(
        self,
        agent_id: str,
        experience: str,
        experience_type: str = "general",
        metadata: Optional[Dict] = None,
        score: Optional[float] = None,
    ) -> str:
        """Store an experience (L3).

        Args:
            agent_id: Agent ID
            experience: Experience description
            experience_type: Type of experience
            metadata: Optional metadata
            score: Optional utility score

        Returns:
            Experience ID
        """
        return self.l3.store_experience(
            agent_id, experience, experience_type, metadata, score
        )

    def retrieve_experiences(
        self, agent_id: str, keywords: Optional[List[str]] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve experiences (L3).

        Args:
            agent_id: Agent ID
            keywords: Optional keywords to search
            limit: Maximum results

        Returns:
            List of experience dicts
        """
        if keywords:
            return self.l3.search_by_keywords(keywords, limit, agent_id)
        else:
            return self.l3.retrieve_recent(agent_id, limit)

    # === L4 GitHub Operations ===

    def export_to_github(self, data_type: str, data: Any) -> str:
        """Export data to GitHub memory (L4).

        Args:
            data_type: Type of data (experiences, session, lessons, agent)
            data: Data to export

        Returns:
            Path to created file
        """
        if data_type == "experiences":
            return self.l4.export_experiences(data)
        elif data_type == "session":
            return self.l4.export_session_archive(
                data.get("session_id", self.session_id), data
            )
        elif data_type == "lessons":
            return self.l4.export_lessons_learned(data)
        elif data_type == "agent":
            return self.l4.export_agent_summary(data.get("agent_id", "unknown"), data)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def sync_to_github(self, message: Optional[str] = None) -> Dict[str, Any]:
        """Sync memory to GitHub (L4).

        Args:
            message: Optional commit message

        Returns:
            Sync result dict
        """
        return self.l4.sync(message)

    # === Unified Operations ===

    def store_task_result(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        experience_type: str = "task",
    ) -> Dict[str, Any]:
        """Store task result across all layers.

        This is the main entry point for storing task results.
        It stores in L1 (session), L2 (history), and L3 (experience).

        Args:
            task: Task dict with id, agent_id, description
            result: Result dict with status, output, etc.
            experience_type: Type for L3 storage

        Returns:
            Dict with storage results
        """
        results = {"task_id": task.get("id"), "timestamp": datetime.now().isoformat()}

        # L1: Store in session context
        self.l1.store(task["id"], result)
        results["l1"] = True

        # L2: Record in task history
        task_record = {
            **task,
            "result": result,
            "status": result.get("status"),
            "completed": datetime.now().isoformat(),
        }
        if result.get("score"):
            task_record["score"] = result["score"]
        self.l2.record_task(task_record)
        results["l2"] = True

        # L3: Store as experience
        experience = self._format_experience(task, result)
        exp_id = self.l3.store_experience(
            agent_id=task.get("agent_id", "unknown"),
            experience=experience,
            experience_type=experience_type,
            score=result.get("score"),
        )
        results["l3"] = exp_id

        return results

    def _format_experience(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Format task result as experience string."""
        parts = [
            f"Task: {task.get('description', task.get('id', 'unknown'))}",
            f"Agent: {task.get('agent_id', 'unknown')}",
            f"Status: {result.get('status', 'unknown')}",
        ]

        if result.get("output"):
            output = str(result["output"])
            parts.append(f"Result: {output[:200]}")

        if result.get("summary"):
            parts.append(f"Summary: {result['summary']}")

        return " | ".join(parts)

    def get_full_context(
        self,
        agent_id: str,
        include_history: bool = True,
        include_experiences: bool = True,
        history_limit: int = 20,
        experience_limit: int = 10,
    ) -> Dict[str, Any]:
        """Get full context for an agent from all layers.

        Args:
            agent_id: Agent ID
            include_history: Include L2 history
            include_experiences: Include L3 experiences
            history_limit: Max history items
            experience_limit: Max experience items

        Returns:
            Combined context dict
        """
        context = {
            "session_id": self.session_id,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
        }

        # L2: Get history
        if include_history:
            context["history"] = self.l2.get_agent_history(agent_id, history_limit)
            context["stats"] = self.l2.get_agent_stats(agent_id)

        # L3: Get experiences
        if include_experiences:
            context["experiences"] = self.l3.retrieve_recent(agent_id, experience_limit)

        return context

    def archive_session(self) -> Dict[str, Any]:
        """Archive current session to L4.

        Returns:
            Archive result dict
        """
        # Export session data
        session_data = self.l1.export()

        # Get recent history
        recent_tasks = self.l2.get_recent_tasks(100)

        archive_data = {**session_data, "recent_tasks": recent_tasks}

        # Export to GitHub
        file_path = self.l4.export_session_archive(self.session_id, archive_data)

        return {
            "success": True,
            "file_path": file_path,
            "task_count": len(recent_tasks),
            "context_keys": len(session_data.get("context", {})),
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics from all layers.

        Returns:
            Combined stats dict
        """
        return {
            "session_id": self.session_id,
            "l1": {"keys": len(self.l1), "size_estimate": self.l1.size_estimate()},
            "l2": {"db_size": self.l2.get_db_size()},
            "l3": self.l3.get_stats(),
            "l4": self.l4.get_status(),
        }
