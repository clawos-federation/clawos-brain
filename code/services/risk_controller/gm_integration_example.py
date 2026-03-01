#!/usr/bin/env python3
"""
GM Integration Example - How to use Risk Controller in GM decision flow

This shows the proper integration pattern for GM to enforce risk rules
before dispatching tasks to agents.
"""

import sys
from pathlib import Path

# Add clawos to path (go up 4 levels to openclaw-system)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from clawos.services.risk_controller import (
    validate_action,
    get_allowed_nodes,
    get_risk_controller,
)


class GMWithRiskControl:
    """Example GM implementation with integrated risk control"""

    def dispatch_task(self, agent_id: str, action: str, context: dict) -> dict:
        """
        Dispatch task to agent with risk validation.

        Returns:
            {
                "allowed": bool,
                "reason": str or None,
                "dispatched": bool,
                "targetNode": str
            }
        """
        # Step 1: Get allowed nodes for this agent
        allowed_nodes = get_allowed_nodes(agent_id)

        # Step 2: Determine target node
        target_node = context.get("targetNode", "default")

        # Step 3: Check if target node is allowed
        if allowed_nodes != ["*"] and target_node not in allowed_nodes:
            # Agent is restricted to specific nodes
            if target_node == "default":
                # Auto-select first allowed node
                target_node = allowed_nodes[0]
                context["targetNode"] = target_node
            elif target_node not in allowed_nodes:
                return {
                    "allowed": False,
                    "reason": f"Agent '{agent_id}' cannot run on node '{target_node}'. Allowed: {allowed_nodes}",
                    "dispatched": False,
                    "targetNode": target_node,
                }

        # Step 4: Validate action against risk rules
        allowed, reason = validate_action(agent_id, action, context)

        if not allowed:
            return {
                "allowed": False,
                "reason": reason,
                "dispatched": False,
                "targetNode": target_node,
            }

        # Step 5: Dispatch to agent (mock implementation)
        # In real implementation, this would call openclaw agent --agent {agent_id}
        print(f"[GM] Dispatching to {agent_id}: action={action}, node={target_node}")

        return {
            "allowed": True,
            "reason": None,
            "dispatched": True,
            "targetNode": target_node,
        }

    def dispatch_alpha_task(self, action: str, context: dict = None) -> dict:
        """Convenience method for alpha-executor tasks"""
        if context is None:
            context = {}

        # Alpha tasks must go to quant node
        context.setdefault("targetNode", "quant")

        return self.dispatch_task("alpha-executor", action, context)


def main():
    """Demo the GM integration with risk controller"""
    gm = GMWithRiskControl()

    print("=" * 60)
    print("GM Risk Controller Integration Demo")
    print("=" * 60)

    # Scenario 1: Alpha executor on wrong node
    print("\n[Scenario 1] Alpha executor trying to run on 'local' node:")
    result = gm.dispatch_task(
        "alpha-executor", "execute-trade", {"targetNode": "local", "symbol": "AAPL"}
    )
    print(f"  Result: {result}")

    # Scenario 2: Alpha executor on correct node
    print("\n[Scenario 2] Alpha executor on 'quant' node:")
    result = gm.dispatch_task(
        "alpha-executor", "execute-trade", {"targetNode": "quant", "symbol": "AAPL"}
    )
    print(f"  Result: {result}")

    # Scenario 3: Using convenience method
    print("\n[Scenario 3] Using dispatch_alpha_task convenience method:")
    result = gm.dispatch_alpha_task("analyze-market", {"symbol": "TSLA"})
    print(f"  Result: {result}")

    # Scenario 4: Non-production agent trying to deploy
    print("\n[Scenario 4] Coding PM trying to deploy to production:")
    result = gm.dispatch_task(
        "coding-pm", "deploy-production", {"targetNode": "prod-server"}
    )
    print(f"  Result: {result}")

    # Scenario 5: Coding PM with normal action
    print("\n[Scenario 5] Coding PM with allowed action:")
    result = gm.dispatch_task(
        "coding-pm", "write-code", {"targetNode": "dev", "task": "implement-feature"}
    )
    print(f"  Result: {result}")

    # Show violation log
    print("\n" + "=" * 60)
    print("Violation Log:")
    print("=" * 60)
    rc = get_risk_controller()
    for violation in rc.violation_log:
        print(f"  - {violation['timestamp']}: {violation['reason']}")

    # Save violations
    rc.save_violation_log()
    print(
        "\n  Violations saved to ~/clawos/blackboard/shared/violations/violations.json"
    )


if __name__ == "__main__":
    main()
