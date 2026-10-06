# Repro capsules (minimal reproducibility payloads)

A repro capsule is a small bundle that makes a failure reproducible without shipping secrets.

## Contents (v1)
- Spec/Lock/Plan snapshots (or their digests + retrieval pointers)
- builder recipe (jail base digest, toolchain digests)
- logs (structured JSONL)
- backend mapping outputs (e.g., generated bhyve_config)
- environment normalization settings (reproducibility knobs)

Optional attachments (policy-gated):
- `trace.capsule` digests (bounded observability evidence)
- `debug.replay.capsule` digests (record/replay traces for time-travel debugging)
- `time.snapshot` digests (time/entropy profile receipts for deterministic runs)
- `redaction.receipt` digests proving deterministic sanitization when exporting

## Non-goals
- secrets (never included)
- huge source trees (referenced by digest)

Capsules are the currency of:
- bug reports
- CI triage
- LLM-assisted debugging (generate fixes from capsule content)

See RFC-0020.
See also: `docs/194-debugging-by-lease-and-replay-capsules.md`, `docs/195-deterministic-redaction-transforms.md`, `docs/197-time-and-rng-authority.md`.

Last updated: 2026-02-24
