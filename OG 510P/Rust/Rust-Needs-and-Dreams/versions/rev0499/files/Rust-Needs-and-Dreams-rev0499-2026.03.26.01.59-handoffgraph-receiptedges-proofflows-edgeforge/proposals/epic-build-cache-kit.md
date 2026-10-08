# Epic Proposal: Build Cache Kit (Build-state topology, lock clarity, reuse truth)

## One-sentence pitch
Give Rust one reviewable build-state boundary over directory topology, lock scope, cache-entry identity, reuse verdicts, and exchange/retention policy so Cargo’s new build-dir layout and future user-wide caches become explainable instead of magical.

## Why this is worthy
This is an ecosystem-shaping contribution because it sits exactly where several major Rust efforts are converging:
- Cargo is actively redesigning build-dir layout around smaller units and finer-grained locking.
- Cargo already documents `build-dir` and `target-dir` as distinct public-facing concepts.
- rust-analyzer still needs a dedicated target-dir escape hatch to avoid blocking on Cargo.
- user-wide and CI-friendly caching are explicit project goals.

If the ecosystem does **not** establish a portable review boundary here, those improvements will still arrive — but as hidden implementation details scattered across Cargo internals, editor settings, CI wrappers, and cache services.

That would repeat a classic Rust tooling failure mode: real power, weak attachability.

## Deliverables
This epic should now be read as part of the shared **Build-State Evidence Stack**; see [`design/build-state-evidence-stack.md`](../design/build-state-evidence-stack.md) and [`design/build-state-evidence-pilot-program.md`](../design/build-state-evidence-pilot-program.md). The stack order is cache/layout truth → change-impact truth → diagnosis truth.

### Schemas / artifact family
- `build-state-subject/v0`
- `build-layout-report/v0`
- `build-lock-report/v0`
- `cache-entry-report/v0`
- `reuse-verdict-report/v0`
- `cache-retention-policy/v0`
- `cache-exchange-profile/v0`
- `build-state-pack/v0`

### Reference tooling
- `cargo cache layout`
- `cargo cache lanes`
- `cargo cache locks`
- `cargo cache entries`
- `cargo cache reuse`
- `cargo cache gc`
- `cargo cache exchange`
- `cargo cache pack`

### Integrations
- Cargo build-dir / target-dir adapters
- rust-analyzer coexistence adapter
- optional `sccache` and CI cache-lane adapters
- optional `cargo-chef` / container-layer adapters
- issue/CI attachment recipes for `build-state-pack/v0`

### Lane map and pilot program
Read this epic together with [`design/build-cache-lane-map.md`](../design/build-cache-lane-map.md) and [`design/build-cache-pilot-program.md`](../design/build-cache-pilot-program.md). The epic now explicitly distinguishes Cargo-native workspace-local state, editor-private duplication, Cargo-native user-wide intermediates, compiler-wrapper caches, container recipe/layer caching, and CI/plugin exchange.

## Example theory-to-practice scenarios
### 1. Editor contention
A team reports that `cargo run` blocks whenever rust-analyzer saves a file.
The kit should produce:
- a `build-layout-report` showing shared directories,
- a `build-lock-report` showing which lock domain blocked,
- and a `reuse-verdict-report` showing whether rust-analyzer duplication-by-policy would have avoided contention.

### 2. Cross-workspace dependency reuse
A developer keeps rebuilding the same dependencies across many repos.
The kit should show:
- which units are eligible for a user-wide lane,
- which are still workspace-local,
- and which were rejected because toolchain/features/inputs differ.

### 3. CI cache precision
A CI pipeline restores a giant blob cache but still rebuilds half the graph.
The kit should distinguish:
- blob restore success,
- actual entry availability,
- reuse rejections,
- and upload/download waste caused by the coarse cache model.

### 4. GC safety
A workstation has hundreds of GB of build state.
The kit should support a dry-run policy that shows:
- which entries are old,
- which are pinned by active workspaces,
- which are editor-private or user-wide,
- and what would be pruned without risking active lanes.

## Distinctness from nearby ideas
This epic is **not**:
- a replacement for `sccache`,
- a remote-cache SaaS,
- a build-performance diagnosis layer,
- a workspace-discovery or build-plan schema,
- or a compile-time sandbox.

It is the missing **persistence / topology / reuse** layer in between them.

## Milestones
### M0 — vocabulary and fixtures
- stabilize minimal v0 schemas
- define reason-code taxonomy
- collect example lock/contention and duplication fixtures

### M1 — Cargo-native topology adapter
- emit layout + lock + entry identity from current Cargo-facing surfaces
- support explicit `build-dir` / `target-dir` distinctions
- prove useful on normal Cargo workspaces first

### M2 — coexistence + user-wide pilots
- rust-analyzer coexistence reports
- shared-cache / user-wide-lane experiments
- retention-policy dry-run support

### M3 — exchange adapters
- CI blob-cache comparison mode
- optional remote/plugin-style exchange profiles
- attachable issue/PR evidence packs

### M4 — convergence with upstream work
- align with Cargo build-dir relayout progress
- align with finer-grained lock evolution
- remain adapter-friendly so proven pieces can migrate upstream later

## Non-goals
- Freezing Cargo internals prematurely
- Claiming all rebuilds are avoidable
- Treating editor-private duplication as always bad
- Collapsing trust/policy questions for remote caches into a mere cache-hit metric
- Replacing Build Doctor Kit’s diagnosis or Compile-Time Capabilities Kit’s authority model

## Why now
- Rust Project Goals — Rework Cargo Build Dir Layout: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Inside Rust — Cargo 1.93 target-dir locking / build-dir split: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo Book — Build Cache (`target-dir`, `build-dir`, artifact classes): https://doc.rust-lang.org/cargo/reference/build-cache.html
- rust-analyzer book — `cargo.targetDir`: https://rust-analyzer.github.io/book/configuration
- Rust Project Goals — User-wide build cache: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

## Strategic outcome
If this succeeds, “Rust build cache” stops meaning “whatever happens inside `target/` plus some wrappers.”
It becomes a real, reviewable substrate that upstream Cargo, IDEs, CI systems, and cache providers can all build on without trapping users inside opaque behavior.
