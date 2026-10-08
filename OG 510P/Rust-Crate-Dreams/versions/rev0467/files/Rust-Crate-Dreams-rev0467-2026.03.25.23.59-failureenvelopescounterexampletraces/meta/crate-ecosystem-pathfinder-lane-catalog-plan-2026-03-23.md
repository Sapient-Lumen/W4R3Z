# Crate ecosystem pathfinder lane catalog plan — 2026-03-23

This note deepens **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** around the next missing implementation layer:
**named task-lane templates**.

The archive already had good material for:

- task profiles,
- candidate import,
- evidence origin,
- starter-set readiness,
- freeze/replay/watch,
- and elimination/re-entry.

What it still lacked was one practical answer to:

> Which task lanes should a real `cargo pathfinder` ship first, and what should each lane provide other people?

## Main judgment

A credible `0.1` for **P-0509** should not ship only one generic “rank crates” workflow.
It should ship a **lane catalog** with a small number of high-value task templates.

Each lane template should provide:

1. a role map,
2. hard constraints,
3. default decision axes,
4. freeze rules,
5. scope-split defaults,
6. reconsideration triggers,
7. and a human-facing explanation contract.

That is the difference between an idea and a product.

## Why lane templates matter now

### 1. “The ecosystem” is not one task
The same public crate surfaces mean different things for:

- a newcomer CLI stack,
- an async service,
- a `no_std` device baseline,
- a Wasm component/plugin host,
- a desktop GUI,
- a safety-critical foundation,
- or a mixed Rust/C++ library boundary.

Without lane templates, the product silently smuggles in one hidden cultural default.

### 2. Current public surfaces are still generic
Cargo search/info/add, crates.io pages, docs.rs pages, security surfaces, and imported receipts are all useful.
None of them tell a team which roles matter for **their** lane.

### 3. Freezable defaults depend on lane-specific vetoes
A lane for teaching may optimize for learnability and stable docs.
A lane for embedded work may veto proc-macros or `std`.
A lane for plugin/component work may care more about target/posture than search visibility.
The product needs first-class space for those differences.

## Recommended first lane catalog

A strong `0.1` should ship a small, opinionated starter catalog.
Not every lane must freeze automatically, but each one should exist as a template.

### 1. `cli_baseline`
**Roles:**
- argument parsing,
- configuration loading,
- structured logging / diagnostics,
- error reporting,
- simple filesystem/process helpers.

**Default axes:**
- teaching fit,
- docs clarity,
- dependency footprint,
- low lock-in,
- maintenance posture.

**What it should provide other people:**
- one teachable starter set,
- one “minimal but boring” alternative,
- one record of which batteries are intentionally deferred.

### 2. `async_service_tokio`
**Roles:**
- runtime,
- HTTP server or RPC transport,
- serialization,
- config,
- logging / tracing,
- graceful shutdown support,
- test surface.

**Default axes:**
- runtime coupling,
- observability fit,
- concurrency semantics,
- production support posture,
- migration friction.

**What it should provide other people:**
- one reviewable service starter pack,
- one explanation of runtime lock-in,
- one set of re-entry conditions for alternative stacks.

### 3. `async_service_runtime_agnostic`
**Roles:**
- protocol/client/server surface,
- serialization,
- tracing/logging,
- cancellation/shutdown posture,
- portability across runtimes where possible.

**Default axes:**
- runtime neutrality,
- trait-surface portability,
- hidden companion requirements,
- migration friction.

**What it should provide other people:**
- one conservative stack that maximizes exit options,
- one explicit note when “runtime agnostic” is mostly an illusion.

### 4. `embedded_no_std_baseline`
**Roles:**
- alloc/no-alloc posture,
- HAL or portability layer expectations,
- logging/diagnostics,
- serialization/storage if needed,
- test/build surface.

**Default axes:**
- `no_std` truth,
- target/toolchain posture,
- build-script/proc-macro tolerance,
- MSRV stability,
- docs visibility versus actual support.

**What it should provide other people:**
- one starter set that does not fake `no_std`,
- one clear list of external prerequisites and unstable assumptions.

### 5. `linux_kernel_adjacent`
**Roles:**
- target/toolchain posture,
- version/MSRV expectations,
- unsafe boundary posture,
- public dependency exposure,
- low-level support constraints.

**Default axes:**
- toolchain compatibility,
- low-level surface clarity,
- public-boundary control,
- long-lived support posture.

**What it should provide other people:**
- one deliberately conservative choice pack,
- one refusal path when public surfaces are too weak to freeze.

