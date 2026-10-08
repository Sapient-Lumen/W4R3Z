# Design: Dependency Control pilot program (`cargo resolve pilot`, `cargo feature pilot`, `dependency-control-pack/v0`)

## Goal
Read together with [`proposals/epic-dependency-control-stack.md`](../proposals/epic-dependency-control-stack.md).

Make the archive treat **Resolution Doctor Kit** and **Feature Kit** as a shared **Dependency Control Stack** without collapsing them into one mega-command.

The missing contribution is not merely “better dependency tooling”.
It is a disciplined rollout that proves Rust projects can publish **portable dependency-control evidence** for a few concrete lanes before widening scope.

## References (signals)
- Rust in 2026 flagships: public/private dependencies and SBOM support remain active supply-chain milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Public/private dependencies goal: help users catch accidental implementation-detail exposure and help tooling better identify API boundary.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- PubGrub-in-Cargo: richer resolver groundwork for better error messages, better MSRV support, CVE-aware resolution, and more cargo extensions.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Cargo 1.93: publish-time support in resolution summaries and “time traveling dependency resolution”.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo unstable docs: `resolver.feature-unification` and `public-dependency`.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo resolver docs: workspace builds unify dependency features across selected packages; separate invocations may be required to avoid that.
  https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo tree docs: the displayed graph is intentionally closer to the feature-unified build graph than the raw manifest entries.
  https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- Cargo build-performance guide: feature-unification can improve build reuse, which makes feature posture part of workflow economics.
  https://doc.rust-lang.org/cargo/guide/build-performance.html
- November 2025 goals update for cargo-semver-checks: getting dependency features right remains a real blocker with many Cargo edge cases.
  https://blog.rust-lang.org/2025/12/16/Project-Goals-2025-November-Update.md/

## Why this needs its own design layer
The archive already had strong ingredients, but it was still missing the execution discipline needed to keep dependency-control work honest.

Without a shared pilot program, this seam is vulnerable to three bad outcomes:
1. **tree theater** — pretty dependency views without attachable evidence;
2. **feature theater** — lots of feature counts and policy rhetoric without scoped why-chains or unification posture;
3. **boundary theater** — public/private dependency claims or semver judgments made without a portable handoff from actual resolution/feature truth.

A worthy contribution here should prove a smaller and stronger claim:
> Rust projects can attach enough dependency-control evidence that humans and tools can distinguish chosen-graph truth, activated-capability truth, and selection-policy truth.

## Design principles
1. **Pilot lanes, not the whole universe.** Each pilot must have one clear dependency-control subject.
2. **Keep fact layers distinct.** Resolution facts, feature facts, and downstream API/policy conclusions must not silently overwrite one another.
3. **Prefer maintainer pain first.** Surprising version picks, workspace feature unification, and release-boundary confusion beat giant speculative supply-chain analytics.
4. **Use Cargo-native signals whenever available.** Import resolver, feature, and config truth instead of screen-scraping CLI prose.
5. **Preserve split-invocation reality.** When different workspace selections produce different truths, say so explicitly rather than flattening them.
6. **Allow honest incompleteness.** Minimization or what-if search may be partial; reports must say when that happens.

## Shared pilot artifacts
### `dependency-control-brief/v0`
A short declaration of why a lane is being piloted.

Should record:
- pilot id
- lane family (`single-crate`, `workspace-unification`, `boundary-handoff`, `upgrade-policy`, `consumer-import`)
- why this lane matters
- selected toolchain / resolver posture
- intended consumers and success bar

### Core imports from existing kits
- `resolve-report/v0`
- `feature-trace/v0`
- optional `conflict-report/v0`
- optional `resolve-repro/v0`
- `feature-report/v0`
- optional `feature-minset/v0`
- optional public/private dependency declarations and downstream handoff notes

### `dependency-control-pack/v0`
Portable bundle for a specific pilot lane.

Should contain:
- the pilot brief
- one chosen-graph subject
- one selected feature/unification subject
- explicit selection-policy notes (MSRV, publish-time, overrides, split invocation, etc.)
- optional conflict / minimization / reproducer attachments
- review summary and unresolved gaps

Design rule: **this pack is a composition envelope, not a schema that absorbs Resolution Doctor or Feature Kit whole.**

## Ranked rollout

### Pilot 1 — Single-crate graph + feature-why truth
Start with the highest-confidence, most teachable lane.

Artifacts:
- `resolve-report/v0`
- `feature-trace/v0`
- `feature-report/v0`
- `dependency-control-brief/v0`

Success bar:
- a maintainer can explain one surprising dependency or feature activation without ad hoc shell glue;
- the chosen graph and active capabilities are reviewable together;
- ordinary PR review can import the result.

### Pilot 2 — Workspace unification / split-selection lane
Prove the stack handles multi-package reality honestly.

Artifacts:
- per-selection `resolve-report/v0`
- per-selection `feature-report/v0`
- unification-policy note
- optional split-invocation comparison report

Success bar:
- the stack can distinguish “Cargo unified these because you selected them together” from “these members are independently fine”;
- feature drift across workspace selections is attachable instead of anecdotal.

### Pilot 3 — Public/private boundary handoff lane
Connect dependency-control truth to release-boundary consumers without flattening them.

Artifacts:
- resolution / feature reports
- public/private declaration posture
- explicit handoff note to Public API Kit / Policy Kit
- optional `api-exposure-report/v0` pointer

Success bar:
- a maintainer can inspect whether dependency-control truth is aligned with API-boundary expectations;
- the stack can say “handoff needed” without pretending to compute the whole semver answer itself.

### Pilot 4 — MSRV / publish-time / upgrade lane
Attach selection policy to chosen graphs.

Artifacts:
- `resolve-report/v0`
- selection-policy note (MSRV precedence, publish-time fence, upgrade intent, override posture)
- optional `conflict-report/v0`
- optional `resolve-repro/v0`

Success bar:
- time-travel or upgrade investigations can move from folklore to portable issue bundles;
- consumers can see what policy assumptions shaped the graph rather than guessing from CLI flags.

### Pilot 5 — Consumer import lane
Widen only after the core boundary is usable.

Consumers:
- Public API Kit
- Policy / Trust / SBOM / Lifecycle Stack
- Build-State Evidence Stack
- Semantic Context + Edit Workflow Stack
- Support Envelope / Release Pipeline consumers where justified

Success bar:
- consumers import dependency-control artifacts instead of re-deriving chosen graph or feature truth.

## What should count as success overall
The stack is working when:
- chosen versions/sources/overrides are reviewable,
- feature activation and unification are attachable,
- public/private boundary handoffs are explicit,
- MSRV/publish-time/upgrade policy is not hidden in command history,
- and downstream consumers can reuse the evidence without inventing a parallel resolver story.

## Failure modes to avoid
- Starting with a universal dependency-health score.
- Pretending one workspace selection tells the whole truth.
- Treating minimal-feature search as authoritative when it is only best effort.
- Letting policy or semver tools silently redefine resolver truth.
- Jumping straight to giant dashboards before the pack boundary is useful.

## Immediate archive instruction
Treat this file plus [`design/dependency-control-stack.md`](./dependency-control-stack.md) as the shared execution layer above Resolution Doctor Kit and Feature Kit.

The next credible dependency-control move is now a ranked stack program:
1. single-crate graph + feature-why truth,
2. workspace unification / split-selection,
3. public/private boundary handoff,
4. MSRV / publish-time / upgrade,
5. consumer imports.
