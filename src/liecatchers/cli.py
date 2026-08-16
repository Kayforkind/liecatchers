from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from liecatchers import __version__
from liecatchers.runner import run_sensors
from liecatchers.sensors import DESCRIPTIONS, REGISTRY, list_sensors

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
FAIL_DEMO = PACKAGE_ROOT / "fixtures" / "fail_demo"
CLEAN_DEMO = PACKAGE_ROOT / "fixtures" / "clean"


def _print_table(results) -> None:
    print(f"LIECATCHERS v{__version__}")
    print(f"{'sensor':<12} {'verdict':<8} reason")
    print("-" * 72)
    for r in results:
        print(f"{r.name:<12} {r.verdict:<8} {r.reason}")
    fails = [r.name for r in results if r.verdict == "fail"]
    skips = [r.name for r in results if r.verdict == "skip"]
    passes = [r.name for r in results if r.verdict == "pass"]
    print("-" * 72)
    print(
        f"{len(fails)} fail, {len(passes)} pass, {len(skips)} skip"
        + (f" — failures: {', '.join(fails)}" if fails else "")
    )


def cmd_run(args: argparse.Namespace) -> int:
    if args.fail_demo:
        workdir = FAIL_DEMO
        if not workdir.is_dir():
            print(f"fail-demo fixture missing: {workdir}", file=sys.stderr)
            return 2
    else:
        workdir = Path(args.workdir).resolve()

    names = args.sensors or None
    try:
        results, receipt = run_sensors(
            workdir,
            names,
            write=not args.no_write,
            fail_demo=bool(args.fail_demo),
        )
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        _print_table(results)
        if not args.no_write:
            print(f"\nWrote {(workdir / 'RECEIPT.json')}")

    return 1 if receipt.get("aggregate") == "fail" else 0


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.workdir).resolve()
    d = root / ".liecatcher"
    d.mkdir(parents=True, exist_ok=True)
    contract = {
        "declared_paths": ["src/", "tests/"],
        "declared_commands": ["pytest"],
        "declared_suites": ["pytest"],
        "native_deps": [],
    }
    path = d / "contract.json"
    path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    print("Edit declared_paths / declared_commands, then run: liecatcher run")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    root = Path(args.workdir).resolve()
    d = root / ".liecatcher"
    d.mkdir(parents=True, exist_ok=True)
    packet = {
        "next_goal": args.next_goal or "Continue from the last verified receipt",
        "artifacts": args.artifacts or ["RECEIPT.json"],
        "open_questions": args.open_questions or [],
        "receipt_ref": "RECEIPT.json",
    }
    path = d / "handoff.json"
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


def cmd_sensor(args: argparse.Namespace) -> int:
    if args.sensor_cmd == "list":
        for name, desc in list_sensors():
            print(f"{name:<12} {desc}")
        return 0
    if args.sensor_cmd == "describe":
        name = args.name
        if name not in REGISTRY:
            print(f"unknown sensor: {name}", file=sys.stderr)
            return 2
        print(f"{name}\n{DESCRIPTIONS[name]}")
        return 0
    return 2


def cmd_receipt(args: argparse.Namespace) -> int:
    root = Path(args.workdir).resolve()
    path = root / "RECEIPT.json"
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    if args.receipt_cmd == "show":
        print(json.dumps(data, indent=2))
        return 0
    if args.receipt_cmd == "verify":
        from liecatchers.receipt import verify_signature

        ok = verify_signature(data)
        print("signature: OK" if ok else "signature: INVALID")
        return 0 if ok else 1
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="liecatcher",
        description="Your agent said Done. Prove it.",
    )
    p.add_argument("--version", action="version", version=f"liecatchers {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run sensors and write RECEIPT.json")
    run.add_argument("sensors", nargs="*", help="Sensor names (default: all)")
    run.add_argument("--workdir", default=".", help="Workspace root")
    run.add_argument(
        "--fail-demo",
        action="store_true",
        help="Run against bundled fixtures/fail_demo (must exit 1)",
    )
    run.add_argument("--no-write", action="store_true", help="Do not write RECEIPT.json")
    run.add_argument("--json", action="store_true", help="Print receipt JSON")
    run.add_argument("--quiet", action="store_true", help="Reserved")
    run.set_defaults(func=cmd_run)

    init = sub.add_parser("init", help="Write .liecatcher/contract.json")
    init.add_argument("--workdir", default=".")
    init.set_defaults(func=cmd_init)

    handoff = sub.add_parser("handoff", help="Write .liecatcher/handoff.json")
    handoff.add_argument("--workdir", default=".")
    handoff.add_argument("--next-goal", default=None)
    handoff.add_argument("--artifacts", nargs="*", default=None)
    handoff.add_argument("--open-questions", nargs="*", default=None)
    handoff.set_defaults(func=cmd_handoff)

    sensor = sub.add_parser("sensor", help="List or describe sensors")
    sensor_sub = sensor.add_subparsers(dest="sensor_cmd", required=True)
    sensor_sub.add_parser("list").set_defaults(func=cmd_sensor)
    describe = sensor_sub.add_parser("describe")
    describe.add_argument("name")
    describe.set_defaults(func=cmd_sensor)

    receipt = sub.add_parser("receipt", help="Show or verify RECEIPT.json")
    receipt_sub = receipt.add_subparsers(dest="receipt_cmd", required=True)
    show = receipt_sub.add_parser("show")
    show.add_argument("--workdir", default=".")
    show.set_defaults(func=cmd_receipt)
    verify = receipt_sub.add_parser("verify")
    verify.add_argument("--workdir", default=".")
    verify.set_defaults(func=cmd_receipt)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
