# Cursor stop-hook

Goal: when the agent tries to finish, run liecatchers and keep the receipt in the workspace.

## Minimal hook idea

In your project's Cursor hooks config, run:

```powershell
uv run --directory <repo> liecatcher run --workdir <project>
```

Use a non-zero exit to signal failure to your hook runner.

## Human trailer

For commits/pushes that agents perform, require:

```
Liecatchers-Human: true
```

in the commit message so the `forged` sensor can pass.

## Troubleshooting (Windows)

- Prefer `uv run` with absolute paths.
- If `git diff` is empty in fixtures, provide `.liecatcher/diff_paths.txt`.
- `RECEIPT.json` is written to `--workdir`, not necessarily the hook cwd.
