# RECEIPT.json schema (`liecatcher.receipt.v1`)

| Field | Type | Meaning |
|-------|------|---------|
| `schema` | string | Must be `liecatcher.receipt.v1` |
| `cli_version` | string | CLI version that wrote the receipt |
| `os` | string | `sys.platform` |
| `generated_at` | string | UTC timestamp |
| `workdir` | string | Absolute workspace path |
| `git` | object | Optional local git summary |
| `contract` | object | Declared paths/commands/suites/native_deps |
| `sensors` | array | Per-sensor verdict, reason, evidence, status |
| `aggregate` | `pass` \| `fail` | `fail` if any sensor failed |
| `failures` | string[] | Names of failing sensors |
| `signature` | string | `sha256:` of canonical JSON excluding this field |

Only the `liecatcher` CLI writes receipts. Agents must not author them.
