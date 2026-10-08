# Frontier salience snapshot — 2026-03-17 (42)

This pass did **not** promote a new lane.
It sharpened an existing high-ranked cross-cutting proposal:

- **P-0520 Crate Lifecycle Surface Pack Kit** — because the archive still lacked a good release-grade artifact for the ordinary maintainer question that sits between “Tokio and friends give us shutdown primitives” and “our release review can actually reason about startup, stop, and cleanup truth”: *what starts background work, what do stop verbs really do, and what evidence do we have that teardown actually finished?*

## Main judgment

The next worthy move in this frontier was **not** another runtime, another structured-concurrency experiment, another graceful-shutdown helper, or another async style guide.
Those pieces already exist in partial form.

The sharper missing layer is the **lifecycle surface contract** above them:

- activation-boundary policy,
- background-work receipts,
- stop-semantics receipts,
- shutdown-obligation reports,
- teardown-evidence reports,
- drain recipes,
- and release-to-release lifecycle diffs.

That move is now better grounded because:

- the Rust vision-doc explicitly argues for more supportive interfaces from crates,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces,
- Tokio’s shutdown guide already frames graceful shutdown as signal, broadcast, and wait,
- `CancellationToken` and `TaskTracker` already provide signal-and-wait substrate,
- `JoinHandle` and `AbortHandle` already separate detach, abort permission, and join semantics,
- `spawn_blocking` explicitly documents that running blocking tasks cannot be aborted,
- `select!` already documents cancellation safety as “drop and recreate without losing progress”,
- and Tokio’s write/shutdown docs already distinguish cancel-safe writes from `write_all` / protocol-shutdown paths that need stronger care.

So the gap is no longer “Rust has no async lifecycle primitives”.
The gap is that maintainers still rarely publish a **reviewable activation / stop / teardown contract** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0520 Crate Lifecycle Surface Pack Kit** — now one of the clearest implementation-ready cross-cutting lanes for steady-state task and shutdown truth.
2. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest support-truth lanes for real users on real machines.
3. **P-0451 Cfg Availability Ledger Kit** — still a highly leverageful way to make conditional API truth reviewable.
4. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than the full lifecycle support contract.
5. **P-0121 FFI Boundary & Bindings Conformance Kit** — still a high-value bridge for Rust↔foreign adoption.
6. **P-0197 Text Layout Conformance Kit** — still a large missing boring default outside Cargo-heavy work.
7. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — still a standout domain-specific workbench with very real ecosystem pain.

## Why this won over adjacent candidates right now

- It beat **more diagnosis follow-ons** because ordinary startup / stop / cleanup truth still precedes many troubleshooting bundles.
- It beat **more observability follow-ons** because signal emission does not answer what background work a crate keeps alive or how to stop it cleanly.
- It beat **more structured-concurrency follow-ons** because substrate alone does not create a receiver-facing support contract.
- It beat several strong **FFI/domain** candidates because this lane multiplies value across clients, streams, workers, watchers, and service crates rather than one domain at a time.

## What changed in the archive

Added:
- `meta/crate-lifecycle-surface-product-plan-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-42.md`
- `entries/2026-03-17-221.md`
- `fixtures/crate-lifecycle-surface-pack-kit/activation-boundary.policy.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/stop-semantics.receipt.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/teardown-evidence.report.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/lazy_background_worker_starts_on_first_request/`
- `fixtures/crate-lifecycle-surface-pack-kit/join_handle_drop_detaches_background_task/`
- `fixtures/crate-lifecycle-surface-pack-kit/protocol_writer_requires_shutdown_not_drop/`

Updated:
- `proposals/crate-lifecycle-surface-pack-kit.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- runtime failure handoff,
- observability contracts,
- authority posture,
- setup/configuration scenarios,
- graceful-shutdown frameworks,
- structured-concurrency substrate,
- and receiver-facing lifecycle-surface contracts

into one fake “better async shutdown” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://tokio.rs/tokio/topics/shutdown
- https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
- https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
- https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- https://docs.rs/tokio/latest/tokio/macro.select.html
- https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- https://docs.rs/tokio/latest/tokio/io/trait.AsyncWrite.html
- https://docs.rs/async-shutdown/latest/async_shutdown/
- https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
- https://docs.rs/task_scope/latest/task_scope/
- https://docs.rs/crate/moro/0.4.0
