# 78 — CTRLJSON Schema + WS Object Schemas (v0.19)

Schematize the *control plane* so that repair + validation are cheap and reliable.

## 1) CTRLJSON minimal schema
Required:
- `agent` (string)
Optional:
- `done` (bool)
- `votes` (object, sparse)
- `propose` (object)
- `req` (object)
- `notes` (array of short strings)

Constraints:
- unknown keys rejected (or quarantined)
- string lengths capped
- votes are top-K sparse and clamped 0..5
- arrays capped (e.g., notes <= 5)

## 2) WS object families (high level)
- C# claim
- P# patch proposal
- E# evidence
- CE# counterexample
- T# task
- SUM# summary/compaction
- CFG# config proposal
- EXEC# execution request
- LEASE# (implicit or explicit lease event)

Each object has:
- `id`
- `type`
- `status`
- `title`
- `body` (bounded fields)
- `refs`

## 3) Why schema matters
- enables strict parsing without retries
- makes malicious/injected text less likely to contaminate the control plane
- makes golden tests easy (61_)

## 4) Implementation notes
- JSON Schema or a Rust struct + serde validation is sufficient.
- The schema can evolve via versioning rules (50_/60_).