### 6. `wasm_browser_client`
**Roles:**
- target posture,
- browser runtime integration,
- serialization/web APIs,
- package size / feature gating,
- debug/dev support.

**Default axes:**
- target fit,
- docs.rs visibility ceiling,
- browser-specific ergonomics,
- migration cost.

**What it should provide other people:**
- one browser-oriented starter set,
- one record of what target/default-target visibility does **not** prove.

### 7. `wasm_component_plugin`
**Roles:**
- component-model/tooling fit,
- host boundary,
- serialization/binding surface,
- packaging and test harness support.

**Default axes:**
- component support truth,
- host/guest portability,
- packaging friction,
- target-tooling maturity.

**What it should provide other people:**
- one component/plugin starter pack,
- one explicit note on what still requires manual review.

### 8. `desktop_gui_baseline`
**Roles:**
- UI toolkit,
- app lifecycle/state,
- logging/diagnostics,
- packaging/update surface,
- debug/iteration support.

**Default axes:**
- dev-loop quality,
- debug posture,
- platform coverage,
- migration friction,
- docs clarity.

**What it should provide other people:**
- one stack for teaching/prototyping,
- one stack for shipping,
- or one explicit scope-split receipt if those must diverge.

### 9. `data_pipeline_batch`
**Roles:**
- data interchange,
- IO/storage,
- CLI/config,
- observability,
- possibly async/runtime posture.

**Default axes:**
- format interoperability,
- dependency footprint,
- platform tooling fit,
- migration cost.

**What it should provide other people:**
- one boring pipeline starter pack,
- one explanation of when a heavier framework is intentionally out of scope.

### 10. `ffi_cpp_library_boundary`
**Roles:**
- ABI/binding layer,
- ownership/error boundary conventions,
- build/toolchain integration,
- test surface,
- packaging/public-boundary posture.

**Default axes:**
- toolchain support,
- boundary clarity,
- migration cost,
- public dependency exposure.

**What it should provide other people:**
- one mixed-language starter decision pack,
- one explanation of which support claims still belong to adjacent toolchain/interoperability lanes.

### 11. `safety_critical_foundation`
**Roles:**
- toolchain evidence,
- coverage/evidence hooks,
- dependency policy,
- support/maintenance posture,
- documentation/spec reference surfaces.

**Default axes:**
- evidence quality,
- transition/off-ramp posture,
- target/toolchain truth,
- documentation/spec basis,
- maintenance continuity.

**What it should provide other people:**
- one conservative, audit-friendly starter basis,
- one explicit refusal when current public evidence cannot support freezing.

## New first-class artifacts this implies

### `lane-template.receipt.json`
Purpose: identify which named lane was used, what its default roles/axes/vetoes are, and what local overrides were applied.

Suggested fields:
- `lane`
- `version`
- `roles`
- `default_axes`
- `default_vetoes`
- `scope_defaults`
- `overrides`
- `manual_review_required`

### `role-pack.manifest.json`
Purpose: show the named roles a frozen starter set actually covers and where companion crates are required.

### `lane-freeze.policy.json`
Purpose: lane-specific readiness rules, cooldown windows, and scope-split defaults.

### `lane-summary.md`
Purpose: a short human-facing explanation of the lane, the winning starter set, the rejected alternatives, and what the pack is good for.

## Suggested commands

- `cargo pathfinder template list`
- `cargo pathfinder init --lane cli_baseline`
- `cargo pathfinder explain --lane async_service_tokio`
- `cargo pathfinder freeze --lane embedded_no_std_baseline`
- `cargo pathfinder doctor --lane desktop_gui_baseline`
- `cargo pathfinder diff --lane ffi_cpp_library_boundary old/ new/`

## Distinctions the implementation must keep explicit

### Lane template is not the final winner
A lane template defines the problem shape, not the blessed outcome.

### Teaching lane is not production lane
The product should allow a principled split when those answers diverge.

### Docs visibility is not target support
Especially for Wasm, embedded, and mixed-language lanes, docs.rs visibility is still only one input.

### Runtime neutrality is not zero lock-in
Some “agnostic” stacks still buy strong trait, macro, or lifecycle commitments.

### Lane choice is not sector ownership
Using a safety-critical or kernel-adjacent lane does not mean pathfinder absorbs those whole sectors; it remains a choice-support layer.

## Good proving grounds

1. a newcomer CLI lane that freezes cleanly,
2. a Tokio service lane with visible runtime lock-in,
3. an embedded lane that refuses to freeze because `no_std` evidence is weak,
4. a GUI lane that intentionally splits teaching and shipping defaults,
5. a mixed-language lane that keeps toolchain/support truth separate from ranking.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
