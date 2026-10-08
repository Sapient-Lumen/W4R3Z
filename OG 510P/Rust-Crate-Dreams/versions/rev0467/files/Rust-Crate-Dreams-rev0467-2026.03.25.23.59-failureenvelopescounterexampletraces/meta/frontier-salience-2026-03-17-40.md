# Frontier salience snapshot — 2026-03-17 (40)

This pass promoted a new cross-cutting crate lane:

- **P-0525 Crate Diagnosis Surface Pack Kit** — because the archive still had no good receiver-facing artifact for the ordinary question that arrives right after “the crate runs” but before “the crate crashed”: *what symptoms does this crate officially recognize, what should I inspect first, and what evidence should I capture?*

## Main judgment

The next worthy crate in the supportiveness frontier was **not** another debugger, telemetry stack, or support portal.
Those pieces already exist in partial form.
The sharper missing layer is the **crate-authored contract** for troubleshooting support:

- official symptom catalogs,
- self-check manifests,
- signal-to-symptom maps,
- remediation classes,
- safe support-capture bundles,
- and release-to-release diffs of that surface.

That move is now better grounded because:

- the Rust vision-doc explicitly argues for more supportive interfaces from crates,
- the 2025 State of Rust survey says debugging still matters while docs and code remain the main learning surfaces,
- the 2026 Rust debugging survey says Rust still needs stronger support across debuggers, operating systems, async debugging, visualizers, and expression evaluation,
- Tokio’s tracing guidance and `tracing` already provide structured diagnostics substrate,
- tokio-console / `console-subscriber` already provide one strong async debugging path,
- `metrics` already gives libraries a common metrics façade,
- and `tokio-metrics` already exposes runtime and task metrics.

So the gap is no longer “Rust has no diagnostics”.
The gap is that crates still rarely publish a **reviewable troubleshooting / symptom / self-check contract** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0525 Crate Diagnosis Surface Pack Kit** — strongest cross-domain troubleshooting-support artifact now missing.
2. **P-0484 Toolchain & Target Support Contract Kit** — still one of the sharpest practical support-truth lanes for real users on real machines.
3. **P-0451 Cfg Availability Ledger Kit** — still a deeply leverageful way to make portability and conditional API truth reviewable.
4. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than full diagnosis support.
5. **P-0121 FFI Boundary & Bindings Conformance Kit** — still a high-value bridge for Rust↔foreign adoption.
6. **P-0197 Text Layout Conformance Kit** — still a large missing boring default outside Cargo-heavy work.
7. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — still a standout domain-specific workbench with very real ecosystem pain.

## Why this won over adjacent candidates right now

- It beat **more observability follow-ons** because signal emission without symptom/self-check/remediation structure still leaves users guessing.
- It beat **more debugger-specific follow-ons** because many reports are “the system is weird” problems before a debugger-specific workflow even begins.
- It beat **runtime-handoff follow-ons** because a great deal of ecosystem pain is steady-state diagnosis rather than crash-only failure.
- It beat several strong **toolchain/docs/FFI/domain** candidates because this lane multiplies value across almost every crate family rather than one domain at a time.

## What changed in the archive

Added:
- `proposals/crate-diagnosis-surface-pack-kit.md`
- `meta/crate-diagnosis-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-40.md`
- `entries/2026-03-17-211.md`
- `fixtures/crate-diagnosis-surface-pack-kit/`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- failure-path guidance,
- runtime failure handoff,
- observability signal contracts,
- debugger / symbol / visualizer posture,
- downstream testing support,
- and receiver-facing diagnosis-surface contracts

into one fake “better Rust debugging” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://tokio.rs/tokio/topics/tracing
- https://docs.rs/console-subscriber/latest/console_subscriber/
- https://docs.rs/tracing/latest/tracing/
- https://docs.rs/metrics/latest/metrics/
- https://docs.rs/tokio-metrics/latest/tokio_metrics/
