from __future__ import annotations

import time
from pathlib import Path

from liecatchers.context import SensorContext, load_contract
from liecatchers.receipt import build_receipt, write_receipt
from liecatchers.sensors import REGISTRY
from liecatchers.types import SensorResult


def run_sensors(
    workdir: Path,
    names: list[str] | None = None,
    *,
    write: bool = True,
    fail_demo: bool = False,
) -> tuple[list[SensorResult], dict]:
    workdir = workdir.resolve()
    contract = load_contract(workdir)
    ctx = SensorContext(
        workdir=workdir,
        run_start=time.time(),
        contract=contract,
        fail_demo=fail_demo,
    )
    selected = names or list(REGISTRY.keys())
    results: list[SensorResult] = []
    for name in selected:
        if name not in REGISTRY:
            raise KeyError(f"unknown sensor: {name}")
        results.append(REGISTRY[name](ctx))

    receipt = build_receipt(
        workdir=workdir,
        results=results,
        contract={
            "declared_paths": contract.declared_paths,
            "declared_commands": contract.declared_commands,
            "declared_suites": contract.declared_suites,
            "native_deps": contract.native_deps,
        },
    )
    if write:
        write_receipt(workdir, receipt)
    return results, receipt
