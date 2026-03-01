#!/usr/bin/env python3
"""L1 Session Memory - RAM-based session context (~100MB)

This layer provides fast, in-memory storage for session context.
Data is lost when the session ends or the process terminates.
"""

from datetime import datetime
from typing import Any, Optional, Dict
import json


class L1SessionMemory:
    """Session memory - RAM-based, cleared on session end.

    Capacity: ~100MB
    Purpose: Fast access to current session context
    Persistence: None (RAM only)
    """

    MAX_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_KEYS = 10000  # Maximum number of keys

    def __init__(self, session_id: str):
        """Initialize session memory.

        Args:
            session_id: Unique identifier for this session
        """
        self.session_id = session_id
        self.context: Dict[str, Dict[str, Any]] = {}
        self.created = datetime.now()
        self._size_estimate = 0

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store a value in session context.

        Args:
            key: Key to store under
            value: Value to store
            metadata: Optional metadata to attach

        Returns:
            True if stored successfully, False if size limit exceeded
        """
        # Estimate size
        try:
            value_size = len(json.dumps(value))
        except (TypeError, ValueError):
            value_size = 1024  # Default estimate for non-serializable

        entry_size = value_size + len(key) * 2  # Rough estimate

        # Check size limits
        if self._size_estimate + entry_size > self.MAX_SIZE:
            return False
        if len(self.context) >= self.MAX_KEYS:
            # Remove oldest entry
            oldest_key = next(iter(self.context))
            self.delete(oldest_key)

        self.context[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self._size_estimate += entry_size
        return True

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from session context.

        Args:
            key: Key to retrieve

        Returns:
            The stored value or None if not found
        """
        entry = self.context.get(key)
        return entry.get("value") if entry else None

    def get_entry(self, key: str) -> Optional[Dict[str, Any]]:
        """Get full entry including timestamp and metadata.

        Args:
            key: Key to retrieve

        Returns:
            Full entry dict or None if not found
        """
        return self.context.get(key)

    def delete(self, key: str) -> bool:
        """Delete a key from context.

        Args:
            key: Key to delete

        Returns:
            True if deleted, False if not found
        """
        if key in self.context:
            entry = self.context[key]
            try:
                size = len(json.dumps(entry))
            except (TypeError, ValueError):
                size = 1024
            self._size_estimate -= size
            del self.context[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all session context."""
        self.context.clear()
        self._size_estimate = 0

    def keys(self) -> list:
        """Get all keys in context."""
        return list(self.context.keys())

    def size_estimate(self) -> int:
        """Get estimated size in bytes."""
        return self._size_estimate

    def export(self) -> dict:
        """Export session for persistence or transfer.

        Returns:
            Dict with session data
        """
        return {
            "sessionId": self.session_id,
            "created": self.created.isoformat(),
            "context": self.context,
            "sizeEstimate": self._size_estimate,
        }

    @classmethod
    def from_export(cls, data: dict) -> "L1SessionMemory":
        """Restore session from export.

        Args:
            data: Exported session data

        Returns:
            Restored L1SessionMemory instance
        """
        instance = cls(data["sessionId"])
        instance.context = data.get("context", {})
        instance._size_estimate = data.get("sizeEstimate", 0)
        if "created" in data:
            instance.created = datetime.fromisoformat(data["created"])
        return instance

    def __len__(self) -> int:
        """Return number of stored keys."""
        return len(self.context)

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.context
