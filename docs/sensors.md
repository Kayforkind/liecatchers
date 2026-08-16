# Sensors

See the README table for the one-line summary. Each sensor returns `pass`, `fail`, or `skip` with an `evidence` object.

| Name | Inputs | Fail when |
|------|--------|-----------|
| done | `.liecatcher/claim.json`, `exit_codes.json`, `junit.xml` | Claimed Done without command artifacts |
| scope | `diff_paths.txt` or `git diff`, `contract.json` | Diff outside declared_paths |
| ghost | contract suites, junit / pytest_cache | Suite declared, artifacts missing |
| hollow | `package.json`, `node_modules/<dep>` | Native dep declared, bits missing |
| fanfic | PR.md / COMMIT_EDITMSG vs diff | Mentioned path not in diff |
| loose | launch.json / mcp.json | `@latest` or missing version |
| forged | claim events + commit message | Agency without `Liecatchers-Human: true` |
| sneak | lockfiles vs `baseline.lock` | Hash drift |
| theater | `test_*.py`, coverage.json | Heuristic same-unit mock.patch |
| amnesia | `.liecatcher/handoff.json` | Missing packet or keys |

Ignore pragma (planned): `# liecatcher-ignore` — not in v0.1.
