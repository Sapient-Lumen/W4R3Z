# Missing-crate sector atlas — 2026-03-23

This note exists to make the archive think **wider** without becoming vague.

The Rust ecosystem now spans many real sectors and subcultures.
A serious missing-crates archive should therefore ask two questions at once:

1. what horizontal crates would help many sectors immediately,
2. and which sectors might eventually justify their own epic crate lanes?

## Main judgment

Across a very wide range of domains, the current archive still sees the same pattern:

- the strongest repeated needs are mostly **control-plane crates**,
- while many sector-specific opportunities still look more like **future workbenches** than near-term top-frontier promotions.

In other words:
- variety is real,
- but it does not automatically outrank the current top board.

## Sector atlas

### 1. Async backend and service platforms — **horizontal-first**
**Why it matters:** async remains a live Rust challenge; backend/server work remains a central Rust growth area.

**Sharper missing crates:**
- **P-0538 Concurrency Contract**
- **P-0486 Debuggability Support**
- **P-0509 Pathfinder**
- **P-0535 Dependency Lifecycle Transition**

**What a worthy crate should provide other people:**
- semantic receipts for channels/tasks/runtime assumptions,
- async debugging/support truth,
- starter-set decisions under runtime constraints,
- migration packets when switching stacks.

### 2. GUI, desktop, game, and creative-app loops — **horizontal-first**
**Why it matters:** the Rust challenges post explicitly calls out GUI compilation pain as a distinctive workflow burden.

**Sharper missing crates:**
- **P-0537 Compile Iteration Feedback**
- **P-0486 Debuggability Support**
- **P-0509 Pathfinder**

**What a worthy crate should provide other people:**
- edit-to-feedback packets,
- stale-code and activation honesty,
- teaching-vs-shipping stack decisions,
- debugger capability packets for visual / event-heavy apps.

### 3. Embedded and edge — **horizontal-first**
**Why it matters:** embedded shows up explicitly in the March 2026 challenges post as a domain with special constraints.

**Sharper missing crates:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0509 Pathfinder**
- **P-0058 Native Deps** where foreign toolchains or C integration appear

**What a worthy crate should provide other people:**
- target / prerequisite truth,
- `no_std` / allocator / linker route clarity,
- dependency pin/replace packets,
- starter sets that respect constrained environments.

### 4. Safety-critical and regulated delivery — **horizontal-first with evidence-heavy sector labs**
**Why it matters:** 2026 flagship work explicitly names safety-critical Rust, MC/DC, unsafe documentation, lints, and FLS cadence.

**Sharper missing crates:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0011 Crate Health**
- evidence-heavy labs such as MC/DC and qualification-support kits

**What a worthy crate should provide other people:**
- audit-friendly evidence bundles,
- long-lived support declarations,
- dependency provenance and continuity truth,
- claim ceilings that survive later review.

### 5. Wasm components, plugins, and host/guest systems — **horizontal-first**
**Why it matters:** Wasm Components are now an explicit 2026 flagship track.

**Sharper missing crates:**
- **P-0484 Toolchain & Target Support**
- **P-0509 Pathfinder**
- **P-0536 Crate Knowledge Pack**

**What a worthy crate should provide other people:**
- host-vs-target support receipts,
- plugin/component stack choices,
- docs/build/target-aware knowledge packs,
- manual-review triggers when runtime behavior exceeds docs visibility.

### 6. Mixed-language / C++ / foreign SDK ecosystems — **horizontal-first**
**Why it matters:** interop remains a durable adoption boundary across enterprise, devices, performance-sensitive stacks, and SDK surfaces.

**Sharper missing crates:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0509 Pathfinder**
- evidence workbenches where ABI, generator, or dialect truth matters

**What a worthy crate should provide other people:**
- wrapper-vs-generator-vs-bindgen choice packets,
- ABI/prerequisite truth,
- migration/off-ramp plans,
- support boundaries for foreign dependencies.

