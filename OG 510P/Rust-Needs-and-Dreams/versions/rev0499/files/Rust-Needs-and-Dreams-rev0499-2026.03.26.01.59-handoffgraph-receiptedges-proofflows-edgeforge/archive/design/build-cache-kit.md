# Design: Build Cache Kit (`cargo cache`, build-state topology, reuse evidence)

## Goal
Turn Rust build caching from a mix of directory folklore, wrapper-specific behavior, and lock-contention workarounds into a **reviewable build-state substrate**.

This kit should make five things explicit:
1. **what build-state units exist**,
2. **where they live**,
3. **who can lock or reuse them**,
4. **why reuse or duplication happened**,
5. **how retention / exchange policy acted on them**.

It should bridge:
- Cargo’s evolving build-dir layout and finer-grained locking,
- rust-analyzer/editor coexistence workarounds,
- local/user-wide/CI/remote cache lanes,
- and build-diagnosis tooling that needs real reuse evidence.

This is **not** just a remote cache project.
It is the shared contract that makes future Cargo-native caching, editor behavior, CI cache plugins, and workspace-local diagnostics legible to one another.

## Why now
Fresh upstream signals all point the same way:
- The 2025h2 Cargo build-dir-layout goal explicitly says the current build cache is hard to break into smaller units, leading to whole-cache locking; it names reduced rust-analyzer contention, fine-grained locking, a first-class user-wide cache, and plugin-based remote-cache read/write as the future target.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo 1.93 says build-dir-layout work is already being paired with finer-grained locking and with a conceptual split between intermediate build state and final artifact state.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The Cargo Book now publicly documents both `target-dir` and `build-dir`, plus the split between final and intermediate artifacts.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- rust-analyzer already exposes a dedicated `cargo.targetDir` workaround specifically to reduce lock contention, but calls out the tradeoff: duplicated build artifacts.
  https://rust-analyzer.github.io/book/configuration
- The user-wide-cache goal frames cross-workspace reuse and more precise CI caching as strategic requirements, not edge cases.
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

Taken together, that means the next missing ecosystem contribution is not “help Cargo cache more.”
It is “make Cargo’s build state, lock scope, and reuse decisions **portable and inspectable**.”

## Core artifact family

### 1. `build-state-subject/v0`
Identity for the build-state domain being discussed:
- workspace / package selection
- toolchain identity
- target triple(s)
- profile / command class (`check`, `build`, `clippy`, `test`, etc.)
- host/target posture
- workspace root and configured `target-dir` / `build-dir`

### 2. `build-layout-report/v0`
Declares the relevant directory topology and unit organization:
- final-artifact dir(s)
- intermediate build dir(s)
- local vs shared vs user-wide classes
- unit segmentation model (package/hash/unit lane if known)
- path-canonicalization / redaction rules
- known unsupported/native/opaque regions

### 3. `build-lock-report/v0`
Makes contention explainable:
- lock domains
- lock holders / contenders
- command classes involved
- blocked-vs-parallelizable verdict
- reason codes such as:
  - `WHOLE_DIR_LOCK`
  - `ARTIFACT_DIR_LOCK_ONLY`
  - `BUILD_UNIT_LOCK`
  - `EDITOR_DUPLICATED_BY_POLICY`
  - `UNSAFE_SHARED_STATE`
  - `UNKNOWN_EXTERNAL_CONTENTION`

### 4. `cache-entry-report/v0`
Portable record of a potentially reusable unit:
- subject reference
- unit identity and producing lane
- normalized key ingredients (toolchain/profile/features/flags/inputs)
- scope class (`workspace-local`, `user-wide`, `editor-private`, `ci-remote`)
- freshness / retention metadata
- attachments or pointers to artifacts/metadata

### 5. `reuse-verdict-report/v0`
Explains a reuse decision:
- candidate entry references
- verdict: `REUSED`, `REBUILT`, `DUPLICATED_BY_POLICY`, `REJECTED_AS_STALE`, `REJECTED_AS_INCOMPATIBLE`, `REJECTED_AS_UNSAFE`, `INCONCLUSIVE`
- reason codes:
  - `TOOLCHAIN_MISMATCH`
  - `FEATURE_RESOLUTION_CHANGED`
  - `BUILD_SCRIPT_INPUTS_UNTRACKED`
  - `PROC_MACRO_INPUTS_UNTRACKED`
  - `LOCK_SCOPE_CONFLICT`
  - `PATH_SENSITIVITY`
  - `LAYOUT_SEGMENTATION_MISSING`
  - `REMOTE_POLICY_FORBIDS_WRITE`
  - `EDITOR_ISOLATION_POLICY`

### 6. `cache-retention-policy/v0`
Policy over stored build-state units:
- size/age/LRU thresholds
- workspace pinning
- final-artifact vs intermediate-artifact retention differences
- “do not prune active editor lane” / “keep last successful CI import” rules
- dry-run outcome summaries

