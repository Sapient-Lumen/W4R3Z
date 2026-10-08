# Pathfinder decision-pack scenario catalog — 2026-03-23

This note deepens **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** around the next missing product layer:
**named scenario packs that emit review packets**.

The archive already had:
- lane boundaries,
- starter-set readiness,
- elimination / re-entry,
- replay / freshness,
- support visibility,
- and decision-watch artifacts.

What it still lacked was the small catalog of scenarios that a real `cargo pathfinder` should ship first.

## Main judgment

A credible `0.1` should not open with a generic “find me the best Rust crates” prompt.
It should open with a small set of **scenario packs**.

Each scenario pack should do four things:
1. declare the roles it is trying to fill,
2. force constraints into the open,
3. emit a compact review packet,
4. record what would reopen the decision later.

## What every scenario pack should emit

Minimum packet:
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `decision-timebox.receipt.json`
- `as-of-replay.report.json`
- `revisit-trigger.policy.json`

Optional packet pieces:
- `scope-split.receipt.json`
- `starter-set-readiness.report.json`
- `support-visibility.report.json`
- `lockin-cost.report.json`
- `manual-review.note.md`

## Recommended first-pack catalog

### 1. `cli_baseline`
**User question:** “I need a sane baseline for a CLI app without weeks of crate churn.”

**Roles:** argument parsing, config, errors, logging, testing helpers, distribution support.

**Typical constraints:** newcomer-friendly, stable docs, low lock-in, common OS support.

**What it should give other people:**
- one teaching-oriented starter set,
- one production-oriented starter set if they differ,
- explicit loser reasons for obvious alternatives,
- a revisit rule when support or security signals change.

### 2. `async_backend_stack`
**User question:** “I need a production backend stack, but I want the choice documented, not folklore-driven.”

**Roles:** runtime, HTTP/service framework, persistence/client layers, observability, testing, graceful shutdown.

**Typical constraints:** async semantics, debugging posture, deployment environment, ecosystem maturity, lock-in cost.

**What it should give other people:**
- one stack choice packet,
- one concurrency/manual-review note,
- one explanation of the runtime-specific assumptions.

### 3. `desktop_gui_stack`
**User question:** “What should we pick for a desktop GUI app, and should teaching defaults differ from shipping defaults?”

**Roles:** UI framework, app lifecycle/state, diagnostics, packaging/update path, dev-loop expectations.

**Typical constraints:** compile-loop pain, debugger support, platform coverage, docs quality, shipping maturity.

**What it should give other people:**
- one teaching-vs-shipping split receipt when needed,
- one explanation of dev-loop and debug tradeoffs,
- one manual-review note for packaging or platform-specific gaps.

### 4. `wasm_component_plugin_stack`
**User question:** “How should we choose crates for a Wasm component/plugin system without confusing host, guest, and build-target truth?”

**Roles:** component generation/binding, host integration, packaging, feature gating, target support, docs surfaces.

**Typical constraints:** host-vs-target separation, target maturity, docs.rs target visibility, runtime packaging differences.

**What it should give other people:**
- one plugin/component starter set,
- one host-target support packet,
- one explicit note on what is still unresolved or manual.

### 5. `embedded_no_std_edge_stack`
**User question:** “What stack fits a constrained device or edge system without pretending normal desktop/server assumptions still apply?”

**Roles:** allocator posture, HAL/driver ecosystem, async-if-any, logging/diagnostics, testing route, support target story.

**Typical constraints:** `no_std`, target toolchains, build-std, memory budgets, native prerequisites.

**What it should give other people:**
- one constrained-environment starter set,
- one note on target / linker / build prerequisites,
- one dependency-risk packet for long-lived devices.

### 6. `mixed_language_interop_stack`
**User question:** “Should we use wrappers, generators, or binding tools, and what does that imply for support and migration?”

**Roles:** FFI surface, ABI/toolchain support, build integration, native prerequisites, testing/documentation route.

**Typical constraints:** language boundary shape, native toolchains, generator lock-in, packaging, auditability.

**What it should give other people:**
- one interop decision packet,
- one wrapper-vs-generator loser receipt,
- one support-boundary and migration note.

### 7. `local_first_sync_stack`
**User question:** “What should we pick for storage, sync, and transport in a local-first system without collapsing durability, merge, and transport into one decision?”

**Roles:** local persistence, sync/replication, transport, conflict semantics, review/repair tooling.

**Typical constraints:** offline operation, conflict visibility, merge model, auditability, portability.

**What it should give other people:**
- one storage/sync/transport split packet,
- one manual-review note around merge semantics,
- one re-entry policy if the ecosystem shifts quickly.

## Command shape

A plausible command surface:

```text
cargo pathfinder scenario run async_backend_stack   --constraints constraints.toml   --freeze-window 30d   --emit decision-brief,starter-set,replay,revisit
```

Related commands:
- `cargo pathfinder scenario list`
- `cargo pathfinder scenario explain desktop_gui_stack`
- `cargo pathfinder replay --as-of 2026-03-23`
- `cargo pathfinder doctor packet ./decision-pack/`

## Review-packet shape

A scenario packet should be readable by at least three audiences:

1. **the adopter** — “what should we pick?”
2. **the reviewer** — “why did the obvious alternatives lose?”
3. **the future maintainer** — “what would reopen this choice?”

That means every packet should be short enough to read and structured enough to diff.

## Refusal boundaries

A scenario pack must not:
- claim timeless “best crate” authority,
- hide sector constraints inside opaque scores,
- treat docs visibility as runnable support,
- silently resurrect previously excluded candidates,
- or flatten host/target/toolchain/build surfaces into one fake compatibility badge.

## New fixture scenarios added this pass

To make this more concrete, the archive now adds four new pathfinder scenario stubs:
- `fixtures/crate-ecosystem-pathfinder-kit/desktop_gui_teaching_vs_shipping_stack/README.md`
- `fixtures/crate-ecosystem-pathfinder-kit/wasm_component_plugin_host_target_split/README.md`
- `fixtures/crate-ecosystem-pathfinder-kit/mixed_language_cpp_wrapper_vs_binding_generator/README.md`
- `fixtures/crate-ecosystem-pathfinder-kit/local_first_sync_transport_storage_split/README.md`

These are still fixture stubs, not full schemas.
That is intentional: the repo should test which scenario packs are most worth productizing before adding more artifact surface.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
