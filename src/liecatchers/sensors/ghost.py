from __future__ import annotations

import time

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    suites = ctx.contract.declared_suites
    junit = ctx.workdir / "junit.xml"
    cache = ctx.workdir / ".pytest_cache"
    found: dict[str, object] = {
        "junit_exists": junit.is_file(),
        "pytest_cache_exists": cache.exists(),
    }
    if junit.is_file():
        found["junit_mtime"] = junit.stat().st_mtime

    needs_pytest = any(s.lower().startswith("pytest") for s in suites)
    if needs_pytest and not junit.is_file() and not cache.exists():
        return SensorResult(
            name="ghost",
            verdict="fail",
            reason="suite was declared but no junit.xml / .pytest_cache from this process",
            evidence={
                "declared_suites": suites,
                "found_artifacts": found,
                "run_start": ctx.run_start,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="ghost",
        verdict="pass",
        reason="suite artifacts present for declared suites",
        evidence={"declared_suites": suites, "found_artifacts": found},
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
