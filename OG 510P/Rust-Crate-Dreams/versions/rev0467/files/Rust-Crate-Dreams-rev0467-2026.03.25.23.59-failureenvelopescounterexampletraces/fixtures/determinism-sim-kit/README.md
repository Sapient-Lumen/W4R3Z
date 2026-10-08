# Deterministic Simulation Kit fixtures

These fixtures exist to make **P-0104 Deterministic Simulation Kit** look buildable instead of merely aspirational.

The receiver-facing question is:

> what files should another maintainer receive in order to understand which deterministic ingredients were controlled, which backend produced the run, what fault/scenario plan was in effect, and whether the failure can be replayed or minimized?

## Minimal pack for 0.1

- `sim-profile.schema.json` — run/profile identity, chosen backend adapter, deterministic lanes in scope, and redaction defaults.
- `backend-capability.receipt.schema.json` — what the backend can honestly control, what remains unsupported, and whether the run is comparable to other backends.
- `fault-plan.schema.json` — topology and injected failures that materially shaped the run.
- `schedule-transcript.report.schema.json` — seed, time advances, schedule token/decisions, major events, and failure site.
- `minimization.report.schema.json` — how a failing scenario was reduced and whether the minimized run stayed comparable.
- `simrun-bundle-manifest.schema.json` — the compact entry index for a portable `simrun@1` bundle.

## Design rules

- Keep **scheduler**, **time**, **randomness**, **fault**, and **external-I/O** lanes explicit.
- Preserve backend truth instead of flattening `tokio-paused`, `turmoil`, `madsim`, `shuttle`, and `loom` into one fake “deterministic mode”.
- Treat **not comparable** and **manual-review-required** as honest outputs.
- Start from a **single-thread deterministic core** claim unless a backend receipt proves more.
- Reuse the shared bundle substrate from **P-0256 Evidence Bundle Core Kit** rather than inventing a forever-one-off zip format.

## Intended first scenarios

1. `tokio_paused_time_timer_race` — a Tokio-first run where paused time and a deterministic schedule token reproduce a timeout-sensitive failure without any simulated network lane.
2. `turmoil_partition_then_repair` — a multi-host turmoil-backed run with a seeded partition/repair sequence, transcript export, and a minimized replay summary.
