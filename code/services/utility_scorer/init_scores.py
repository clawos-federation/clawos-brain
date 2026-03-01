#!/usr/bin/env python3
"""Initialize utility scores for all ClawOS agents.

This script creates initial utility score files for all agents
defined in the ClawOS system architecture.

Run once to set up initial scores for all agents.
"""

import json
from datetime import datetime
from pathlib import Path

# All agents from AGENTS.md
AGENTS = {
    # Command Layer (3) - Higher initial trust
    "assistant": {"tier": "command", "initialScore": 0.70},
    "gm": {"tier": "command", "initialScore": 0.75},
    "validator": {"tier": "command", "initialScore": 0.75},
    # PM Layer (4) - Good initial trust
    "platform-pm": {"tier": "pm", "initialScore": 0.65},
    "coding-pm": {"tier": "pm", "initialScore": 0.65},
    "writing-pm": {"tier": "pm", "initialScore": 0.65},
    "research-pm": {"tier": "pm", "initialScore": 0.60},
    # Workers - Dev Group (codex)
    "coder-frontend": {"tier": "worker", "initialScore": 0.55},
    "coder-backend": {"tier": "worker", "initialScore": 0.55},
    "tester-auto": {"tier": "worker", "initialScore": 0.50},
    # Workers - Writing Group (glm-5)
    "writer-general": {"tier": "worker", "initialScore": 0.55},
    "reviewer-content": {"tier": "worker", "initialScore": 0.55},
    # Workers - System Group (codex)
    "sreagent": {"tier": "worker", "initialScore": 0.60},
    "securityagent": {"tier": "worker", "initialScore": 0.60},
    "github-ops": {"tier": "worker", "initialScore": 0.55},
    "alpha-bridge": {"tier": "worker", "initialScore": 0.50},
    # Workers - Research Group (glm-5)
    "researcher-web": {"tier": "worker", "initialScore": 0.50},
    "researcher-file": {"tier": "worker", "initialScore": 0.50},
    # Workers - Service Group (glm-5, shared)
    "browser-worker": {"tier": "worker", "initialScore": 0.55},
}

NOMINATION_THRESHOLD = 0.85


def initialize_scores(scores_dir: Path = None):
    """Create initial score files for all agents."""
    scores_dir = scores_dir or Path.home() / "clawos/blackboard/utility-scores"
    scores_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()

    for agent_id, config in AGENTS.items():
        score = config["initialScore"]
        tier = config["tier"]

        data = {
            "agentId": agent_id,
            "tier": tier,
            "utilityScore": score,
            "lastUpdated": timestamp,
            "nominationEligible": score >= NOMINATION_THRESHOLD,
            "initialized": True,
            "history": [
                {
                    "timestamp": timestamp,
                    "oldScore": None,
                    "newScore": score,
                    "notes": f"Initial score for {tier} tier agent",
                }
            ],
        }

        file_path = scores_dir / f"{agent_id}.json"
        file_path.write_text(json.dumps(data, indent=2))
        print(f"Created: {file_path.name} (score: {score})")

    print(f"\nInitialized {len(AGENTS)} agent scores in {scores_dir}")


if __name__ == "__main__":
    import sys

    scores_dir = None
    if len(sys.argv) > 1:
        scores_dir = Path(sys.argv[1])

    initialize_scores(scores_dir)