### 7. `cache-exchange-profile/v0`
Models movement between cache lanes:
- local ↔ user-wide
- local ↔ editor-private
- local ↔ CI remote
- read/write permissions and trust posture
- import/export granularity
- redaction/provenance rules

### 8. `build-state-pack/v0`
Attachable bundle containing:
- one `build-state-subject`
- one `build-layout-report`
- optional `build-lock-report`
- zero or more `cache-entry-report`s
- zero or more `reuse-verdict-report`s
- optional retention / exchange policy attachments
- optional raw Cargo/rust-analyzer/CI traces

## Reference UX
A reference implementation could expose:
- `cargo cache layout` — print or emit `build-layout-report/v0`
- `cargo cache locks` — explain contention and emit `build-lock-report/v0`
- `cargo cache entries` — inspect reusable units across local/shared lanes
- `cargo cache reuse` — explain why a unit reused, rebuilt, or duplicated
- `cargo cache gc --policy ...` — preview/apply `cache-retention-policy`
- `cargo cache exchange` — inspect or simulate CI/user-wide/editor exchange lanes
- `cargo cache pack` — emit `build-state-pack/v0`

## Theory of change
The important design move is to separate **layout**, **locking**, **entry identity**, **reuse verdict**, **retention/exchange policy**, and now also **cache lane identity**.

That separation matters because today’s Rust build-cache pain is often misdiagnosed:
- a “cache miss” may actually be an **isolation policy**,
- a “slow build” may really be **lock contention**,
- a “bad CI cache” may be a **blob-granularity problem**,
- a “rust-analyzer rebuild” may be a deliberate **target-dir split**,
- a “clean fixed it” story may hide **topology drift** rather than semantic invalidation.

If those truths stay flattened together, tooling will keep producing vague advice and opaque behavior.


## Lane map and pilot order
This kit should now be read together with:
- [`design/build-cache-lane-map.md`](./build-cache-lane-map.md)
- [`design/build-cache-pilot-program.md`](./build-cache-pilot-program.md)

The lane map is the rule for what must stay distinct: **Cargo-native workspace-local state, editor-private duplication, Cargo-native user-wide intermediates, compiler-wrapper caches, container recipe/layer caching, and CI/plugin exchange** are related but non-equivalent lanes.

The pilot order is deliberately ranked: Cargo-native split-dir first, editor coexistence second, wrapper cache third, container layer fourth, CI/user-wide exchange fifth.

## Shared stack role
This kit is now one leg of the archive’s shared **Build-State Evidence Stack**:
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md)
- [`design/build-state-evidence-pilot-program.md`](./build-state-evidence-pilot-program.md)

That means future revisions should treat Build Cache Kit primarily as the **layout / lock / reuse / retention** layer, not as a generic diagnosis tool or relink oracle.

## Adjacent kits and boundaries
- **Build Doctor Kit** consumes `build-state-pack/v0` as evidence; it should diagnose, not redefine cache/layout facts.
- **Change Impact Kit** classifies edits and rebuild scope; Build Cache Kit explains persisted artifact layout, lock scope, and reuse behavior once those impacts hit storage.
- **Compile-Time Capabilities Kit** explains build-script/proc-macro authority and determinism inputs; Build Cache Kit should reference those facts rather than absorb them.
- **Build Interop Kit** handles workspace/discovery/plan/event contracts; Build Cache Kit handles persisted build-state topology and reuse behavior.
- **SBOM Evidence Kit** inventories shipped/software dependency content; Build Cache Kit tracks intermediate/final build-state reuse, not supply-chain inventory.
- **Semantic Context Kit** is analysis/data-plane truth; Build Cache Kit is build-state persistence and reuse truth.

## Early pilots
1. **rust-analyzer coexistence pilot**
   - compare shared target-dir vs editor-private target-dir vs future build-dir split
   - emit lock reports and duplication reason codes
2. **workspace-local vs user-wide pilot**
   - reuse common dependencies across multiple workspaces
   - show unit-level reuse eligibility and rejections
3. **CI exchange pilot**
   - compare coarse blob caching to entry-aware exchange
   - report upload/download relevance and stale-entry rejection
4. **flat-dir / bloat pilot**
   - surface when layout causes retention or scan costs to rise pathologically

## Success criteria
- Users can explain *why* rust-analyzer and CLI builds blocked or duplicated work.
- Cargo-native future caching can reuse an artifact language the ecosystem already understands.
- CI cache integrations stop pretending every cache action is “hit or miss” on one opaque tarball.
- Teams can review GC, exchange, and isolation policies instead of discovering them through rebuild pain.

## Failure modes to avoid
- A fake universal cache score.
- Treating local/shared/editor/remote lanes as morally equivalent.
- Pretending reuse decisions are only about hashing and not about lock scope, policy, and trust.
- Replacing Cargo internals prematurely instead of building an adapter layer first.
