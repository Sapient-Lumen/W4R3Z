## Execution addendum (rev0456)
Read `design/compatibility-claims-execution-blueprint-2026Q1.md` before using this stack as if it already answered “what should we build?”.

Interpretation rule:
- this stack still names the imported-owner layers;
- the execution blueprint now names the concrete contribution shape as **reference layer + report/pack command + imported-claims corpus**;
- and future stack edits should preserve subject, claim-family, evidence, drift, consumer-handoff, and unknown/out-of-scope truth as separate layers.

# Design: Compatibility Claims Stack (Support Envelope + Acceptance Surface, with Debuggability imports)

## Goal
Treat **compatibility claims** as a first-class ecosystem layer instead of leaving them split across support tables, debugger lore, compiler-lane fixtures, and release-note caveats. Read this together with [`design/compatibility-claims-lane-map.md`](./compatibility-claims-lane-map.md), which now states the rule for what must stay separate.

The missing contribution is not another platform matrix, another UI-test harness, or a universal compatibility badge.
It is an explicit stack that lets Rust projects describe:
- what support they declare across dev-host, source-build, release-artifact, and docs lanes;
- what debugger tuples and visualizer lanes they can honestly claim;
- what advanced trait / borrow / solver-sensitive patterns they intentionally support on which compiler lanes;
- what changed;
- and what downstream docs, release, policy, audit, and assistant consumers may safely import.

The archive already had most of the pieces.
What it still lacked was the synthesis saying those pieces together define a real frontier for **compatibility-claim products**.

## References (signals)
- Target tiers and host-tool guarantees are already structured and not equivalent.
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- Runtime floors are already present in platform-support docs for some targets, which proves that support is more than a triple.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- Rust 1.90/1.91 showed support posture moving in both directions: `x86_64-apple-darwin` demotion and `aarch64-pc-windows-msvc` promotion.
  https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- docs.rs changed its default targets in October 2025, so docs surfaces are part of the public compatibility story.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The 2026 debugging survey and compiler-dev-guide debuginfo pages make debugger-family/version/OS variability explicit.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
- The Rust Reference exposes `debugger_visualizer`, proving that visualizer artifacts are part of the public debugging surface rather than purely private setup.
  https://doc.rust-lang.org/reference/attributes/debugger.html
- The 2025 State of Rust survey says online docs remain canonical while machine consumers rise, which increases the need for attachable compatibility truth.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 flagships keep next-solver work live, so acceptance posture for advanced patterns remains a moving compatibility boundary.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s `supported-targets` RFC shows that package authors want first-class support declarations, but it only covers one slice of the wider compatibility problem.
  https://github.com/rust-lang/rfcs/pull/3759

## Core ownership model
### Support Envelope Kit owns
- dev-host / source-build / release-artifact / docs lanes;
- target / provisioning / host-tool posture;
- runtime-floor reports and support observations;
- support diffs and waivers.

### Acceptance Surface Kit owns
- named advanced-pattern catalogs;
- compiler-lane profiles;
- expected pass/fail/xfail posture;
- workaround truth and acceptance diffs.

### Debuggability Stack exports into this stack
Compatibility Claims should **import**, not absorb:
- debugger family/version/OS/target/toolchain tuple truth;
- visualizer coverage;
- async-inspection posture;
- expression-evaluation posture;
- tuple-specific capability results.

That separation matters.
“Compiles and runs” is not the same as “supported for debugging”, and neither is the same as “advanced trait patterns accepted on stable”.

## Design principles
1. **Keep claim kinds separate.** Platform support, debugger support, and advanced-pattern acceptance are related but non-equivalent.
2. **Declared vs observed stays visible.** A declaration without observation is still useful, but it is not an observed result.
3. **Debugger truth is imported, not silently implied.** Native stepping, visualizers, async inspection, and expression evaluation cannot be flattened into one generic support bit.
4. **Acceptance truth is pattern-based, not slogan-based.** The unit of review is a named pattern family on a specific compiler lane.
5. **Diffs matter.** Compatibility claims are strategic partly because they drift.
6. **Consumers need bounded summaries.** Docs, release notes, support pages, CI, policy, and safety/audit consumers need different renderings of the same underlying truth.
7. **Do not build a mega-format.** The stack should mainly compose existing lower-layer artifacts.

