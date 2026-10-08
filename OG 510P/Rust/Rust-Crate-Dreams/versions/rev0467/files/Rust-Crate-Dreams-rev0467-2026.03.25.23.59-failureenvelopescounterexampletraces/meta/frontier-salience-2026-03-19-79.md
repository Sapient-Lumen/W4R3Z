# Frontier salience snapshot — 2026-03-19 (79)

This pass did **not** add another queue, another pool, another cache, another rate limiter, or another profiling stack.
It sharpened a top-ranked support-surface lane:

- **P-0521 Crate Resource Surface Pack Kit** — because Rust now has real queue/pool/cache/permit/runtime substrate, but still lacks one boring receiver-facing contract for admission order, backlog ownership, capacity shrink, acquire fate, and pressure evidence.

## Main judgment

The next worthy move here was **not** more substrate.
That substrate already exists.

The sharper missing layer is the **joined resource contract** above today’s substrate, especially once five facts stay explicit:

- **admission-path truth** — which limit, queue, pool, or layer decides first,
- **backlog-ownership truth** — whether waiting work is owned by the crate, upstream, downstream, or an external peer,
- **capacity-shrink truth** — what can permanently or temporarily reduce effective capacity,
- **acquire-fate truth** — whether callers wait, time out, error, or wake closed at the boundary,
- **pressure-evidence truth** — which metrics and receipts actually support the claim.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces, and resource usage remains a visible productivity problem;
- Tokio documents that unbounded `mpsc` channels can buffer arbitrarily and may abort the process if memory is exhausted;
- Tokio documents that `spawn_blocking` reaches a configured thread upper limit and then queues more work;
- Tokio `Semaphore` documents wait-for-permit behavior, while `SemaphorePermit::forget` can reduce available permits;
- Tower documents that `buffer` and `concurrency_limit` change effective in-flight counts depending on layer order;
- SQLx documents fair `Pool::acquire()` waiting and graceful `Pool::close()` behavior;
- Deadpool documents closure semantics that immediately wake current and future waiters with `PoolError::Closed`.

So the gap is no longer “Rust lacks capacity primitives”.
The gap is that teams still rarely get a **reviewable crate-authored resource promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0521 Crate Resource Surface Pack Kit** — now a stronger implementation-ready lane because the substrate below it is real and the receiver-facing contract above it is still weak.
4. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
5. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
6. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
7. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.
8. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest adoption-trust lanes.
9. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
10. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
11. **P-0515 Crate Off-Ramp Pack Kit** — still a strong survivability / supportiveness follow-on.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0519** pass because the support stack still needed a more concrete answer for “where does work actually wait and who owns that waiting room?” before going further into ambient-power review.
- It beat a deeper **P-0522** pass because durable-byte promises matter, but today’s queue/pool/permit/layer-order substrate makes resource truth unusually buildable right now.
- It beat more **foreign-package shipping** work because the archive already has several fresh shipping-contract revisions and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because the ecosystem-choice lane is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen.

## What changed in the archive

Added:
- `entries/2026-03-19-259.md`
- `meta/frontier-salience-2026-03-19-79.md`
- `meta/crate-resource-surface-product-plan-2026-03-19.md`
- `fixtures/crate-resource-surface-pack-kit/README.md`
- `fixtures/crate-resource-surface-pack-kit/admission-path.report.schema.json`
- `fixtures/crate-resource-surface-pack-kit/backlog-ownership.receipt.schema.json`
- `fixtures/crate-resource-surface-pack-kit/capacity-shrink.report.schema.json`
- `fixtures/crate-resource-surface-pack-kit/acquire-fate.report.schema.json`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_buffer_before_concurrency_limit/README.md`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_buffer_before_concurrency_limit/admission-path.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_buffer_before_concurrency_limit/resource-budget.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_concurrency_limit_before_buffer/README.md`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_concurrency_limit_before_buffer/admission-path.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/servicebuilder_concurrency_limit_before_buffer/resource-budget.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/semaphore_forget_reduces_effective_capacity/README.md`
- `fixtures/crate-resource-surface-pack-kit/semaphore_forget_reduces_effective_capacity/capacity-shrink.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/semaphore_forget_reduces_effective_capacity/reclaim-obligation.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/sqlx_pool_waits_fairly_and_close_wakes_waiters/README.md`
- `fixtures/crate-resource-surface-pack-kit/sqlx_pool_waits_fairly_and_close_wakes_waiters/acquire-fate.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/sqlx_pool_waits_fairly_and_close_wakes_waiters/reclaim-obligation.report.example.json`
- `fixtures/crate-resource-surface-pack-kit/tower_concurrency_limit_upstream_backlog_external/backlog-ownership.receipt.example.json`
- `fixtures/crate-resource-surface-pack-kit/tower_concurrency_limit_upstream_backlog_external/admission-path.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-resource-surface-pack-kit.md`
- `fixtures/crate-resource-surface-pack-kit/tower_concurrency_limit_upstream_backlog_external/README.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
