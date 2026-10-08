# Rust Engine (`gr_engine`) — determinism, durability, and testing hooks

## 9.1 Determinism contract
`gr_engine` MUST produce identical outputs given the same specs and seeds.

## 9.2 Chunk execution API (AFK support)
Rust MUST expose chunkable task execution:
- `run_task(task_key, specs, seed) -> ResultArtifact`

Task output MUST include:
- hash of inputs + engine version,
- summary stats,
- optional trace.

## 9.3 Atomic writes (required helpers)
Rust SHOULD ship helpers:
- `atomic_write(path, bytes)` (temp + fsync optional + rename),
- `fsync_dir(parent_dir)` optional.

## 9.4 Testing hooks (new, required)
The engine MUST make it easy to generate many small randomized scenarios.

### Property-based testing support (recommended)
The Rust crate SHOULD include property-based tests for:
- invariants (symmetry under player swap),
- determinism under same seed,
- cache key correctness (same inputs -> same artifact hash),
- boundedness (no NaNs; probabilities clamp; payoffs finite),
- “no orphan state” invariants in strategy state machines.

These tests can be implemented with a PBT framework (e.g., proptest) and should shrink failing cases.

### Metamorphic relations as tests (recommended)
Include a test harness to run metamorphic relations as:
- unit tests (small, quick),
- integration tests (CI).

## 9.5 Analytic/certificate calculations (optional)
For tractable classes, Rust MAY compute:
- transition matrices,
- stationary distributions,
- expected payoffs,
and emit analysis artifacts for cross-checking simulation.

## 9.6 If Rust spawns subprocesses
Avoid if possible. If needed:
- place subprocesses in cgroup/scope or process group,
- never daemonize.

## 9.7 Failure artifacts (must)
Every failure MUST emit:
- minimal reproducer,
- trace (when enabled),
- metric deltas,
- engine version/build hash.
