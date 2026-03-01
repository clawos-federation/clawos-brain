#!/usr/bin/env python3
"""Nomination Manager - Auto-nomination workflow for federation memory

This module handles the nomination of high-performing agents to
federation memory. Nomination requires Boss approval before
actual promotion.

Process:
1. Check agents with score >= 0.85
2. Create nomination proposal in blackboard
3. Wait for Boss approval
4. On approval: promote to federation memory
5. On rejection: log and dismiss

Usage:
    from nomination import NominationManager

    manager = NominationManager()
    candidates = manager.check_candidates()
    for agent in candidates:
        manager.create_nomination(agent)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Nomination:
    """Represents a nomination for federation memory."""

    nomination_id: str
    agent_id: str
    utility_score: float
    timestamp: str
    status: str  # pending, approved, rejected
    reason: str
    evidence: dict
    boss_notes: str = ""


class NominationManager:
    """Manages agent nominations for federation memory."""

    def __init__(
        self, scores_dir: Optional[Path] = None, nominations_dir: Optional[Path] = None
    ):
        """
        Initialize the NominationManager.

        Args:
            scores_dir: Optional custom scores directory
            nominations_dir: Optional custom nominations directory
        """
        self.scores_dir = scores_dir or Path.home() / "clawos/blackboard/utility-scores"
        self.nominations_dir = (
            nominations_dir or Path.home() / "clawos/blackboard/nominations"
        )
        self.nominations_dir.mkdir(parents=True, exist_ok=True)

        # Import scorer here to avoid circular imports
        from scorer import UtilityScorer

        self.scorer = UtilityScorer(scores_dir=self.scores_dir)

    def check_candidates(self) -> list[dict]:
        """
        Check for agents eligible for nomination.

        Returns:
            List of agent dictionaries eligible for nomination
        """
        candidates = []

        for file_path in self.scores_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text())

                # Check nomination eligibility
                if data.get("nominationEligible", False):
                    # Check if already nominated (pending)
                    if not self._has_pending_nomination(data["agentId"]):
                        candidates.append(data)
            except json.JSONDecodeError:
                continue

        return sorted(candidates, key=lambda x: x.get("utilityScore", 0), reverse=True)

    def create_nomination(self, agent_data: dict, reason: str = "") -> str:
        """
        Create a nomination proposal for an agent.

        Args:
            agent_data: Agent score data dictionary
            reason: Optional reason for nomination

        Returns:
            Nomination ID
        """
        agent_id = agent_data["agentId"]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        nomination_id = f"nom-{agent_id}-{timestamp}"

        nomination = {
            "nominationId": nomination_id,
            "agentId": agent_id,
            "utilityScore": agent_data.get("utilityScore", 0),
            "tier": agent_data.get("tier", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "reason": reason
            or f"Score {agent_data.get('utilityScore', 0):.2f} exceeds threshold 0.85",
            "evidence": {
                "scoreHistory": agent_data.get("history", [])[
                    -5:
                ],  # Last 5 score changes
                "lastUpdated": agent_data.get("lastUpdated"),
            },
            "bossNotes": "",
            "approvedBy": None,
            "approvedAt": None,
        }

        # Save nomination
        file_path = self.nominations_dir / f"{nomination_id}.json"
        file_path.write_text(json.dumps(nomination, indent=2))

        return nomination_id

    def approve_nomination(
        self, nomination_id: str, boss_notes: str = "", approved_by: str = "boss"
    ) -> bool:
        """
        Approve a nomination (Boss action required).

        Args:
            nomination_id: The nomination to approve
            boss_notes: Optional notes from Boss
            approved_by: Identifier of approver

        Returns:
            True if approved successfully
        """
        file_path = self.nominations_dir / f"{nomination_id}.json"

        if not file_path.exists():
            return False

        try:
            nomination = json.loads(file_path.read_text())
        except json.JSONDecodeError:
            return False

        # Update nomination status
        nomination["status"] = "approved"
        nomination["bossNotes"] = boss_notes
        nomination["approvedBy"] = approved_by
        nomination["approvedAt"] = datetime.now().isoformat()

        file_path.write_text(json.dumps(nomination, indent=2))

        # Log the approval (would trigger federation memory update in full system)
        self._log_approval(nomination)

        return True

    def reject_nomination(self, nomination_id: str, boss_notes: str = "") -> bool:
        """
        Reject a nomination (Boss action).

        Args:
            nomination_id: The nomination to reject
            boss_notes: Reason for rejection

        Returns:
            True if rejected successfully
        """
        file_path = self.nominations_dir / f"{nomination_id}.json"

        if not file_path.exists():
            return False

        try:
            nomination = json.loads(file_path.read_text())
        except json.JSONDecodeError:
            return False

        # Update nomination status
        nomination["status"] = "rejected"
        nomination["bossNotes"] = boss_notes
        nomination["approvedBy"] = None
        nomination["approvedAt"] = datetime.now().isoformat()

        file_path.write_text(json.dumps(nomination, indent=2))

        return True

    def get_pending_nominations(self) -> list[dict]:
        """
        Get all pending nominations awaiting Boss approval.

        Returns:
            List of pending nomination dictionaries
        """
        pending = []

        for file_path in self.nominations_dir.glob("nom-*.json"):
            try:
                nomination = json.loads(file_path.read_text())
                if nomination.get("status") == "pending":
                    pending.append(nomination)
            except json.JSONDecodeError:
                continue

        return sorted(pending, key=lambda x: x.get("utilityScore", 0), reverse=True)

    def get_all_nominations(self, status: Optional[str] = None) -> list[dict]:
        """
        Get all nominations, optionally filtered by status.

        Args:
            status: Optional status filter (pending, approved, rejected)

        Returns:
            List of nomination dictionaries
        """
        nominations = []

        for file_path in self.nominations_dir.glob("nom-*.json"):
            try:
                nomination = json.loads(file_path.read_text())
                if status is None or nomination.get("status") == status:
                    nominations.append(nomination)
            except json.JSONDecodeError:
                continue

        return sorted(nominations, key=lambda x: x.get("timestamp", ""), reverse=True)

    def _has_pending_nomination(self, agent_id: str) -> bool:
        """Check if agent has a pending nomination."""
        for file_path in self.nominations_dir.glob(f"nom-{agent_id}-*.json"):
            try:
                nomination = json.loads(file_path.read_text())
                if nomination.get("status") == "pending":
                    return True
            except json.JSONDecodeError:
                continue
        return False

    def _log_approval(self, nomination: dict) -> None:
        """Log approved nomination to federation log."""
        log_dir = Path.home() / "clawos/blackboard/federation"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "nominations.log"
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] APPROVED: {nomination['agentId']} (score: {nomination['utilityScore']})\n"

        with open(log_file, "a") as f:
            f.write(log_entry)

    def auto_nominate_eligible(self) -> list[str]:
        """
        Automatically create nominations for all eligible agents.

        This creates pending nominations that require Boss approval.

        Returns:
            List of created nomination IDs
        """
        candidates = self.check_candidates()
        nomination_ids = []

        for candidate in candidates:
            try:
                nomination_id = self.create_nomination(candidate)
                nomination_ids.append(nomination_id)
            except Exception as e:
                print(f"Failed to nominate {candidate['agentId']}: {e}")

        return nomination_ids


# CLI interface
if __name__ == "__main__":
    import sys

    manager = NominationManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            candidates = manager.check_candidates()
            if candidates:
                print(f"Found {len(candidates)} nomination candidates:")
                for c in candidates:
                    print(f"  - {c['agentId']}: {c.get('utilityScore', 0):.2f}")
            else:
                print("No nomination candidates found.")

        elif sys.argv[1] == "pending":
            pending = manager.get_pending_nominations()
            if pending:
                print(f"Pending nominations ({len(pending)}):")
                for n in pending:
                    print(
                        f"  - {n['nominationId']}: {n['agentId']} (score: {n['utilityScore']})"
                    )
            else:
                print("No pending nominations.")

        elif sys.argv[1] == "auto":
            nomination_ids = manager.auto_nominate_eligible()
            if nomination_ids:
                print(f"Created {len(nomination_ids)} nominations:")
                for nid in nomination_ids:
                    print(f"  - {nid}")
            else:
                print("No new nominations created.")

        elif sys.argv[1] == "approve":
            if len(sys.argv) < 3:
                print("Usage: python nomination.py approve <nomination_id>")
                sys.exit(1)
            nomination_id = sys.argv[2]
            notes = sys.argv[3] if len(sys.argv) > 3 else ""
            if manager.approve_nomination(nomination_id, notes):
                print(f"Approved: {nomination_id}")
            else:
                print(f"Failed to approve: {nomination_id}")

        elif sys.argv[1] == "reject":
            if len(sys.argv) < 3:
                print("Usage: python nomination.py reject <nomination_id>")
                sys.exit(1)
            nomination_id = sys.argv[2]
            notes = sys.argv[3] if len(sys.argv) > 3 else "Rejected by Boss"
            if manager.reject_nomination(nomination_id, notes):
                print(f"Rejected: {nomination_id}")
            else:
                print(f"Failed to reject: {nomination_id}")

        elif sys.argv[1] == "list":
            status = sys.argv[2] if len(sys.argv) > 2 else None
            nominations = manager.get_all_nominations(status)
            print(json.dumps(nominations, indent=2))

    else:
        # Default: show pending
        pending = manager.get_pending_nominations()
        candidates = manager.check_candidates()

        print("=== Nomination Status ===")
        print(f"Eligible candidates: {len(candidates)}")
        print(f"Pending nominations: {len(pending)}")

        if candidates:
            print("\nCandidates ready for nomination:")
            for c in candidates:
                print(f"  - {c['agentId']}: {c.get('utilityScore', 0):.2f}")

        if pending:
            print("\nPending Boss approval:")
            for n in pending:
                print(f"  - {n['nominationId']}: {n['agentId']}")
