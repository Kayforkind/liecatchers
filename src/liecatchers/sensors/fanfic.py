from __future__ import annotations

import time

from liecatchers.context import SensorContext, extract_mentioned_paths
from liecatchers.types import SensorResult


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    sources = [
        (".liecatcher/PR.md", ctx.read_text(".liecatcher/PR.md")),
        (".git/COMMIT_EDITMSG", ctx.read_text(".git/COMMIT_EDITMSG")),
        ("COMMIT_EDITMSG", ctx.read_text("COMMIT_EDITMSG")),
    ]
    mentioned: set[str] = set()
    used_source = None
    for name, text in sources:
        if text:
            used_source = name
            mentioned |= extract_mentioned_paths(text)

    diff = ctx.git_diff_paths()
    fictional = sorted(p for p in mentioned if p not in diff and not p.startswith(".liecatcher/"))

    # If no message and no mentions, skip rather than false-fail
    if used_source is None:
        return SensorResult(
            name="fanfic",
            verdict="skip",
            reason="no PR.md / COMMIT_EDITMSG to inspect",
            evidence={"mentioned_paths": [], "diff_paths": sorted(diff)},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if fictional:
        return SensorResult(
            name="fanfic",
            verdict="fail",
            reason=f"message names paths not in the diff: {fictional}",
            evidence={
                "message_source": used_source,
                "mentioned_paths": sorted(mentioned),
                "diff_paths": sorted(diff),
                "fictional_paths": fictional,
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    return SensorResult(
        name="fanfic",
        verdict="pass",
        reason="mentioned paths are present in the diff",
        evidence={
            "message_source": used_source,
            "mentioned_paths": sorted(mentioned),
            "diff_paths": sorted(diff),
            "fictional_paths": [],
        },
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
