# Cargo tool-workflow coverage boundaries — 2026-03-08

Purpose: keep **P-0494 Cargo Compile-Time-Deps Workflow Kit** narrow and receiver-facing as it becomes more implementation-ready around selection coverage and workspace invocation truth.

## What changed in the substrate

The current rust-analyzer and Cargo docs make three support boundaries explicit enough to model:

1. rust-analyzer documents `cargo.allTargets = true` by default, and `check.allTargets` inherits it unless overridden.
2. Cargo documents `--all-targets` as a real expansion to `--lib --bins --tests --benches --examples`, which means target-class coverage is a named boundary rather than vague “editor completeness.”
3. rust-analyzer documents `check.workspace`, `{label}`, `per_workspace`, and `once`, which means package scope and working-directory rules are part of the observed workflow truth.

Issue reports make this concrete instead of hypothetical:
- `allTargets = false` can leave a dev-dependency proc-macro unavailable in analysis,
- and `check.workspace = false` can still leak broader diagnostics on first startup.

## What P-0494 should provide now

A worthy **P-0494** bundle should now be able to export:

- one `selection-coverage.report.json`,
- one `workspace-invocation.receipt.json`,
- and conservative verdicts when package scope, target-class coverage, or startup behavior are not exact.

The report should be allowed to say:
- “workspace policy expected package-only diagnostics, but startup leakage widened the observed set,”
- “`allTargets = false` removed test/example/dev-dependency-bearing lanes,”
- “proc-macro availability is missing because the relevant lane was not selected,”
- and “linked-project invocation ran once from the opened project, so per-workspace parity is not exact.”

## What this proposal is not

### Not a rust-analyzer bug tracker clone
The crate may capture startup leakage and coverage holes as **support truth**, but it should not become a giant issue-mirroring database or promise to fix rust-analyzer itself.

### Not a universal target graph enumerator
The crate should freeze the parts of selection and coverage that matter for support handoff. It should not try to become a replacement for Cargo’s target graph, metadata, or future build planning APIs.

### Not another “build correctness” claim
Coverage honesty is exactly the point. If the tool run omitted tests, benches, examples, dev-dependencies, or proc-macro lanes, the bundle should say so and stop there.

## Concrete boundary rules

1. Keep **selection scope**, **target-class coverage**, and **workspace invocation topology** separate.
2. Treat startup leakage or ambiguous first-run behavior as first-class `manual_review_required` input, not as noise to normalize away.
3. Record whether `allTargets`, `check.workspace`, `{label}`, and invocation strategy changed the observed run shape.
4. Keep proc-macro availability diagnosis attached to coverage facts, not just to generic “proc macro failed” wording.
5. Prefer small conservative artifacts over big inferred dashboards.

## Sources

- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build command docs: https://doc.rust-lang.org/cargo/commands/cargo-build.html
- rust-analyzer issue #18528: https://github.com/rust-lang/rust-analyzer/issues/18528
- rust-analyzer issue #17126: https://github.com/rust-lang/rust-analyzer/issues/17126
