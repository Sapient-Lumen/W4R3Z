## Execution addendum (rev0456)
Read `design/compatibility-claims-execution-blueprint-2026Q1.md` first when turning this pilot program into a real build plan.

Interpretation rule:
- this pilot program still matters as a proving-lane catalog;
- the execution blueprint now names the concrete contribution shape and bounded handoff rules;
- and pilot outputs should remain imported claims rather than a portal or badge pretending to own the whole verdict.

# Design: Compatibility Claims Pilot Program

## Why this pilot program exists
The archive already has two strong but slightly separated ideas:
- [`design/support-envelope-kit.md`](./support-envelope-kit.md) for platform / runtime / docs / delivery support truth
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md) for solver- and borrow-check-sensitive acceptance truth

This pilot program treats them as one strategic band: **Compatibility Claims**. Read it alongside [`design/compatibility-claims-stack.md`](./compatibility-claims-stack.md) and [`design/compatibility-claims-lane-map.md`](./compatibility-claims-lane-map.md): Support Envelope and Acceptance Surface are the core owners, while debugger tuple truth remains an imported input from the Debuggability Stack rather than a silent implication.

The common problem is simple:
Rust keeps getting richer support and acceptance stories, but projects still publish them as scattered README prose, ad hoc CI matrices, debugger issue trackers, unstable-lane caveats, and local test fixtures.

That was always inefficient. It is more urgent now because official Rust work is actively changing the boundaries people care about:
- target tiers and host-tool guarantees continue to evolve;
- target promotions and baseline changes keep happening;
- safety-critical adopters explicitly need to map “tier” and toolchain drift to something they can responsibly bet on;
- debugger support varies by debugger family, version, operating system, async/runtime features, and visualizer coverage;
- next-solver, Polonius, and evolving-trait work are changing what advanced Rust patterns are accepted and how stable those answers are.

So the missing contribution is not one more cross-build wrapper, not one more UI-test harness, and not one more compatibility badge.
It is a **reviewable compatibility-claims substrate** that makes support claims and acceptance claims explicit, diffable, and attachable.

## Primary signals
- Rust’s target-tier policy and platform-support docs already distinguish tier guarantees, host tools, and platform-specific runtime notes:
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- Rust 1.91 promoted `aarch64-pc-windows-msvc` to Tier 1, proving that target support is not static and that support-diff artifacts matter:
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- The Rust debugging survey says support varies across debugger family/version and operating system, and calls out visualizers, async debugging, and expression evaluation as explicit expectations:
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The safety-critical adoption writeup says regulated teams need to map tier/support language to what they can responsibly bet on for their platform and product lifetime:
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2026 flagships and 2025H2 goals make solver- and borrow-sensitive acceptance drift a live issue, not a hypothetical one:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- Cargo’s machine-facing direction keeps strengthening: plumbing commands, `cargo report`, structured logging, and JSON-schema work all point toward a larger ecosystem need for explicit machine-usable contracts:
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/

## Working thesis
A worthy contribution here should make it possible to answer questions like:
- “What do you support on Linux, macOS, Windows, custom targets, and docs.rs — in what sense?”
- “What minimum OS / glibc / kernel / SDK / ABI / CPU-feature assumptions are attached to that claim?”
- “Which debuggers and debugger versions are expected to work on which targets?”
- “Which advanced trait/borrow patterns are intentionally supported on stable today?”
- “Which patterns only work on nightly / next-solver / Polonius lanes?”
- “What changed between the last release and this one?”

## The stack
### 1) Support Envelope Kit
Owns:
- dev-host / source-build / release-artifact / docs lanes
- runtime floors
- observed support evidence
- support diffs and waivers

### 2) Acceptance Surface Kit
Owns:
- named pattern catalogs
- compiler-lane profiles
- expected pass/fail/xfail posture
- workaround truth
- acceptance diffs and waivers

### 3) Shared compatibility-claims posture
They should share:
- subject identity conventions
- lane naming discipline
- evidence strength vocabulary
- diff / waiver ergonomics
- attachable pack conventions
- explicit “declared vs observed” separation

## Ranked pilot program
### Pilot 1 — Released binary with explicit runtime floors
Use one CLI or service binary that ships Linux/macOS/Windows artifacts.

Must prove:
- support-envelope separation between dev-host, source-build, release-artifact, and docs lanes;
- explicit runtime-floor reports (glibc / macOS / Windows SDK or CRT where knowable);
- support diffs when floors or shipped artifacts change.

Why first:
- it is the clearest user-facing support-claims case;
- it exercises release tooling, docs, CI, and packaging all at once;
- it forces the archive to treat platform support as a contract, not a vibe.

### Pilot 2 — Debugger capability lane
Use a crate or workspace with a reproducible debugger battery.

Must prove:
- debugger family / version / OS lanes are explicit;
- visualizer packs and async-debug posture can attach to the support story;
- projects can publish “supported for debugging” separately from “compiles and runs.”

Why second:
- the debugging survey makes this pain explicit;
- it shows that compatibility claims are broader than target triples;
- it connects Support Envelope Kit to Debugger Experience Kit without flattening them.

### Pilot 3 — Advanced-pattern acceptance lane
Use one crate close to trait-solver or borrow-check edges.

Must prove:
- explicit stable/beta/nightly/experimental lane profiles;
- named accepted/rejected/workaround-dependent pattern families;
- acceptance diffs across solver / Polonius / evolving-trait changes.

Why third:
- this is where Acceptance Surface Kit becomes obviously strategic;
- it creates reusable evidence for docs, release notes, and ecosystem guidance;
- it avoids waiting until solver transitions have already surprised users.

### Pilot 4 — Mixed workspace support + acceptance bundle
Use one workspace with host tools, a library, and at least one cross-target or Wasm/native boundary.

Must prove:
- one archive can carry both support claims and acceptance claims without conflating them;
- docs surfaces, toolchain lanes, and advanced-pattern lanes remain distinct;
- diff reports remain readable under real workspace complexity.

### Pilot 5 — Safety-oriented / long-lived support lane
Use one project that cares about long support windows, explicit toolchain pinning, or regulated review.

Must prove:
- support claims survive contact with long-lived baselines and target tiers;
- waivers and bounded uncertainty can be recorded honestly;
- the output is useful to policy / assurance layers rather than just CI.

## Shared schema discipline
Pilot outputs should keep these distinctions intact:
1. **declared** claim vs **observed** result
2. **platform support** vs **debugging support** vs **advanced-pattern acceptance**
3. **stable lane** vs **experimental lane**
4. **runtime floor** vs **target triple**
5. **semantic workaround** vs **behaviorally lossy workaround**
6. **temporary waiver** vs **supported contract**

## What not to do
Do not turn this pilot program into:
- a universal compatibility badge,
- a giant hosted matrix service,
- a single mega-format that erases support/acceptance differences,
- or an excuse to duplicate Cargo/rustc/project-goals work.

The job is narrower and more valuable:
**publish compatibility claims in a form that people and tools can actually review.**

## Archive implications
This pilot program strengthens the case that the next credible frontier move is not merely more build plumbing or more language theorizing in isolation.
It is a cross-cutting, attachable compatibility-claims layer that can feed:
- Safety Evidence Kit
- Debugger Experience Kit
- Release Pipeline Kit
- DocProof Kit
- Ecosystem Atlas Kit
- Policy / Trust / Lifecycle tooling
- and future Cargo/rustc machine-facing seams
without pretending to replace any of them.
