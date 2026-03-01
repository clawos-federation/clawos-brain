#!/usr/bin/env python3
"""L3 Vector Memory - ChromaDB-based long-term memory

This layer provides long-term memory storage for experiences and learnings.
Uses a simplified file-based implementation (ChromaDB stub for future upgrade).
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
import hashlib
import re


class L3VectorMemory:
    """Vector memory - Long-term experience storage.

    Capacity: Unlimited (file-based)
    Purpose: Store and retrieve experiences for learning
    Persistence: JSONL files (ChromaDB-ready structure)

    Note: This is a simplified file-based implementation.
    Full vector search requires: pip install chromadb
    """

    DEFAULT_STORAGE_PATH = Path.home() / "clawos/memory/l3/experiences"
    COLLECTION = "clawos-experiences"

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize vector memory.

        Args:
            storage_path: Optional custom storage path
        """
        self.storage_path = storage_path or self.DEFAULT_STORAGE_PATH
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.experiences_file = self.storage_path / "experiences.jsonl"
        self.index_file = self.storage_path / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load or create experience index."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                self._index = json.load(f)
        else:
            self._index = {
                "by_agent": {},  # agent_id -> [experience_ids]
                "by_type": {},  # type -> [experience_ids]
                "total": 0,
            }

    def _save_index(self) -> None:
        """Save experience index."""
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def _generate_id(self, agent_id: str, content: str) -> str:
        """Generate unique experience ID."""
        timestamp = datetime.now().timestamp()
        hash_input = f"{agent_id}-{content[:100]}-{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for simple matching.

        This is a simplified keyword extraction for the file-based implementation.
        """
        # Simple keyword extraction: lowercase, remove punctuation, split
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        # Remove common words
        stopwords = {
            "the",
            "and",
            "for",
            "was",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
        }
        return [w for w in words if w not in stopwords][:20]

    def store_experience(
        self,
        agent_id: str,
        experience: str,
        experience_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ) -> str:
        """Store an experience for later retrieval.

        Args:
            agent_id: ID of the agent having this experience
            experience: The experience text/description
            experience_type: Type of experience (task, decision, learning, etc.)
            metadata: Optional additional metadata
            score: Optional success/utility score

        Returns:
            Experience ID
        """
        exp_id = self._generate_id(agent_id, experience)
        keywords = self._extract_keywords(experience)

        entry = {
            "id": exp_id,
            "agent_id": agent_id,
            "experience": experience,
            "type": experience_type,
            "keywords": keywords,
            "metadata": metadata or {},
            "score": score,
            "created": datetime.now().isoformat(),
        }

        # Append to experiences file
        with open(self.experiences_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Update index
        if agent_id not in self._index["by_agent"]:
            self._index["by_agent"][agent_id] = []
        self._index["by_agent"][agent_id].append(exp_id)

        if experience_type not in self._index["by_type"]:
            self._index["by_type"][experience_type] = []
        self._index["by_type"][experience_type].append(exp_id)

        self._index["total"] += 1
        self._save_index()

        return exp_id

    def retrieve_recent(
        self, agent_id: str, limit: int = 10, experience_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve recent experiences for an agent.

        Args:
            agent_id: Agent ID to query
            limit: Maximum number of experiences
            experience_type: Optional type filter

        Returns:
            List of experience dicts
        """
        if not self.experiences_file.exists():
            return []

        experiences = []
        with open(self.experiences_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry["agent_id"] == agent_id:
                        if (
                            experience_type is None
                            or entry.get("type") == experience_type
                        ):
                            experiences.append(entry)
                except json.JSONDecodeError:
                    continue

        # Return most recent first
        return experiences[-limit:][::-1]

    def search_by_keywords(
        self, keywords: List[str], limit: int = 20, agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search experiences by keywords.

        This is a simplified keyword search. For vector similarity,
        upgrade to ChromaDB.

        Args:
            keywords: Keywords to search for
            limit: Maximum results
            agent_id: Optional agent filter

        Returns:
            List of matching experiences with scores
        """
        if not self.experiences_file.exists():
            return []

        results = []
        keywords_lower = [k.lower() for k in keywords]

        with open(self.experiences_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Filter by agent if specified
                    if agent_id and entry["agent_id"] != agent_id:
                        continue

                    # Calculate simple match score
                    entry_keywords = entry.get("keywords", [])
                    matches = sum(1 for k in keywords_lower if k in entry_keywords)

                    if matches > 0:
                        entry_copy = entry.copy()
                        entry_copy["match_score"] = matches / len(keywords_lower)
                        results.append(entry_copy)
                except json.JSONDecodeError:
                    continue

        # Sort by match score
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return results[:limit]

    def get_by_type(
        self, experience_type: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get experiences by type.

        Args:
            experience_type: Type to filter by
            limit: Maximum results

        Returns:
            List of experiences
        """
        if not self.experiences_file.exists():
            return []

        experiences = []
        with open(self.experiences_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == experience_type:
                        experiences.append(entry)
                except json.JSONDecodeError:
                    continue

        return experiences[-limit:][::-1]

    def get_high_scoring(
        self, min_score: float = 0.8, limit: int = 50, agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get high-scoring experiences.

        Args:
            min_score: Minimum score threshold
            limit: Maximum results
            agent_id: Optional agent filter

        Returns:
            List of high-scoring experiences
        """
        if not self.experiences_file.exists():
            return []

        experiences = []
        with open(self.experiences_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    score = entry.get("score")

                    if score is not None and score >= min_score:
                        if agent_id is None or entry["agent_id"] == agent_id:
                            experiences.append(entry)
                except json.JSONDecodeError:
                    continue

        experiences.sort(key=lambda x: x.get("score", 0), reverse=True)
        return experiences[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dict with stats
        """
        return {
            "total_experiences": self._index.get("total", 0),
            "agent_count": len(self._index.get("by_agent", {})),
            "type_count": len(self._index.get("by_type", {})),
            "types": list(self._index.get("by_type", {}).keys()),
        }

    def rebuild_index(self) -> None:
        """Rebuild index from experiences file."""
        self._index = {"by_agent": {}, "by_type": {}, "total": 0}

        if not self.experiences_file.exists():
            self._save_index()
            return

        with open(self.experiences_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    agent_id = entry["agent_id"]
                    exp_type = entry.get("type", "general")

                    if agent_id not in self._index["by_agent"]:
                        self._index["by_agent"][agent_id] = []
                    self._index["by_agent"][agent_id].append(entry["id"])

                    if exp_type not in self._index["by_type"]:
                        self._index["by_type"][exp_type] = []
                    self._index["by_type"][exp_type].append(entry["id"])

                    self._index["total"] += 1
                except json.JSONDecodeError:
                    continue

        self._save_index()
