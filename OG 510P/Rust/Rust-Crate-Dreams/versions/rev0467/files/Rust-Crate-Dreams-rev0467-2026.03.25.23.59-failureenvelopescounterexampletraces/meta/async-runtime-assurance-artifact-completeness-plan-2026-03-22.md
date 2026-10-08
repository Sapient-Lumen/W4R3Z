# Async runtime assurance artifact-completeness plan — 2026-03-22

This note deepens **P-0532 Async Runtime Assurance Profile Kit** around one product question:

> What should another engineer actually receive when a crate or product team claims a runtime choice is understood, reviewed, or qualification-ready?

## Product stance

The crate should remain **read-first, reviewer-facing, and conservative**.
It should not become:

- a runtime abstraction layer,
- a benchmark harness,
- a shutdown helper,
- or a full assurance-case system.

Its job is to emit a compact pack that answers:

- which runtime/concurrency model is in play,
- what shutdown and blocking semantics matter,
- what evidence class backs the claim,
- how runtime posture changed across revisions,
- and where host/test/runtime lanes diverge from target/runtime lanes.

## New first-class artifacts

### `qualification-basis.receipt.json`

For each reviewed lane, record:

- subject / lane identifier,
- primary runtime family,
- `claim_basis` (`documentation_only`, `documentation_plus_metrics`, `documentation_plus_on_target_measurement`, `imported_assurance_artifact`, `mixed`, `manual_review_required`),
- `target_scope` (`host_only`, `board_or_rtos_specific`, `mixed_host_and_target`, `manual_review_required`),
- imported evidence references,
- open assumptions,
- manual-review zones,
- notes on instrumentation availability versus real target exercise.

This keeps “Tokio has metrics” separate from “this product target was actually measured”.

### `runtime-profile-diff.report.json`

When comparing two captures, record:

- subject,
- old/new bundle references,
- which axes changed (`runtime_family`, `scheduler_model`, `allocation_posture`, `preemption_posture`, `timer_authority`, `blocking_posture`, `qualification_basis`, `shutdown_behavior`),
- whether the change is `runtime_model_changed`, `evidence_class_changed`, `support_meaning_changed`, `manual_review_required`,
- review notes.

This keeps “same runtime, better evidence” separate from “different runtime model now”.

### `runtime-assurance-bundle.manifest.json`

For one exported pack, record:

- subject,
- lane entries,
- required artifacts,
- optional/imported artifacts,
- host-vs-target separation notes,
- manual-review gaps,
- redaction or sharing posture.

This should be the thing another reviewer actually opens first.

## Receiver-facing workflow

### `capture`
Import runtime profile, shutdown behavior, and qualification basis.

### `check`
Flag claims that overreach evidence, such as:

- docs-only lane claiming target-qualified posture,
- mixed host/target stack flattened into one runtime profile,
- shutdown summary that hides `spawn_blocking` aftermath,
- static embedded executor labeled the same as thread-pool runtime.

### `diff`
Highlight whether the main change was runtime choice, shutdown behavior, or evidence class.

### `pack`
Emit one `runtime-assurance-bundle.manifest.json` plus the underlying receipts.

## Good first scenario families

1. **Tokio docs + metrics still do not make on-target qualification claims.**
2. **Embassy no-`alloc` / static-task profile is still mostly docs-derived until board-specific evidence is imported.**
3. **Tokio → Embassy or Tokio → RTIC is runtime-model drift, not a tiny evidence update.**
4. **Mixed host Tokio + target Embassy projects need a joined bundle with distinct lanes.**

## Boundary reminders

Keep P-0532 separate from:

- full lifecycle support contracts (**P-0520**),
- resource and budget topology (**P-0521**),
- toolchain/target support posture (**P-0484**),
- and system-level assurance argumentation (**P-0503**).

The value here is the **joined runtime-support artifact** above current runtime docs and below a full assurance workbench.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
- https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- https://docs.rs/tokio-metrics/latest/tokio_metrics/
- https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html
- https://docs.embassy.dev/embassy-executor/git/std/index.html
- https://docs.embassy.dev/embassy-executor/0.5.1/
- https://rtic.rs/2/book/en/by-example/app.html
- https://rtic.rs/2/book/en/monotonic_impl.html
