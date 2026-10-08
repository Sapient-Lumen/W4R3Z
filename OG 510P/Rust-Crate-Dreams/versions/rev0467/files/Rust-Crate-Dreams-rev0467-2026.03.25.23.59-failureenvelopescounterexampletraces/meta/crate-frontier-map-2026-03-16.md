# Crate frontier map — 2026-03-16

This map is the archive’s current answer to “what kinds of missing crates seem most worth building across a very wide range of Rust use-cases?”
It is deliberately broader than the narrow ranked frontier snapshots.

Current official Rust signals suggest three cross-cutting pains remain unusually important:

1. **ecosystem orientation / supportiveness**,
2. **build and Cargo explainability**,
3. **interop and evidence workbenches that make niche domains boring to adopt**.

## 1. Ecosystem orientation and supportive crate surfaces

Most cross-cutting right now.
This is the lane cluster that helps people answer not only “what should I reach for?” but also “what does the chosen crate actually hand me before and after failure?” without pretending the Rust project has officially blessed one answer forever.

Primary proposals:
- `proposals/crate-ecosystem-pathfinder-kit.md` (**P-0509**)
- `proposals/crate-guidance-pack-kit.md` (**P-0512**)
- `proposals/crate-runtime-handoff-pack-kit.md` (**P-0513**)
- `proposals/crate-upgrade-pack-kit.md` (**P-0514**)
- `proposals/crate-offramp-pack-kit.md` (**P-0515**)
- `proposals/crate-configuration-scenario-pack-kit.md` (**P-0516**)
- `proposals/crate-performance-envelope-pack-kit.md` (**P-0517**)
- `proposals/crate-observability-surface-pack-kit.md` (**P-0518**)
- `proposals/crate-authority-surface-pack-kit.md` (**P-0519**)
- `proposals/crate-lifecycle-surface-pack-kit.md` (**P-0520**)
- `proposals/crate-resource-surface-pack-kit.md` (**P-0521**)
- `proposals/crate-persistence-surface-pack-kit.md` (**P-0522**)
- `proposals/crate-test-surface-pack-kit.md` (**P-0523**)
- `proposals/crate-example-surface-pack-kit.md` (**P-0524**)
- `proposals/crate-diagnosis-surface-pack-kit.md` (**P-0525**)
- `proposals/crate-capability-contract-kit.md` (**P-0510**)
- `proposals/crate-interop-profile-pack-kit.md` (**P-0511**)
- `proposals/crate-health.md` (**P-0011**)
- `proposals/trust-lens.md` (**P-0017**)
- `proposals/stdx-curated.md` (**P-0006**)

Judgment:
- **P-0509** is the highest-value task-selection artifact.
- **P-0514** is the sharpest release-to-release supportiveness lane: it answers how a downstream user should actually move between crate versions.
- **P-0515** is the sharpest deprecation/supersession/off-ramp lane: it answers how a downstream user should actually leave a crate, lane, or unsafe version family.
- **P-0516** is the sharpest setup/configuration lane: it answers how a downstream user should actually instantiate a chosen crate for a named scenario instead of hand-assembling a recipe from feature names and docs fragments.
- **P-0517** is the sharpest performance-support lane next to it: it answers what performance tradeoff a downstream user is actually buying, which metric is authoritative, and where benchmark honesty stops.
- **P-0518** is the sharpest operability/observability-support lane next to it: it answers what telemetry a downstream user can actually expect, which names are stable enough to rely on, and where cost or sensitivity boundaries begin.
- **P-0519** is the sharpest authority-surface / sandboxability-support lane next to it: it answers what ambient powers a downstream user is actually buying, what can be injected or disabled, and where determinism or host dependence begins.
- **P-0520** is the sharpest lifecycle-support lane next to them: it answers what background work a downstream user is actually buying, which stop paths are supported, and where cancel / abort / drain obligations begin.
- **P-0521** is the sharpest resource-support lane next to them: it answers what queues, buffers, pools, caches, workers, and bursts a downstream user is actually buying, which of them are bounded, and where saturation semantics begin.
- **P-0522** is the sharpest persistence-support lane next to them: it answers what bytes or durable state a downstream user is actually buying, which of those surfaces are public contracts versus internal-only artifacts, and where compatibility, durability, recovery, and migration semantics begin.
- **P-0523** is the sharpest downstream-testing-support lane next to them: it answers what official fixtures, fake backends, deterministic seams, scenario corpora, and integration topologies a downstream user is actually buying.
- **P-0524** is the sharpest adoption / example-support lane next to them: it answers what the smallest officially supported path to first success actually is, where the examples live, what they require, and what success should look like.
- **P-0525** is the sharpest diagnosis / troubleshooting-support lane next to them: it answers which symptoms a downstream user can officially rely on, what self-checks exist, which signals matter first, and what evidence is safe to capture.
- **P-0512** is the sharpest compile-time / early-failure supportiveness lane next to it.
- **P-0513** is the sharpest runtime failure handoff lane above raw error/panic substrate and below domain-specific incident bundles.
- **P-0510** is the most promising producer-side contract lane.
- **P-0511** is the sharpest shared ecosystem-profile lane above standard building blocks and below task-specific selection.
- **P-0011** and **P-0017** are important imports into that broader ecosystem-supportiveness frontier.
- **P-0006** is best treated as one possible downstream output, not the entire answer.

