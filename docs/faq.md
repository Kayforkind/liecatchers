# FAQ

**Does liecatchers call cloud LLMs?**  
No. It only reads the local workspace.

**What is a receipt?**  
A `RECEIPT.json` written by this CLI with per-sensor verdicts and a sha256 signature.

**Why did a sensor skip?**  
Missing inputs (no lockfile, no native deps, no PR message). Skip is not fail.

**How do I prove the demo works?**  
`uv run liecatcher run --fail-demo` must exit `1`.  
`uv run liecatcher run --workdir fixtures/clean` must exit `0`.
