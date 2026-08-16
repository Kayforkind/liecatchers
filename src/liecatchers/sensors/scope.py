from __future__ import annotations

import time

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    diff = ctx.git_diff_paths()
    out_of_scope = sorted(
        p for p in diff if not ctx.path_matches(p, ctx.contract.declared_paths)
    )
    if out_of_scope:
        return SensorResult(
            name="scope",
            verdict="fail",
            reason=f"{len(out_of_scope)} path(s) outside declared contract",
            evidence={
                "declared_paths": ctx.contract.declared_paths,
                "diff_paths": sorted(diff),
                "out_of_scope": out_of_scope,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="scope",
        verdict="pass",
        reason="diff is within declared_paths",
        evidence={
            "declared_paths": ctx.contract.declared_paths,
            "diff_paths": sorted(diff),
            "out_of_scope": [],
        },
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
