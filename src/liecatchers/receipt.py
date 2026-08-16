from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from liecatchers import SCHEMA, __version__
from liecatchers.types import SensorResult


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign_payload(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_receipt(
    *,
    workdir: Path,
    results: list[SensorResult],
    contract: dict[str, Any] | None = None,
    git: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failures = [r.name for r in results if r.verdict == "fail"]
    sensors = [
        {
            "name": r.name,
            "verdict": r.verdict,
            "reason": r.reason,
            "evidence": r.evidence,
            "duration_ms": r.duration_ms,
            "status": r.status,
        }
        for r in results
    ]
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "cli_version": __version__,
        "os": __import__("sys").platform,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workdir": str(workdir.resolve()),
        "git": git or {},
        "contract": contract or {},
        "sensors": sensors,
        "aggregate": "fail" if failures else "pass",
        "failures": failures,
    }
    payload["signature"] = sign_payload(
        {k: v for k, v in payload.items() if k != "signature"}
    )
    return payload


def write_receipt(workdir: Path, receipt: dict[str, Any]) -> Path:
    path = workdir / "RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path


def verify_signature(receipt: dict[str, Any]) -> bool:
    expected = receipt.get("signature")
    if not expected:
        return False
    body = {k: v for k, v in receipt.items() if k != "signature"}
    return sign_payload(body) == expected
