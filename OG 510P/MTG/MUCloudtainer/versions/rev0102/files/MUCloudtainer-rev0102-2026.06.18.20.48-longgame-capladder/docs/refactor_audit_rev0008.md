# rev0008 refactor and audit notes

## Refactor performed

### 1. Separated safe and fast action application

Before:

```text
apply_action always recomputed legal_actions
```

After:

```text
apply_action(..., validate=True)   # safe default
apply_action(..., validate=False)  # trusted hot path
```

### 2. Added optional engine logging

Before:

```text
all games built text logs
```

After:

```text
record_log=True   # debugging, gametable, transcripts
record_log=False  # payoff tables, profiling, learning rollouts
```

### 3. Added population-payoff module

New:

```text
src/muc5/payoff.py
```

This keeps payoff construction out of scripts and makes strategy bundles importable by future PSRO/evolution/neural experiments.

### 4. Added throughput module

New:

```text
src/muc5/perf.py
```

This keeps performance measurement reusable and auditable.

## Audit checks added

`scripts/audit_cube.py` now verifies:

```text
rev0008 payoff game rows = 256
rev0008 payoff aggregate rows = 128
rev0008 profile summary exists
rev0008 cProfile output exists
benchmark helper returns positive throughput
rev0008 default strategy population has 8 bundles
rev0008 required files exist
```

Inherited checks still cover:

```text
deck-space row count
probe table stability
life-total feature visibility
mulligan policy/agent plumbing
card conservation
rev0007 gametable artifacts
rev0007 sparring probe
```

## Validation command set

```bash
python -m pytest -q
python scripts/run_rev0008_payoff_table.py
python scripts/profile_simulator_rev0008.py
python scripts/audit_cube.py
```

## Known caveat

`record_log=False` suppresses text logs, so payoff rows have `log_events = 0`. This is intentional for high-throughput evaluation. Use gametable/replay/debug modes for transcript-quality game logs.
