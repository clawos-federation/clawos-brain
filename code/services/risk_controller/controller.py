#!/usr/bin/env python3
"""Risk Controller - SDK-level risk enforcement"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class RiskController:
    """SDK-level risk enforcement for ClawOS"""

    def __init__(self, risk_limits_path: str = None):
        if risk_limits_path is None:
            risk_limits_path = Path.home() / "clawos/blackboard/shared/risk-limits.json"
        self.rules = self._load_rules(risk_limits_path)
        self.logger = logging.getLogger("risk-controller")
        self.violation_log = []

    def _load_rules(self, path: Path) -> list:
        if path.exists():
            return json.loads(path.read_text()).get("rules", [])
        return []

    def validate_action(self, agent_id: str, action: str, context: dict) -> tuple:
        """Validate action against risk rules. Returns (allowed, reason)"""
        for rule in self.rules:
            if not self._applies_to_agent(rule, agent_id):
                continue

            # Node restriction check
            if rule["type"] == "node-restriction":
                target_node = context.get("targetNode", context.get("node"))
                allowed = rule.get("allowedNodes", ["*"])
                if target_node and allowed != ["*"] and target_node not in allowed:
                    return self._handle_violation(
                        agent_id,
                        action,
                        rule,
                        f"Node '{target_node}' not allowed for agent '{agent_id}'",
                    )

            # Action restriction check
            if rule["type"] == "action-restriction":
                forbidden = rule.get("forbiddenActions", [])
                if action in forbidden:
                    return self._handle_violation(
                        agent_id,
                        action,
                        rule,
                        f"Action '{action}' forbidden for agent '{agent_id}'",
                    )

            # Resource limit check
            if rule["type"] == "resource-limit":
                if not self._check_resource_limit(rule, agent_id, context):
                    return self._handle_violation(
                        agent_id,
                        action,
                        rule,
                        f"Resource limit exceeded for '{agent_id}'",
                    )

            # Safety action check
            if rule["type"] == "safety-action":
                if not self._check_safety(rule, agent_id, context):
                    return self._handle_violation(
                        agent_id,
                        action,
                        rule,
                        f"Safety condition violated for '{agent_id}'",
                    )

        return (True, None)

    def get_allowed_nodes(self, agent_id: str) -> list:
        """Get allowed nodes for an agent"""
        for rule in self.rules:
            if self._applies_to_agent(rule, agent_id):
                if "allowedNodes" in rule:
                    return rule["allowedNodes"]
        return ["*"]  # Default: all nodes

    def _applies_to_agent(self, rule: dict, agent_id: str) -> bool:
        """Check if rule applies to agent.
        
        Handles:
        - Positive patterns: agent matches → rule applies
        - Negation patterns (!xxx): agent matches → rule does NOT apply
        - Only negations, no match → rule applies ("all except")
        """
        agents = rule.get("agents", [])
        if not agents:
            return False  # No agents specified = rule doesn't apply
            
        has_positive_patterns = False
        
        for pattern in agents:
            if pattern.startswith("!"):
                # Negation: if agent matches, rule does NOT apply
                negated = pattern[1:]
                if negated == "*" or agent_id == negated or agent_id.startswith(negated.rstrip("*")):
                    return False
            else:
                has_positive_patterns = True
                # Positive pattern: if agent matches, rule applies
                if pattern == "*" or agent_id == pattern or agent_id.startswith(pattern.rstrip("*")):
                    return True
        
        # If we only had negation patterns and none matched, rule applies
        # (meaning "all agents except these negated ones")
        if not has_positive_patterns:
            return True
            
        return False

    def _handle_violation(
        self, agent_id: str, action: str, rule: dict, reason: str
    ) -> tuple:
        violation = {
            "timestamp": datetime.now().isoformat(),
            "agentId": agent_id,
            "action": action,
            "rule": rule["id"],
            "reason": reason,
            "enforcement": rule["enforcement"],
        }
        self.violation_log.append(violation)

        if rule["enforcement"] == "hard":
            self.logger.error(f"BLOCKED: {reason}")
            return (False, reason)
        else:
            self.logger.warning(f"WARNING: {reason}")
            return (True, f"Warning: {reason}")

    def _check_resource_limit(self, rule: dict, agent_id: str, context: dict) -> bool:
        limits = rule.get("limits", {})
        agent_limit = limits.get(agent_id, limits.get("default", float("inf")))
        current_usage = context.get("currentUsage", 0)
        return current_usage <= agent_limit

    def _check_safety(self, rule: dict, agent_id: str, context: dict) -> bool:
        trigger = rule.get("trigger", "")
        if "disconnect" in trigger:
            last_heartbeat = context.get("lastHeartbeat")
            if last_heartbeat:
                minutes_ago = (
                    datetime.now() - datetime.fromisoformat(last_heartbeat)
                ).seconds / 60
                threshold = int(trigger.split(">")[1].strip().split()[0])
                return minutes_ago <= threshold
        return True

    def is_rule_immutable(self, rule_id: str) -> bool:
        """Check if a rule can be modified at runtime"""
        immutable = json.loads(
            (Path.home() / "clawos/blackboard/shared/risk-limits.json").read_text()
        ).get("immutable", [])
        return rule_id in immutable

    def save_violation_log(self, path: Optional[Path] = None) -> None:
        """Save violation log to file"""
        if path is None:
            path = Path.home() / "clawos/blackboard/shared/violations/violations.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.violation_log, f, indent=2)


# Singleton instance for SDK integration
_controller_instance = None


def get_risk_controller() -> RiskController:
    """Get singleton RiskController instance"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = RiskController()
    return _controller_instance


def validate_action(agent_id: str, action: str, context: dict = None) -> tuple:
    """SDK convenience function for action validation"""
    if context is None:
        context = {}
    return get_risk_controller().validate_action(agent_id, action, context)


def get_allowed_nodes(agent_id: str) -> list:
    """SDK convenience function for getting allowed nodes"""
    return get_risk_controller().get_allowed_nodes(agent_id)


if __name__ == "__main__":
    # Test the risk controller
    logging.basicConfig(level=logging.INFO)

    rc = RiskController()

    # Test alpha-isolation rule
    print("Testing alpha-isolation rule...")
    allowed, reason = rc.validate_action(
        "alpha-executor", "execute-trade", {"targetNode": "local"}
    )
    print(f"  Local node: allowed={allowed}, reason={reason}")

    allowed, reason = rc.validate_action(
        "alpha-executor", "execute-trade", {"targetNode": "quant"}
    )
    print(f"  Quant node: allowed={allowed}, reason={reason}")

    # Test trading limits
    print("\nTesting trading-limits rule...")
    print(
        f"  Allowed nodes for alpha-executor: {rc.get_allowed_nodes('alpha-executor')}"
    )

    # Test immutability
    print("\nTesting immutability...")
    print(f"  alpha-isolation immutable: {rc.is_rule_immutable('alpha-isolation')}")
    print(f"  cost-limit immutable: {rc.is_rule_immutable('cost-limit')}")

    print("\nViolation log:", rc.violation_log)