## Core artifact family
### 1. `compat-subject/v0`
Records:
- crate / workspace / release / binary / package identity;
- relevant version or release candidate;
- supported audience or consumer class;
- linked packs and imported lower-layer artifacts.

### 2. `compat-lane-catalog/v0`
Defines the named compatibility lanes in scope.

Should record:
- lane ids and classes (`platform-support`, `debugger-tuple`, `acceptance-profile`, `docs-surface`, `other`);
- human-facing labels;
- whether the lane is declared, observed, imported, or mixed;
- required lower-layer attachments;
- review/waiver posture.

### 3. `compat-claim-register/v0`
The thin composition record tying imported artifacts together.

Should record:
- linked `support-envelope`, `support-observation-report`, or `support-diff-report` entries where relevant;
- linked debugger capability/battery/tuple artifacts where relevant;
- linked acceptance expectation/check/diff artifacts where relevant;
- claim status (`supported`, `partial`, `watch`, `experimental`, `deprecated`, `unsupported`, `inconclusive`);
- reason codes;
- explicit declared-vs-observed notes;
- confidence and bounded uncertainty.

Design rule: **the register imports lower-layer truth rather than replacing it**.

### 4. `compat-change-report/v0`
A cross-lane compatibility diff artifact.

Should record:
- baseline and comparison identity;
- lane additions/removals;
- support widening/narrowing;
- debugger tuple changes;
- acceptance-lane changes;
- raised/lowered runtime floors;
- docs-target changes;
- reason-coded verdicts and waivers.

### 5. `compat-consumer-summary/v0`
A bounded rendering layer for consumers.

Should record:
- consumer class (`docs`, `release`, `support`, `ci`, `policy`, `audit`, `assistant`, `other`);
- which lanes are relevant to that consumer;
- what the consumer may say directly;
- mandatory caveats;
- forbidden automatic conclusions.

### 6. `compat-pack/v0`
Bundle for review and reuse:
- subject;
- lane catalog;
- claim register;
- optional change report;
- one or more consumer summaries;
- imported support/debugger/acceptance attachments or pointers;
- checksums and generator identity.

## What a worthy contribution would look like in practice
A serious contribution here would look like a thin `cargo compat` / `compat-pack/v0` layer that:
- imports lower-layer support, debugger, and acceptance artifacts;
- renders a reviewable claim register rather than prose-only badges;
- supports reason-coded diffs across releases and toolchain updates;
- and lets more than one consumer reuse the same facts without bespoke scraping.

The bar is **not**:
- a hosted compatibility dashboard,
- a cargo-core merger fantasy,
- or a schema that pretends all compatibility evidence is the same kind of thing.

The bar is a **portable compatibility-claims contract layer**.

## Boundaries and non-goals
- **Not Support Envelope Kit:** Support Envelope still owns platform/runtime/support truth.
- **Not Acceptance Surface Kit:** Acceptance Surface still owns compiler-lane/pattern truth.
- **Not Debuggability Stack:** debugger tuple truth should stay a separate input.
- **Not a universal score or badge:** the point is explicit lane-specific claims.
- **Not a substitute for target-tier policy, docs.rs, debugger work, or compiler evolution:** the stack composes with them.

## Immediate archive consequence
The archive should now treat [`design/compatibility-claims-lane-map.md`](./compatibility-claims-lane-map.md) as the explicit lane-discipline note above the rest of this stack.

The archive should now treat:
- [`design/support-envelope-kit.md`](./support-envelope-kit.md),
- [`design/support-envelope-pilot-program.md`](./support-envelope-pilot-program.md),
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md),
- [`design/compatibility-claims-pilot-program.md`](./compatibility-claims-pilot-program.md),
- and imported debugger tuple outputs from the Debuggability Stack

as one explicit **Compatibility Claims Stack**.

That does **not** demote the lower layers.
It clarifies that together they now form a credible path toward an epic ecosystem contribution.

See also: [`proposals/epic-compatibility-claims-stack.md`](../proposals/epic-compatibility-claims-stack.md).
