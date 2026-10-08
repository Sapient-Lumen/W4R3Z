# Crate Test Surface Pack Kit — isolation / reset boundaries (2026-03-20)

This note keeps **P-0523 Crate Test Surface Pack Kit** from blurring together several truths that current Rust test tooling now makes meaningfully different.

## Main judgment

The archive already had fixture catalogs, deterministic seams, topology manifests, environment requirements, and witness-lineage receipts.
The sharper follow-on move is to keep three more questions separate:

1. **isolation class** — whether each helper or scenario is fresh per call, fresh per test, process-shared, externally shared, or only safe because a runner gives each test a separate process;
2. **parallel-safety posture** — whether a workflow is safe under shared-process `cargo test`, only safe with serial execution, or only safe under a process-per-test runner such as nextest;
3. **reset / cleanup capability** — whether state disappears because the OS owns cleanup, because Drop runs, because an explicit reset API exists, because an external daemon is usually torn down, or because cleanup is best-effort only.

## Why this boundary matters now

Current official substrate makes this sharper than a generic “tests are isolated” claim:

- Rust's own testing docs say `cargo test` runs tests in parallel by default and warn against shared files or environment state.
- `std::env::set_var` is now unsafe outside single-threaded programs on non-Windows platforms, which turns environment mutation into an isolation claim.
- nextest's process-per-test model makes some mutation patterns safe there while remaining unsafe or at least much less honest to claim under `cargo test`.
- `wiremock` documents per-test `MockServer` creation for full isolation.
- `testcontainers` documents isolated integration tests with scope-based container cleanup.
- `tempfile` distinguishes OS cleanup from destructor-dependent cleanup.

## Keep these claims separate

### 1. Deterministic seam versus isolation class

A crate can have a deterministic clock seam or fake transport and still be process-shared, globally stateful, or only serial-safe.
Do not let “deterministic” stand in for “isolated”.

### 2. Environment requirement versus runner assumption

A scenario may only need loopback or tempdir access, yet still require nextest's process isolation or single-threaded execution to be honest.
Do not let “host capability available” stand in for “parallel-safe on the default runner”.

### 3. Cleanup mechanism versus reset guarantee

A temp file cleaned up by the OS, a temp dir deleted on Drop, a container removed when a handle goes out of scope, and an explicit reset API are not the same support promise.
Do not let “usually cleaned up” stand in for “fresh again for the next test”.

### 4. Witness lineage versus contamination risk

A direct run, portable replay, or compile-fail harness can prove that a scenario happened.
That does **not** prove the helper is contamination-safe under parallel execution.

## Working rule for future passes

When refining **P-0523**, prefer tiny artifacts such as `isolation-class.receipt` and `reset-capability.receipt` before inventing another neighboring test harness, mock framework, or CI replay lane.
