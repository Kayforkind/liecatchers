from __future__ import annotations

from collections.abc import Callable

from liecatchers.context import SensorContext
from liecatchers.sensors import amnesia, done, fanfic, forged, ghost, hollow, loose, scope, sneak, theater
from liecatchers.types import SensorResult

SensorFn = Callable[[SensorContext], SensorResult]

REGISTRY: dict[str, SensorFn] = {
    "done": done.run,
    "scope": scope.run,
    "ghost": ghost.run,
    "hollow": hollow.run,
    "fanfic": fanfic.run,
    "loose": loose.run,
    "forged": forged.run,
    "sneak": sneak.run,
    "theater": theater.run,
    "amnesia": amnesia.run,
}

DESCRIPTIONS: dict[str, str] = {
    "done": "Claimed Done but declared commands never left exit/junit evidence",
    "scope": "Files appeared outside .liecatcher/contract.json declared_paths",
    "ghost": "Suite declared but no junit.xml / .pytest_cache",
    "hollow": "npm green while native bits (sharp/binding.gyp) missing",
    "fanfic": "PR/commit message names paths not in the git diff",
    "loose": "MCP/npm/pypi launch unpinned (@latest / missing version)",
    "forged": "commit/push/merge without Liecatchers-Human: true trailer",
    "sneak": "lockfile hash drifted from .liecatcher/baseline.lock",
    "theater": "coverage theater via mock.patch of the unit under test",
    "amnesia": "no structured .liecatcher/handoff.json for the next turn",
}


def list_sensors() -> list[tuple[str, str]]:
    return [(name, DESCRIPTIONS[name]) for name in REGISTRY]
