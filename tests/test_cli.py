from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FAIL = ROOT / "fixtures" / "fail_demo"
CLEAN = ROOT / "fixtures" / "clean"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "liecatchers.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(SRC)},
    )


def test_sensor_registry_has_ten():
    from liecatchers.sensors import REGISTRY

    assert len(REGISTRY) == 10


def test_fail_demo_exits_one():
    proc = _run("run", "--fail-demo", "--no-write")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "fail" in proc.stdout.lower()


def test_fail_demo_writes_receipt(tmp_path: Path):
    # copy isn't needed — run on fixture with write
    proc = _run("run", "--fail-demo")
    assert proc.returncode == 1
    receipt = FAIL / "RECEIPT.json"
    assert receipt.is_file()
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert data["schema"] == "liecatcher.receipt.v1"
    assert data["aggregate"] == "fail"
    assert "done" in data["failures"]
    assert "amnesia" in data["failures"]
    from liecatchers.receipt import verify_signature

    assert verify_signature(data)


def test_clean_exits_zero():
    proc = _run("run", "--workdir", str(CLEAN))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads((CLEAN / "RECEIPT.json").read_text(encoding="utf-8"))
    assert data["aggregate"] == "pass"
    assert data["failures"] == []


def test_sensor_list():
    proc = _run("sensor", "list")
    assert proc.returncode == 0
    for name in (
        "done",
        "scope",
        "ghost",
        "hollow",
        "fanfic",
        "loose",
        "forged",
        "sneak",
        "theater",
        "amnesia",
    ):
        assert name in proc.stdout


def test_receipt_verify_after_run():
    _run("run", "--workdir", str(CLEAN))
    proc = _run("receipt", "verify", "--workdir", str(CLEAN))
    assert proc.returncode == 0
    assert "OK" in proc.stdout
