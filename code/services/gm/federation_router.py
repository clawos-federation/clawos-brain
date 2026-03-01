#!/usr/bin/env python3
"""Federation Router - Enhanced task routing for ClawOS federation

This module provides intelligent task routing capabilities that consider:
- A2A Agent Cards for capability matching
- Node availability and online status
- Agent utility scores for optimal selection
- Evolution queue for idle-time scheduling

Usage:
    from clawos.services.gm.federation_router import FederationRouter

    router = FederationRouter()
    decision = router.route_task({"type": "code", "description": "Add login feature"})
    print(f"Selected agent: {decision['agentId']} on node {decision['node']}")
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class FederationRouter:
    """Enhanced task routing with A2A, node awareness, and evolution integration."""

    def __init__(self):
        self.blackboard = Path.home() / "clawos/blackboard"
        self.a2a_cards_dir = Path.home() / "openclaw-system/clawos/a2a-cards"
        self.features_file = Path.home() / "openclaw-system/clawos/config/features.json"

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to best agent/node based on capabilities and scores.

        Args:
            task: Task dictionary with 'type' and 'description' keys

        Returns:
            Routing decision with agentId, node, tier, confidence, utilityScore
        """
        # 1. Get required capabilities
        capabilities = self._extract_capabilities(task)

        # 2. Find matching agents from A2A cards
        candidates = self._find_agents(capabilities)

        # 3. Filter by node availability
        available = [
            a
            for a in candidates
            if self._is_node_online(a.get("identity", {}).get("node"))
        ]

        # 4. Rank by utility score
        ranked = sorted(
            available,
            key=lambda a: a.get("performance", {}).get("utilityScore", 0),
            reverse=True,
        )

        if not ranked:
            return {
                "error": "No available agent for this task",
                "capabilities_requested": capabilities,
                "candidates_found": len(candidates),
                "available_count": 0,
            }

        # 5. Return best match
        best = ranked[0]
        return {
            "agentId": best.get("humanReadableId", "unknown"),
            "node": best.get("identity", {}).get("node", "unknown"),
            "tier": best.get("identity", {}).get("tier", "worker"),
            "confidence": self._calculate_confidence(ranked),
            "utilityScore": best.get("performance", {}).get("utilityScore", 0.5),
            "alternatives": [
                {
                    "agentId": a.get("humanReadableId"),
                    "score": a.get("performance", {}).get("utilityScore", 0),
                }
                for a in ranked[1:4]  # Top 3 alternatives
            ],
        }

    def _extract_capabilities(self, task: Dict[str, Any]) -> List[str]:
        """Extract required capabilities from task description.

        Args:
            task: Task dictionary

        Returns:
            List of capability strings
        """
        task_type = task.get("type", "").lower()
        desc = task.get("description", "").lower()

        capabilities = []

        # Code-related tasks
        if "code" in task_type or "开发" in desc or "implement" in desc:
            capabilities.extend(["coding", "software-engineering", "development"])

        # Writing tasks
        if "write" in task_type or "写作" in desc or "document" in desc:
            capabilities.extend(["writing", "content-creation", "documentation"])

        # Research tasks
        if "research" in task_type or "调研" in desc or "analyze" in desc:
            capabilities.extend(["research", "analysis", "investigation"])

        # Testing tasks
        if "test" in task_type or "测试" in desc or "verify" in desc:
            capabilities.extend(["testing", "quality-assurance", "validation"])

        # Alpha/trading tasks
        if "alpha" in task_type or "quant" in desc or "trading" in desc:
            capabilities.extend(["quantitative", "trading", "alpha"])

        # Default to general if no specific capabilities detected
        return capabilities or ["general"]

    def _find_agents(self, capabilities: List[str]) -> List[Dict[str, Any]]:
        """Find agents matching capabilities from A2A cards.

        Args:
            capabilities: List of required capabilities

        Returns:
            List of matching agent cards
        """
        if not self.a2a_cards_dir.exists():
            return []

        candidates = []

        for card_file in self.a2a_cards_dir.rglob("*.json"):
            try:
                card = json.loads(card_file.read_text())

                # Extract agent's skills and tags
                agent_skills = []
                agent_tags = []

                for skill in card.get("skills", []):
                    agent_skills.append(skill.get("id", ""))
                    agent_tags.extend(skill.get("tags", []))

                # Check if any capability matches
                matches = any(
                    c in agent_skills or c in agent_tags for c in capabilities
                )

                if matches:
                    candidates.append(card)

            except (json.JSONDecodeError, IOError):
                continue

        return candidates

    def _is_node_online(self, node: Optional[str]) -> bool:
        """Check if node is online.

        Args:
            node: Node identifier

        Returns:
            True if node is online or status unknown
        """
        if not node:
            return True

        status_file = self.blackboard / "shared/node-status.json"
        if not status_file.exists():
            return True  # Assume online if no status file

        try:
            status = json.loads(status_file.read_text())
            nodes = status.get("nodes", {})
            # Handle both dict and list formats
            if isinstance(nodes, dict):
                nodes = nodes.values()
            for n in nodes:
                if n.get("id") == node or n.get("role") == node:
                    return n.get("status") == "online"
        except (json.JSONDecodeError, IOError):
            pass

        return True  # Default to online

    def _calculate_confidence(self, ranked: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for routing decision.

        Higher confidence when there's a clear best choice.

        Args:
            ranked: List of ranked agent cards (best first)

        Returns:
            Confidence score between 0.5 and 1.0
        """
        if len(ranked) < 2:
            return 1.0

        best_score = ranked[0].get("performance", {}).get("utilityScore", 0)
        second_score = ranked[1].get("performance", {}).get("utilityScore", 0)

        if best_score == 0:
            return 0.5

        # Confidence increases with score gap
        return min(1.0, 0.5 + (best_score - second_score) / 2)

    def check_evolution_queue(self) -> Optional[Dict[str, Any]]:
        """Check if there are pending evolution tasks for idle time.

        Returns:
            Dict with priority and task, or None if no pending tasks
        """
        queue_dir = self.blackboard / "federation/evolution-queue"

        if not queue_dir.exists():
            return None

        priority_files = {
            "P1": "p1-knowledge.json",
            "P2": "p2-training.json",
            "P3": "p3-exploration.json",
            "P4": "p4-soul-drafts.json",
        }

        for priority, filename in priority_files.items():
            queue_file = queue_dir / filename

            if queue_file.exists():
                try:
                    queue = json.loads(queue_file.read_text())
                    tasks = queue.get("tasks", [])

                    if tasks:
                        return {
                            "priority": priority,
                            "task": tasks[0],
                            "queue_size": len(tasks),
                        }
                except (json.JSONDecodeError, IOError):
                    continue

        return None

    def get_node_status(self) -> Dict[str, Any]:
        """Get current node status for the federation.

        Returns:
            Dict with node status information
        """
        status_file = self.blackboard / "shared/node-status.json"

        if not status_file.exists():
            return {"nodes": [], "error": "Status file not found"}

        try:
            return json.loads(status_file.read_text())
        except (json.JSONDecodeError, IOError) as e:
            return {"nodes": [], "error": str(e)}

    def log_decision(
        self,
        task_id: str,
        decision: Dict[str, Any],
        alternatives: List[str],
        result: str,
    ) -> None:
        """Log routing decision to GM decisions log.

        Args:
            task_id: Task identifier
            decision: Routing decision made
            alternatives: List of alternative agents considered
            result: Result of the task (success/failure/pending)
        """
        decisions_file = self.blackboard / "gm/decisions.md"
        decisions_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"""
### {task_id}
- **时间**: {timestamp}
- **选择**: {decision.get("agentId", "unknown")} (score: {decision.get("utilityScore", 0):.2f})
- **节点**: {decision.get("node", "unknown")}
- **置信度**: {decision.get("confidence", 0):.2f}
- **备选**: {", ".join(alternatives) if alternatives else "无"}
- **结果**: {result}

"""

        with open(decisions_file, "a") as f:
            f.write(entry)


# Convenience functions for SDK usage
def route_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Route a task to the best available agent.

    Args:
        task: Task dictionary with type and description

    Returns:
        Routing decision
    """
    router = FederationRouter()
    return router.route_task(task)


def get_evolution_task() -> Optional[Dict[str, Any]]:
    """Get next pending evolution task for idle time.

    Returns:
        Evolution task or None
    """
    router = FederationRouter()
    return router.check_evolution_queue()


if __name__ == "__main__":
    # Demo usage
    router = FederationRouter()

    # Test routing
    print("=== Task Routing Test ===")
    test_task = {"type": "code", "description": "Add user authentication feature"}
    result = router.route_task(test_task)
    print(f"Task: {test_task}")
    print(f"Decision: {json.dumps(result, indent=2)}")

    # Test evolution queue
    print("\n=== Evolution Queue Check ===")
    evolution = router.check_evolution_queue()
    if evolution:
        print(f"Found {evolution['priority']} task: {evolution['task'].get('id')}")
    else:
        print("No pending evolution tasks")

    # Test node status
    print("\n=== Node Status ===")
    status = router.get_node_status()
    for node in status.get("nodes", []):
        print(f"  {node.get('name')}: {node.get('status')}")
