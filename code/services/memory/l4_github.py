#!/usr/bin/env python3
"""L4 GitHub Memory - Sync to clawos-brain repository

This layer provides GitHub-based long-term memory sync for
cross-session and cross-machine memory persistence.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import shutil


class L4GitHubMemory:
    """GitHub memory - Sync to clawos-brain repository.

    Capacity: Unlimited (GitHub storage)
    Purpose: Cross-session/cross-machine memory sync
    Persistence: GitHub repository (clawos-brain)

    Note: Requires git setup with proper credentials
    """

    DEFAULT_REPO_PATH = Path.home() / "openclaw-system/clawos-brain"
    MEMORY_PATH = "memory/github/"

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize GitHub memory.

        Args:
            repo_path: Optional custom repository path
        """
        self.repo_path = repo_path or self.DEFAULT_REPO_PATH
        self.memory_path = self.repo_path / self.MEMORY_PATH

        # Create directories
        self.memory_path.mkdir(parents=True, exist_ok=True)

    def _check_git_repo(self) -> bool:
        """Check if repository exists and is a git repo."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists()

    def _run_git(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command in the repository."""
        return subprocess.run(
            ["git"] + list(args),
            cwd=self.repo_path,
            check=check,
            capture_output=True,
            text=True,
        )

    def export_experiences(self, experiences: List[Dict[str, Any]]) -> str:
        """Export experiences to GitHub memory.

        Args:
            experiences: List of experience dicts to export

        Returns:
            Path to created file
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H%M%S")

        # Create daily directory
        daily_path = self.memory_path / date_str
        daily_path.mkdir(parents=True, exist_ok=True)

        # Create experiences file
        file_name = f"experiences-{timestamp}.json"
        file_path = daily_path / file_name

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "date": date_str,
            "experiences": experiences,
            "count": len(experiences),
            "version": "1.0",
        }

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        return str(file_path)

    def export_agent_summary(self, agent_id: str, summary: Dict[str, Any]) -> str:
        """Export agent summary to GitHub memory.

        Args:
            agent_id: Agent ID
            summary: Summary data dict

        Returns:
            Path to created file
        """
        agents_path = self.memory_path / "agents"
        agents_path.mkdir(parents=True, exist_ok=True)

        file_path = agents_path / f"{agent_id}.json"

        summary_data = {
            "agent_id": agent_id,
            "updated_at": datetime.now().isoformat(),
            **summary,
        }

        with open(file_path, "w") as f:
            json.dump(summary_data, f, indent=2)

        return str(file_path)

    def export_session_archive(
        self, session_id: str, session_data: Dict[str, Any]
    ) -> str:
        """Export session archive to GitHub memory.

        Args:
            session_id: Session ID
            session_data: Session data dict

        Returns:
            Path to created file
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        sessions_path = self.memory_path / "sessions" / date_str
        sessions_path.mkdir(parents=True, exist_ok=True)

        file_path = sessions_path / f"{session_id}.json"

        archive_data = {
            "session_id": session_id,
            "archived_at": datetime.now().isoformat(),
            **session_data,
        }

        with open(file_path, "w") as f:
            json.dump(archive_data, f, indent=2)

        return str(file_path)

    def export_lessons_learned(self, lessons: List[Dict[str, Any]]) -> str:
        """Export lessons learned to GitHub memory.

        Args:
            lessons: List of lesson dicts

        Returns:
            Path to created file
        """
        lessons_path = self.memory_path / "lessons"
        lessons_path.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = lessons_path / f"{date_str}.json"

        # Append to existing file if it exists
        existing = []
        if file_path.exists():
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    existing = data.get("lessons", [])
                except json.JSONDecodeError:
                    pass

        all_lessons = existing + lessons

        lessons_data = {
            "date": date_str,
            "updated_at": datetime.now().isoformat(),
            "lessons": all_lessons,
            "count": len(all_lessons),
        }

        with open(file_path, "w") as f:
            json.dump(lessons_data, f, indent=2)

        return str(file_path)

    def sync(self, message: Optional[str] = None) -> Dict[str, Any]:
        """Sync to GitHub.

        Args:
            message: Optional commit message

        Returns:
            Dict with sync results
        """
        if not self._check_git_repo():
            return {
                "success": False,
                "error": "Not a git repository",
                "path": str(self.repo_path),
            }

        try:
            # Check for changes
            status_result = self._run_git("status", "--porcelain")
            if not status_result.stdout.strip():
                return {
                    "success": True,
                    "message": "No changes to sync",
                    "files_changed": 0,
                }

            # Stage all changes
            self._run_git("add", ".")

            # Create commit
            commit_msg = (
                message or f"Memory sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            self._run_git("commit", "-m", commit_msg)

            # Get commit info
            log_result = self._run_git("log", "-1", "--format=%H %s")
            commit_hash, commit_subject = log_result.stdout.strip().split(" ", 1)

            return {
                "success": True,
                "message": "Committed successfully",
                "commit_hash": commit_hash,
                "commit_subject": commit_subject,
                "files_changed": len(status_result.stdout.strip().split("\n")),
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "stderr": e.stderr if hasattr(e, "stderr") else None,
            }

    def push(self) -> Dict[str, Any]:
        """Push to GitHub remote.

        Returns:
            Dict with push results
        """
        if not self._check_git_repo():
            return {"success": False, "error": "Not a git repository"}

        try:
            self._run_git("push")
            return {"success": True, "message": "Pushed to GitHub"}
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "stderr": e.stderr if hasattr(e, "stderr") else None,
            }

    def pull(self) -> Dict[str, Any]:
        """Pull from GitHub remote.

        Returns:
            Dict with pull results
        """
        if not self._check_git_repo():
            return {"success": False, "error": "Not a git repository"}

        try:
            result = self._run_git("pull")
            return {
                "success": True,
                "message": "Pulled from GitHub",
                "output": result.stdout,
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "stderr": e.stderr if hasattr(e, "stderr") else None,
            }

    def get_status(self) -> Dict[str, Any]:
        """Get repository status.

        Returns:
            Dict with status info
        """
        if not self._check_git_repo():
            return {"is_repo": False, "path": str(self.repo_path)}

        try:
            # Get branch
            branch_result = self._run_git("branch", "--show-current")
            branch = branch_result.stdout.strip()

            # Get status
            status_result = self._run_git("status", "--porcelain")
            changes = status_result.stdout.strip()

            # Get last commit
            log_result = self._run_git("log", "-1", "--format=%H %ci %s")
            last_commit = log_result.stdout.strip()

            return {
                "is_repo": True,
                "path": str(self.repo_path),
                "branch": branch,
                "has_changes": bool(changes),
                "changed_files": len(changes.split("\n")) if changes else 0,
                "last_commit": last_commit,
            }
        except subprocess.CalledProcessError:
            return {
                "is_repo": True,
                "path": str(self.repo_path),
                "error": "Failed to get status",
            }

    def list_exports(self, category: str = "all") -> List[Dict[str, Any]]:
        """List exported files.

        Args:
            category: Category to list (all, agents, sessions, lessons)

        Returns:
            List of export info dicts
        """
        exports = []

        categories = (
            ["agents", "sessions", "lessons"] if category == "all" else [category]
        )

        for cat in categories:
            cat_path = self.memory_path / cat
            if not cat_path.exists():
                continue

            for file_path in cat_path.rglob("*.json"):
                exports.append(
                    {
                        "category": cat,
                        "path": str(file_path.relative_to(self.memory_path)),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                    }
                )

        return sorted(exports, key=lambda x: x["modified"], reverse=True)
