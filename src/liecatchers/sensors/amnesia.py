from __future__ import annotations

import time

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

REQUIRED = ("next_goal", "artifacts", "open_questions", "receipt_ref")


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    path = ctx.liecatcher_dir() / "handoff.json"
    if not path.is_file():
        return SensorResult(
            name="amnesia",
            verdict="fail",
            reason="no .liecatcher/handoff.json for the next agent turn",
            evidence={
                "handoff_path": str(path),
                "handoff_present": False,
                "missing_keys": list(REQUIRED),
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    data = ctx.load_json(".liecatcher/handoff.json") or {}
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        return SensorResult(
            name="amnesia",
            verdict="fail",
            reason=f"handoff.json missing keys: {missing}",
            evidence={
                "handoff_path": str(path),
                "handoff_present": True,
                "missing_keys": missing,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="amnesia",
        verdict="pass",
        reason="structured handoff packet present",
        evidence={
            "handoff_path": str(path),
            "handoff_present": True,
            "missing_keys": [],
        },
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
