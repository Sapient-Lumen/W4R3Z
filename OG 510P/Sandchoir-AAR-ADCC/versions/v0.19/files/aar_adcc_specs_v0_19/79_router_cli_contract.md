# 79 — Router CLI Contract (Machine-Usable) (v0.19)

MetaLLM ergonomics live or die on a stable CLI. The Gearbox UI can be a thin wrapper over this.
Design principle: **every command has a human mode and a JSON mode**.

## 1) Command groups
### State + views
- `state show [--json]`
- `telemetry show [--agent A1] [--window 10] [--json]`
- `view render --agent A1 [--profile normal|emergency] [--json]`
- `view diff --agent A1 --since-cursor 123 [--json]`
- `ws list --type C|P|E|CE|T|SUM|CFG|EXEC [--json]`
- `ledger open <ID>` (prints pointer/path; full blobs live on disk)

### Control levers
- `mode get|set <Normal|Gatekeeper|PatchOnly|Freeze|Recovery> [--json]`
- `budget get|set <profile> [--json]`
- `weights get|set A1=2.0 A2=0.7 ... [--json]`
- `explore get|set discovery=0|1 random=0|1 [--json]`
- `integrator get|set <A?> [--json]`
- `select patch <P#>|none [--json]`
- `select ce <CE#>|none [--json]`

### Evidence/execution
- `verifier list [--json]`
- `verifier run <name> [--timeout cheap|medium|expensive] [--json]`
- `exec run <EXEC#> [--json]`

### Objects + requests
- `req add <REQ_JSON>` (or `req add --file req.json`)
- `req list|close ... [--json]`
- `cfg apply <CFG#> [--json]`
- `compact now [--json]`

### Threads + checkpoints
- `thread list|open|fork|close ... [--json]`
- `snapshot create [--label "..."] [--json]`
- `snapshot restore <SNAP#> [--json]`
- `checkpoint list|restore ... [--json]`

### Experiments
- `exp create <EXP_JSON> [--json]`
- `exp run <EXP#> [--json]`
- `exp status <EXP#> [--json]`
- `exp report <EXP#> [--json]`

## 2) Output contracts
### JSON mode
- single JSON object per command
- includes:
  - `ok` boolean
  - `cursor` current cursor
  - `result` payload (object/array)
  - `warnings` array
  - `errors` array

### Human mode
- compact, stable formatting; never dumps large blobs.

## 3) Exit codes
- 0 ok
- 2 user error
- 3 recoverable runtime error
- 4 corrupted state / invariant violation (forces Recovery)

## 4) MetaLLM pattern
MetaLLM should call:
- `telemetry show` and `view diff` first (cheap)
Then choose one:
- `mode set`
- `compact now`
- `verifier run`
- `select patch`
Only rarely:
- `weights set` (prefer human approval)

## 5) Back-compat
- CLI is versioned: `router --version` prints kernel + schema versions.
- CLI flags are additive; breaking changes require a new major protocol version.
