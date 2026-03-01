"""ClawOS GM Services - Federation routing and coordination"""

from .federation_router import FederationRouter, route_task, get_evolution_task

__all__ = ["FederationRouter", "route_task", "get_evolution_task"]
