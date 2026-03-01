#!/usr/bin/env python3
"""
ClawOS Memory System - 4-Layer Memory Architecture

This package provides a unified memory system with 4 layers:
- L1: Session Memory (RAM-like, fast access, session-scoped)
- L2: Task History (SQLite, persistent task and decision records)
- L3: Vector Memory (experiences, searchable, learning-oriented)
- L4: GitHub Sync (cross-machine backup and sync)

Usage:
    from clawos.services.memory import MemoryManager

    # Initialize with session ID
    manager = MemoryManager("session-123")

    # Store task result across all layers
    manager.store_task_result(
        {"id": "task-1", "agent_id": "gm", "description": "Test task"},
        {"status": "completed", "output": "Done"}
    )

    # Get agent context
    context = manager.get_full_context("gm")
"""

from .l1_session import L1SessionMemory
from .l2_history import L2TaskHistory
from .l3_vector import L3VectorMemory
from .l4_github import L4GitHubMemory
from .memory_manager import MemoryManager

__all__ = [
    "L1SessionMemory",
    "L2TaskHistory",
    "L3VectorMemory",
    "L4GitHubMemory",
    "MemoryManager",
]

__version__ = "1.0.0"
