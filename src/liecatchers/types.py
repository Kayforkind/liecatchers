from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Verdict = Literal["pass", "fail", "skip"]


@dataclass(frozen=True)
class SensorResult:
    name: str
    verdict: Verdict
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    status: Literal["production", "stub", "heuristic"] = "production"


@dataclass
class Contract:
    declared_paths: list[str] = field(default_factory=lambda: ["src/", "tests/"])
    declared_commands: list[str] = field(default_factory=lambda: ["pytest"])
    declared_suites: list[str] = field(default_factory=lambda: ["pytest"])
    native_deps: list[str] = field(default_factory=list)
