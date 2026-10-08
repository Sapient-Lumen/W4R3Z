# Architecture (current + intended)

Concord is built as a deterministic scientific toolchain: easy to iterate, hard to misinterpret, and safe to interrupt.

## Components

- `crates/gr_engine` (Rust)
  - deterministic simulation core
  - bounded, interpretable strategy execution (Stage 1–2: builtins + memory-one; later: FSM + GRDSL)
  - structured artifacts + stable hashes
  - testing hooks for determinism, metamorphic checks, and shrinking (Stage 2+)
- `grlab` (Python)
  - orchestration (experiments, search loops, reporting)
  - AFK safety (durable queue + atomic chunk commits + kill guarantees) (Stage 3)
  - definition hygiene (registries + snapshot hashes + defdiff) (Stage 2)

## “Tests are artifacts”

The long-run goal is for probes/suites/scorecards to be versioned inputs to the engine and always visible in reports.

Stage 1 intentionally keeps this minimal (single `TaskSpec` → single `MatchArtifact`) so the system can grow without losing determinism.

See `docs/DEFINITIONS.md` for the definition/versioning workflow.

## Artifact model (Stage 1)

- Input: `TaskSpec` JSON (world + strategies + seeds + trace config)
- Output: `MatchArtifact` JSON
  - engine version
  - input hash
  - seeds/streams used
  - summary metrics + optional trace
