# liecatchers

> Your agent said "Done." Prove it.

Ten sensors. One `RECEIPT.json`. Zero API keys. Windows-first.

liecatchers runs after your coding agent claims completion and checks the claim against the real workspace — declared commands, git diff, lockfiles, native modules, handoff packets. If the agent lied, you get a machine-readable receipt you can paste back into the next turn.

```powershell
uvx --from . liecatcher run --fail-demo
```

[Install](#install-windows-60-seconds) · [Sensors](#the-10-sensors) · [Receipt](#receiptjson--the-one-source-of-truth) · [Cursor hook](#cursor-stop-hook) · [Docs](docs/)

---

## What it catches

Agents print **Done** while:

- tests never ran
- files appeared outside the agreed contract
- the PR invents paths that are not in the diff
- npm looks green but native bits are missing
- the next agent gets no structured handoff

liecatchers turns that into **exit code 1** plus a signed `RECEIPT.json`.

## 30-second fail-demo

From a clone on Windows PowerShell:

```powershell
cd D:\Projects\liecatchers   # or your clone path
uv sync --extra dev
uv run liecatcher run --fail-demo
echo $LASTEXITCODE
```

Expected: **exit code 1**, a table of FAIL/PASS/SKIP, and `fixtures/fail_demo/RECEIPT.json`.

Honest path (bundled clean fixture):

```powershell
uv run liecatcher run --workdir fixtures/clean
echo $LASTEXITCODE
```

Expected: **exit code 0**, `aggregate: pass`.

## Install (Windows, 60 seconds)

### Option A — from this repo (recommended while pre-PyPI)

```powershell
git clone https://github.com/kazimrmerchant/liecatchers.git
cd liecatchers
uv sync --extra dev
uv run liecatcher --version
```

### Option B — pip editable

```powershell
pip install -e ".[dev]"
liecatcher --version
```

Requires Python 3.11+. No API keys. No network calls at runtime.

## The 10 sensors

| Sensor | Catches | Day-1 |
|--------|---------|-------|
| `done` | Claimed Done but declared commands left no exit/junit evidence | production |
| `scope` | Diff paths outside `.liecatcher/contract.json` | production |
| `ghost` | Suite declared but no `junit.xml` / `.pytest_cache` | production |
| `hollow` | npm green while native bits (`sharp`, etc.) missing | production |
| `fanfic` | PR/commit text names paths not in the diff | production |
| `loose` | MCP/launch manifests use `@latest` / missing version | production |
| `forged` | commit/push/merge without `Liecatchers-Human: true` | production |
| `sneak` | lockfile hash drifted from `.liecatcher/baseline.lock` | production |
| `theater` | `mock.patch` targets the unit under test (heuristic) | heuristic |
| `amnesia` | missing `.liecatcher/handoff.json` for the next turn | production |

```powershell
uv run liecatcher sensor list
uv run liecatcher sensor describe done
```

## Quick start on your project

```powershell
uv run liecatcher init --workdir .
# edit .liecatcher/contract.json — declared_paths, declared_commands
uv run liecatcher run --workdir .
uv run liecatcher handoff --workdir . --next-goal "Review RECEIPT and continue"
uv run liecatcher receipt show --workdir .
uv run liecatcher receipt verify --workdir .
```

Exit codes: `0` pass · `1` any sensor failed · `2` CLI misuse.

## RECEIPT.json — the one source of truth

Written only by this CLI (not by the agent). Example shape:

```json
{
  "schema": "liecatcher.receipt.v1",
  "cli_version": "0.1.0",
  "aggregate": "fail",
  "failures": ["done", "ghost", "amnesia"],
  "sensors": [
    {
      "name": "done",
      "verdict": "fail",
      "reason": "claimed Done but declared commands never left artifacts: ['pytest']",
      "evidence": {},
      "status": "production"
    }
  ],
  "signature": "sha256:..."
}
```

If `aggregate != pass`, the agent lied (or the contract is wrong). Show the receipt to the agent.

Full field reference: [docs/receipt-schema.md](docs/receipt-schema.md).

## Cursor stop-hook

Add a project hook that refuses a clean stop until sensors pass. Example for Cursor hooks (adapt to your `hooks.json`):

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "uv run liecatcher run --workdir .",
        "timeout_ms": 60000
      }
    ]
  }
}
```

Details: [docs/cursor-hook.md](docs/cursor-hook.md).

Human git agency trailer (for `forged`):

```
Liecatchers-Human: true
```

## Why not nuhuh / DoneSpec / casper

- **nuhuh** — strong “re-run the claim” idea; liecatchers is a **named series of orthogonal sensors** with one receipt schema.
- **DoneSpec** — contract file focus; liecatchers adds scope/hollow/fanfic/forged/amnesia as first-class sensors.
- **casper** — Claude Code judgment toolkit; liecatchers is a small Windows-first CLI you can `uv run` without a host plugin.

## FAQ

- **Does it call OpenAI/Anthropic?** No. Zero network, zero keys.
- **macOS/Linux?** Should work; Windows is the primary test surface.
- **Will it block forever?** No. It prints a receipt and exits.
- **Can I add a sensor?** Yes — see [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/adding-a-sensor.md](docs/adding-a-sensor.md).

## License

MIT. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). AI-assisted patches are welcome if you can explain the diff and tests pass.