### 7. Local-first collaboration and offline-first apps — **watchlist sector lab**
**Why it matters:** this is a real modern software need, but the archive should not jump straight to “the one true CRDT supercrate.”

**A worthy future lane would need to provide:**
- conflict-evidence packets,
- storage/transport/sync separation receipts,
- replayable merge traces,
- durability / portability claim ceilings,
- manual-review triggers for data-loss or policy-sensitive cases.

**Current repo judgment:** watch closely, but do not outrank pathfinder/debug/build truth yet.

### 8. Robotics, digital twins, industrial automation — **watchlist sector lab**
**Why it matters:** this domain combines timing, control, interop, simulation, safety, and hardware reality.

**A worthy future lane would need to provide:**
- timing-boundary evidence,
- simulation-vs-device equivalence ceilings,
- state handoff / transport / control-loop receipts,
- toolchain and certification boundary packets.

**Current repo judgment:** promising, especially where safety-critical and interop pressures meet, but still below the horizontal frontier.

### 9. Geospatial, logistics, and physical-world data — **watchlist sector lab**
**Why it matters:** these stacks care about coordinate transforms, precision loss, provenance, and format boundaries more than a generic “maps crate list.”

**A worthy future lane would need to provide:**
- provenance receipts,
- transform/loss accounting,
- coordinate-reference and precision ceilings,
- reviewable conversion bundles.

### 10. Science, numerics, GPU, and data engineering — **horizontal-first with format/loss sub-labs**
**Why it matters:** these users often need interop truth, device/layout constraints, build support, and migration honesty.

**Sharper missing crates:**
- **P-0509 Pathfinder**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- specific format/loss/accounting workbenches when crossing ecosystems

**Guardrail:** do not invent a “Rust NumPy / ML / GPU supercrate” lane unless it exports a new evidence seam.

### 11. Reverse engineering, observability, and eBPF-adjacent operations — **watchlist sector lab**
**Why it matters:** these systems are intensely capability- and target-sensitive.

**A worthy future lane would need to provide:**
- capability-route receipts,
- kernel / target / toolchain support truth,
- privilege / deployment boundary packets,
- verifier or portability claim ceilings.

### 12. Media, timeline, and transcoding systems — **watchlist sector lab**
**Why it matters:** these stacks are full of timing, buffering, codec, and packaging edges that are easy to overclaim.

**A worthy future lane would need to provide:**
- timeline semantics receipts,
- buffering and drift reports,
- codec capability packets,
- support ceilings for platform-specific acceleration.

### 13. Air-gapped enterprise and long-lived internal platforms — **watchlist sector lab with strong overlap to native/build/dependency lanes**
**Why it matters:** many large adopters need offline, controlled, reviewable delivery.

**Sharper missing crates today:**
- **P-0058 Native Deps**
- **P-0535 Dependency Lifecycle Transition**
- **P-0489 Cargo Build-Dir Consumer Transition**
- **P-0536 Crate Knowledge Pack**

**A sector-specific lane would only be justified if it exported:**
- air-gap support bundles,
- repeatable vendoring / rebuild packets,
- native prerequisite proofs,
- reviewable update/off-ramp workflows.

## Ranking rule for future sector promotions

A sector should only earn a new top-level lane if all of these are true:

1. the missing value is **not** better explained by pathfinder, debuggability, dependency transition, docs/build truth, toolchain support, native deps, or crate knowledge packs;
2. it exports a **portable artifact seam** another team can review later;
3. it avoids the trap of becoming a giant “industry umbrella” with no product boundary;
4. it names what the crate would **refuse to claim**.

## Eliminate-for-now bucket

These ideas may still be useful someday, but do not currently deserve frontier promotion:
- a generic Rust AI-wrapper mega-lane,
- a generic “one true game dev stack” lane,
- a generic “science supercrate” lane,
- a generic “enterprise platform crate” lane.

Unless they produce stronger artifacts than the current frontier, they are still weaker than deepening the control-plane kits.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
