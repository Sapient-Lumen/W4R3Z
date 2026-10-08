# Gap: Rust still lacks reviewable compatibility claims across platform, debugger, and acceptance boundaries

Rust projects increasingly need to say something sharper than “works on Linux/macOS/Windows” or “supported on stable”.
They need to say:
- which targets, host-tool lanes, docs surfaces, and runtime baselines are actually supported;
- which debugger families / versions / operating systems / visualizer lanes are expected to work;
- which advanced trait / borrow / solver-sensitive patterns are intentionally accepted on which compiler lanes;
- what changed between releases or toolchain updates;
- and what docs, release notes, policy gates, or safety-oriented consumers may legitimately conclude.

Today those answers are still scattered across:
- README support tables and issue-template prose;
- rustc target-tier policy pages and per-target notes;
- docs.rs defaults and crate-local docs metadata;
- debugger setup pages, visualizer scripts, and survey writeups;
- `trybuild` / `ui_test` fixtures and local compiler-lane folklore;
- and release notes or private maintainer memory when support posture changes.

That fragmentation means Rust still lacks a portable way to publish **compatibility claims** as reviewable, diffable, attachable artifacts. The archive now addresses this directly with [`design/compatibility-claims-lane-map.md`](../design/compatibility-claims-lane-map.md), which keeps host/build/release/docs/runtime/debugger/acceptance lanes distinct before any summary layer is allowed.

## Why this matters more now
Several current Rust signals make the missing seam unusually explicit.

- Rust’s target-tier policy distinguishes tier guarantees from the extra guarantees needed to ship host tools, so “supported target” is already more structured than many projects communicate.
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- Official support posture is visibly moving: `x86_64-apple-darwin` was demoted to Tier 2 with host tools for Rust 1.90 because CI guarantees changed, while Rust 1.91 promoted `aarch64-pc-windows-msvc` to Tier 1.
  https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- docs.rs changed its default target list in October 2025, proving that docs targets are part of the public support story rather than a hidden rendering detail.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The rustc platform-support pages already record real runtime-floor facts for some targets (minimum OS / kernel / glibc / ABI / CPU assumptions), so support claims are no longer reducible to a target triple.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- The 2026 debugging survey says people explicitly want support across several debugger versions and operating systems, quality visualizers, first-class async debugging, and Rust expression evaluation. That means “debugging support” is a compatibility claim in its own right.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The Rust compiler dev guide’s debugging material says Rust supports three major debuggers with materially different limitations and debug-info formats, which reinforces that debugger support varies by tuple instead of existing as one global property.
  https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/editor use rises. That increases the value of machine-usable compatibility truth instead of prose that humans reinterpret differently.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The safety-critical adoption writeup explicitly recommends target-focused readiness checklists and ecosystem-wide MSRV conventions, which is direct evidence that projects need support claims durable enough to survive long product lifetimes.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- On the compiler-acceptance side, the 2026 flagships keep next-solver stabilization and related trait-evolution work active. That means advanced-pattern acceptance will keep moving in ways projects may need to declare and diff.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s `supported-targets` RFC is a strong demand signal too: package authors clearly want a first-class way to express target support posture, but that alone still would not settle runtime floors, debugger support, or solver-sensitive acceptance.
  https://github.com/rust-lang/rfcs/pull/3759

Taken together, the missing problem is not just “we need better CI matrices.”
The missing problem is:

**how can a Rust project publish compatibility claims that stay honest across platform support, debugger tuple reality, and compiler-lane acceptance drift?**

## What is missing
The ecosystem still lacks a thin shared layer that keeps these truths distinct but composable:

1. **Platform/support truth**
   - dev-host vs source-build vs release-artifact vs docs-surface vs runtime-floor lanes;
   - target tier and host-tool posture;
   - runtime floors and provisioning assumptions;
   - declared vs observed support.

2. **Debugger tuple truth**
   - debugger family / version / OS / target / toolchain tuple;
   - visualizer availability and compatibility;
   - async-inspection and expression-evaluation posture;
   - `supported` / `partial` / `watch` / `unsupported` outcomes.

3. **Acceptance truth**
   - solver-/borrow-check-sensitive pattern families;
   - stable/beta/nightly/experimental compiler-lane profiles;
   - workaround truth and reason-coded acceptance diffs;
   - explicit “supported today” versus “works only on experimental lane” boundaries.

4. **Change and consumer truth**
   - what changed between releases or toolchain updates;
   - what docs, release, support, policy, safety, or assistant consumers may import;
   - what they are forbidden to flatten into one fake “supported” verdict.

## What this should not become
This should **not** become:
- a universal compatibility badge;
- a giant hosted matrix site;
- another cross-build wrapper or one more UI-test harness;
- or a mega-schema that erases support, debugger, and acceptance differences.

The missing contribution is a **compatibility-claims substrate** that can import lane-specific evidence while preserving exactly which kind of claim each artifact is making.

## What a worthy contribution would look like
A serious contribution here would:
- give projects a thin `compat-pack`-style bundle for compatibility claims;
- import support-envelope, debugger-capability, and acceptance-surface artifacts instead of replacing them;
- publish reason-coded diffs when compatibility posture changes;
- render bounded summaries for docs, releases, support pages, CI, policy, and safety-oriented consumers;
- and keep declared claims, observed evidence, imported debugger truth, and imported acceptance truth visibly separate.

That is the part the Rust ecosystem still appears to be missing.

## Likely shape of the solution
The strongest path is an explicit **Compatibility Claims Stack** with:
- **Support Envelope Kit** as the platform/runtime owner;
- **Acceptance Surface Kit** as the compiler-lane/pattern owner;
- **Debuggability Stack** as the source of imported debugger tuple truth;
- and a thin composition layer that publishes compatibility subjects, lane catalogs, imported claim registers, diffs, and bounded consumer summaries.

That would let projects describe compatibility as a reviewable contract instead of a mixture of target tiers, debugger caveats, docs.rs defaults, and passing screenshots.