## 2. Cargo/build explainability and review artifacts

Still the archive’s densest high-salience cluster because the Rust project is actively adding substrate while users still lack portable explanations.

Primary proposals:
- `proposals/cargo-resolver-explanation-kit.md` (**P-0468**)
- `proposals/cargo-build-insights.md` (**P-0035**)
- `proposals/cargo-rebuild-explanation-kit.md` (**P-0469**)
- `proposals/cargo-lock-contention-witness-kit.md` (**P-0490**)
- `proposals/build-std-workbench-kit.md` (**P-0430**)

Judgment:
- These are among the archive’s strongest “boring but epic” crates because they turn painful invisible behavior into reviewable evidence.

## 3. Async supportiveness, migration, and determinism

Rust’s async story is valuable but still feels more expert-only than “sync Rust”.
The best missing crates here are the ones that make transition, replay, and failure explanation portable.

Primary proposals:
- `proposals/async-dyn-transition-kit.md` (**P-0458**)
- `proposals/deterministic-simulation-kit.md` (**P-0104**)
- `proposals/hardship-harness-kit.md` (**P-0114**)

Judgment:
- The strongest work here is not yet another runtime or executor.
- It is tooling that makes async adoption and async failure reviewable.

## 4. Release truth, package review, and supply-chain receipts

This is where “can we ship/review/trust what Cargo produced?” becomes a first-class artifact story.

Primary proposals:
- `proposals/cargo-package-review-kit.md` (**P-0470**)
- `proposals/cargo-sbom-precursor-workbench-kit.md` (**P-0125**)
- `proposals/cargo-artifact-handoff-kit.md` (**P-0471**)

Judgment:
- These are strong because they fit real release engineering pain without pretending Cargo itself must solve every org-policy layer.

## 5. Docs, learning, and support surfaces

A quieter but still valuable cluster.
If Rust users learn from docs and source, the archive should care about the artifacts that make those surfaces less surprising.

Primary proposals:
- `proposals/crate-example-surface-pack-kit.md` (**P-0524**)
- `proposals/crate-diagnosis-surface-pack-kit.md` (**P-0525**)
- `proposals/docsrs-build-parity-evidence-kit.md` (**P-0472**)
- `proposals/cargo-doc-portal.md` (**P-0049**)

Judgment:
- This cluster is probably under-ranked compared with its educational leverage.
- **P-0524** is the strongest receiver-facing lane here because it turns first-success and example trust into reviewable artifacts instead of asking users to infer them from prose.
- **P-0525** is the strongest troubleshooting-support neighbor here because it turns symptom recognition and self-check guidance into reviewable artifacts instead of issue-thread folklore.
- Good docs/support crates often multiply the value of other crates rather than competing with them.

## 6. Text, UI, and accessibility substrate

A major cross-domain adoption frontier: desktop, mobile, embedded screens, editors, browsers, and assistive tech all touch it.

Primary proposals:
- `proposals/text-layout-conformance-kit.md` (**P-0197**)
- `proposals/ui-accessibility-kit.md` (**P-0087**)
- `proposals/text-input-kit.md` (**P-0027**)

Judgment:
- This cluster remains one of the best “Rust is missing boring defaults” frontiers outside Cargo.

## 7. Local-first and distributed application support

Rust has substrate here, but still lacks enough boring coordination artifacts for real-world ops and debugging.

Primary proposals:
- `proposals/localfirst-sync-kit.md` (**P-0076**)
- `proposals/deterministic-simulation-kit.md` (**P-0104**)
- `proposals/hardship-harness-kit.md` (**P-0114**)

Judgment:
- This cluster deserves more attention whenever the archive swings too far back into Cargo-only work.

## 8. Domain-specific interop workbenches

The archive has a very wide long tail here: healthcare, geospatial, robotics, identity, media, scientific data, industrial systems, and more.
The best proposals are usually the ones that sit above existing Rust substrate and below impossible “rewrite the world” ambitions.

Judgment:
- Keep choosing domains where Rust already has meaningful pieces but still lacks a boring coordination artifact: conformance kits, replay bundles, profile locks, semantic diffs, and evidence packs.

## Current portfolio rule

When choosing the next proposal to strengthen, prefer one of three shapes:

1. a **cross-cutting decision/supportiveness crate**,
2. a **Cargo/build explainability crate**,
3. or a **domain workbench** that makes an existing but messy standards surface portable and reviewable.

That is where the archive’s best “epic but buildable” crates now live.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/reference/attributes.html
- https://doc.rust-lang.org/std/error/index.html
- https://doc.rust-lang.org/std/error/trait.Error.html
- https://doc.rust-lang.org/std/backtrace/index.html
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
