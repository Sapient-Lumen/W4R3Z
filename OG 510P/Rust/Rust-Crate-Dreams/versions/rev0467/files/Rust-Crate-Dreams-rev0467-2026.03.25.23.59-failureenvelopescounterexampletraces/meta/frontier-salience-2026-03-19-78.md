# Frontier salience snapshot — 2026-03-19 (78)

This pass did **not** add another shutdown framework, another task runtime, another structured-concurrency substrate, or another generic async helper.
It sharpened a top-ranked support-surface lane:

- **P-0520 Crate Lifecycle Surface Pack Kit** — because Rust now has real shutdown/cancellation/task-lifecycle substrate, but still lacks one boring receiver-facing contract for activation boundaries, stop-verb truth, blocking-work caveats, teardown evidence, and drain recipes.

## Main judgment

The next worthy move here was **not** more substrate.
That substrate already exists.

The sharper missing layer is the **joined lifecycle contract** above today’s substrate, especially once five facts stay explicit:

- **activation-boundary truth** — when background work really starts,
- **stop-verb truth** — what `drop`, `abort`, `cancel`, `close`, `shutdown`, `join`, and `detach` actually mean,
- **blocking-work truth** — where abort/cancel claims stop being strong enough,
- **teardown-evidence truth** — what proves cleanup completed rather than merely started,
- **drain-recipe truth** — what the supported graceful, timed, and hard-stop paths are.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- Tokio’s graceful-shutdown guide already frames shutdown as signal + propagate + wait;
- `CancellationToken` and `TaskTracker` already provide signal-and-wait substrate;
- Tokio documents that dropping a `JoinHandle` detaches the task and loses its output;
- Tokio documents that dropping a `JoinSet` aborts tracked tasks, while `JoinSet::shutdown()` aborts all tasks and waits for them to finish shutting down;
- Tokio’s `select!` and I/O docs already explain cancellation safety, partial progress, and `flush`/`shutdown` distinctions;
- `async_shutdown`, `tokio-graceful-shutdown`, `task_scope`, and `moro` already cover useful adjacent implementation slices.

So the gap is no longer “Rust lacks shutdown helpers”.
The gap is that teams still rarely get a **reviewable crate-authored lifecycle promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — now a stronger implementation-ready lane because the shutdown/cancellation substrate below it is real and the receiver-facing contract above it is still weak.
3. **P-0524 Crate Example Surface Pack Kit** — now a stronger first-success lane after the latest pass.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
5. **P-0521 Crate Resource Surface Pack Kit** — still a strong resource-support lane.
6. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
7. **P-0483 Public API Readiness Bundle Kit** — now a stronger joined release-review lane.
8. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
9. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
10. **P-0515 Crate Off-Ramp Pack Kit** — still a strong survivability / supportiveness follow-on.
11. **P-0071 MCP Guard Kit** — still a strong modern protocol/deployment-support lane.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0521** pass because the support stack still needed a more concrete answer for “how does this crate really start and stop?” before going further into resource promises.
- It beat a deeper **P-0519** pass because ambient powers matter, but current Tokio/task/I/O substrate makes lifecycle truth unusually buildable now.
- It beat another **foreign-package shipping** pass because the archive already had several fresh shipping-contract revisions and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because the ecosystem-choice lane is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen.

## What changed in the archive

Added:
- `entries/2026-03-19-258.md`
- `meta/frontier-salience-2026-03-19-78.md`
- `meta/crate-lifecycle-surface-product-plan-2026-03-19.md`
- `fixtures/crate-lifecycle-surface-pack-kit/join_handle_drop_detaches_background_task/stop-semantics.receipt.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/join_handle_drop_detaches_background_task/teardown-evidence.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/lazy_background_worker_starts_on_first_request/activation-boundary.policy.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/lazy_background_worker_starts_on_first_request/background-work.receipt.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/protocol_writer_requires_shutdown_not_drop/shutdown-obligation.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/protocol_writer_requires_shutdown_not_drop/teardown-evidence.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/streaming_writer/cancellation-surface.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/streaming_writer/race-retry-safety.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/watcher_subscription/stop-semantics.receipt.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/connection_pool_client/drain-recipe.manifest.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/connection_pool_client/lifecycle-check.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/spawn_blocking_abort_not_guaranteed/README.md`
- `fixtures/crate-lifecycle-surface-pack-kit/spawn_blocking_abort_not_guaranteed/stop-semantics.receipt.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/spawn_blocking_abort_not_guaranteed/teardown-evidence.report.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/joinset_shutdown_vs_detach_all/README.md`
- `fixtures/crate-lifecycle-surface-pack-kit/joinset_shutdown_vs_detach_all/stop-semantics.receipt.example.json`
- `fixtures/crate-lifecycle-surface-pack-kit/joinset_shutdown_vs_detach_all/drain-recipe.manifest.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-lifecycle-surface-pack-kit.md`
- `fixtures/crate-lifecycle-surface-pack-kit/README.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
