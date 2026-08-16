from __future__ import annotations

import time

from liecatchers.context import SensorContext
from liecatchers.types import SensorResult

TRAILER = "Liecatchers-Human: true"


def run(ctx: SensorContext) -> SensorResult:
    started = time.perf_counter()
    events = (ctx.load_json(".liecatcher/claim.json") or {}).get("events") or []
    message = (
        ctx.read_text(".git/COMMIT_EDITMSG")
        or ctx.read_text("COMMIT_EDITMSG")
        or ctx.read_text(".liecatcher/COMMIT_EDITMSG")
        or ""
    )
    has_trailer = TRAILER.lower() in message.lower()

    risky = [e for e in events if str(e).lower() in {"commit", "push", "merge"}]
    if not risky and not message:
        return SensorResult(
            name="forged",
            verdict="skip",
            reason="no commit/push/merge events to inspect",
            evidence={"events": events, "trailer_present": False},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if risky and not has_trailer:
        return SensorResult(
            name="forged",
            verdict="fail",
            reason=f"git agency events {risky} without '{TRAILER}' trailer",
            evidence={
                "events": events,
                "trailer_present": False,
                "message_preview": message[:200],
            },
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    if message and not has_trailer and risky:
        # already handled
        pass

    if message and not has_trailer and not risky:
        # bare message without events — treat as advisory pass if no agency claimed
        return SensorResult(
            name="forged",
            verdict="pass",
            reason="no push/merge/commit events claimed without human trailer",
            evidence={"events": events, "trailer_present": has_trailer},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    return SensorResult(
        name="forged",
        verdict="pass",
        reason="human trailer present for agency events",
        evidence={"events": events, "trailer_present": has_trailer},
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
