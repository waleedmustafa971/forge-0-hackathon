"""Routes agent tasks to two providers, e.g. Muse Spark 1.3 for reasoning and Muse Spark Open for volume.

The primary provider handles every task except those listed for the secondary. Each completion
keeps the provider and model that actually produced it, so per-call accounting stays exact.
"""

from __future__ import annotations

from typing import Any

from providers.base import AgentRequest, AIProvider, Completion, T


class RoutingProvider(AIProvider):
    def __init__(self, primary: AIProvider, secondary: AIProvider, tasks: frozenset[str]) -> None:
        self.primary = primary
        self.secondary = secondary
        self.tasks = tasks
        self.name = f"{primary.name}+{secondary.name}"[:40]
        self.model = f"{primary.model} + {secondary.model}"[:120]
        self.simulated = primary.simulated or secondary.simulated

    def route(self, task: str) -> AIProvider:
        return self.secondary if task in self.tasks else self.primary

    def generate(self, request: AgentRequest, schema: type[T]) -> Completion[T]:
        return self.route(request.task).generate(request, schema)

    def check(self, deep: bool = False) -> dict[str, Any]:
        primary = self.primary.check(deep)
        secondary = self.secondary.check(deep)
        return {
            "provider": self.name,
            "model": self.model,
            "ok": bool(primary.get("ok")) and bool(secondary.get("ok")),
            "primary": primary,
            "secondary": {**secondary, "tasks": sorted(self.tasks)},
        }

    def describe(self) -> dict[str, Any]:
        return {
            **super().describe(),
            "routing": {
                "primary": self.primary.describe(),
                "secondary": {**self.secondary.describe(), "tasks": sorted(self.tasks)},
            },
        }
