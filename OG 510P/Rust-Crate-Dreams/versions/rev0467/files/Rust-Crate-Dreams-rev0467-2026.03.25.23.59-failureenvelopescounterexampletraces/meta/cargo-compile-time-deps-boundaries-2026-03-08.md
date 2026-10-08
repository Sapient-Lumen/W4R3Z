# Cargo compile-time-deps workflow boundaries — 2026-03-08

Purpose: keep **P-0494 Cargo Compile-Time-Deps Workflow Kit** narrow and receiver-facing as it becomes more implementation-ready.

## Main judgment

The missing crate is not another editor integration layer.
It is a **support bundle** for tool-facing Cargo workflows with two especially important truths frozen explicitly:

1. **comparison-baseline truth** — what is this run being compared against?
2. **override-command truth** — what command actually ran and how was it resolved?

## Current upstream substrate

Cargo and rust-analyzer now expose enough surface that these truths are no longer hidden implementation details:

- Cargo documents `--compile-time-deps` as permanently unstable and tool-oriented.
- RFC 3477 keeps `cargo build` as the stronger correctness surface.
- rust-analyzer documents `check.overrideCommand` and `cargo.buildScripts.overrideCommand` as first-class config.
- rust-analyzer documents that override commands must emit JSON.
- rust-analyzer documents that `{label}` changes behavior toward package-scoped checking.
- rust-analyzer documents `cargo.targetDir` as a real trade-off: less lock contention, more duplicated artifacts.
- rust-analyzer documents `cargo.buildScripts.useRustcWrapper = true` by default for build scripts.

## What P-0494 should provide

A good 0.1 should now hand other people:

- one `tool-build.receipt.json`,
- one `compile-surface.manifest.json`,
- one `parity-check.report.json`,
- one `fallback.plan.json`,
- one `comparison-baseline.lock`,
- and one `override-command.receipt.json`.

## What must stay out of scope

### Not P-0490
Do not turn P-0494 into a contention or wait artifact.
If the question is “who blocked whom on which cache root?”, that is **P-0490**.

### Not P-0489
Do not turn P-0494 into a build-dir internals migration kit.
If the question is “which tool scrapes Cargo internals and will break under layout change?”, that is **P-0489**.

### Not a wrapper framework
Do not turn P-0494 into a new universal command wrapper, IDE extension, or build-system bridge.
The value is the **receipt and comparison lock**, not owning execution for every environment.

## High-value boundaries to freeze

### 1. Comparison baseline
Every parity claim should say whether it is:

- `tool_vs_tool`,
- `tool_vs_full_build`,
- `tool_vs_terminal_build`,
- or `tool_vs_policy`.

Without this, the bundle will quietly overclaim equivalence.

### 2. Selection scope
The bundle should capture whether the observed command was:

- workspace-wide,
- package-scoped,
- label-scoped,
- target-filtered,
- or otherwise narrowed.

This is especially important when `{label}` or custom override commands are used.

### 3. Override provenance
The bundle should record:

- check override command,
- build-script override command,
- whether they were paired,
- placeholder use (`{label}`, `{saved_file}`),
- JSON-output expectations,
- command-path resolution mode (plain name / absolute / relative / wrapper),
- and wrapper hints such as rust-analyzer’s build-script wrapper behavior.

### 4. Honest fallback zones
The crate should prefer:

- `full_build_required`,
- `build_script_cfg_risk`,
- or `manual_review_required`

instead of inventing false equivalence.

## Common false gap patterns to resist

1. “The editor used Cargo, so the result is basically a build.”
2. “A custom override command worked once, so its provenance does not matter.”
3. “Selection drift is just configuration noise.”
4. “Target-dir separation explains the whole problem.”

## Sources

- Cargo unstable docs (`compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- RFC 3477 (`cargo check` policy): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- rust-analyzer issue #10793 (relative override command): https://github.com/rust-lang/rust-analyzer/issues/10793
- rust-analyzer issue #5962 (custom build script override / VFS mismatch): https://github.com/rust-lang/rust-analyzer/issues/5962
- esp-idf-sys issue #113 (toolchain-specific buildScripts override): https://github.com/esp-rs/esp-idf-sys/issues/113
