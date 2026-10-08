# Design: Dependency Control Stack (Resolution Doctor + Feature Kit)

## Goal
Treat **Resolution Doctor Kit** and **Feature Kit** as one shared **Dependency Control Stack**.

The missing contribution is not another tree viewer, another lockfile diff, another “why is this feature on?” FAQ page, or another resolver fork.
It is a portable, reviewable stack that keeps three kinds of dependency truth distinct while letting them compose:
- **selection truth** — which packages, versions, sources, overrides, and constraints actually won;
- **activation truth** — which features and optional dependencies became active, in which scope, and why;
- **control truth** — which unification, MSRV, publish-time, and public/private-boundary choices shaped the graph.

That separation matters because Rust dependency pain is rarely one thing:
- sometimes the problem is a **surprising version choice**,
- sometimes it is **feature creep or workspace-wide unification**,
- sometimes it is a **boundary mistake** around what is public versus private,
- and sometimes it is all three at once.

## Why this seam matters now
Current official Rust/Cargo signals are unusually aligned here:
- Rust’s 2026 flagship slate keeps **Secure your supply chain** active, with milestones around stabilizing public/private dependencies and SBOM support.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private dependencies goal exists specifically to help users catch accidental implementation-detail exposure and help tooling identify what constitutes an API.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Cargo 1.93 says dependency resolution now has publish-time data support in the registry summary format and discusses “time traveling dependency resolution” as a user-facing exploration path.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s unstable docs now expose `resolver.feature-unification`, which means workspace-level unification policy is becoming a reviewable configuration seam instead of pure folklore.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo’s resolver docs are explicit that workspace builds unify features across selected packages and that separate Cargo invocations are required when you need to avoid that unification.
  https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo’s feature docs and build-performance guidance both treat feature posture as a real cost and reuse concern, not a cosmetic manifest detail.
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/guide/build-performance.html
- The PubGrub-in-Cargo goal explicitly frames richer resolver behavior as groundwork for better error messages, better MSRV support, CVE-aware resolution, and a richer ecosystem of Cargo extensions.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html

Taken together, that means ideal Rust needs a more executable story for dependency control than the archive had previously written down.

## What each kit owns
### Resolution Doctor Kit
[`design/resolution-doctor-kit.md`](./resolution-doctor-kit.md) owns:
- chosen packages, versions, and sources,
- constraint and conflict explanations,
- override and replacement posture,
- selected build-context graph identity,
- minimized reproducer export.

Its question is:
> what graph did Cargo actually choose, and why?

### Feature Kit
[`design/feature-kit.md`](./feature-kit.md) owns:
- enabled features and optional dependencies,
- why-chains for activation,
- unification-sensitive deltas,
- minimization/search posture,
- org-level feature policy.

Its question is:
> given the chosen graph, which capabilities turned on, in what scope, and who requested them?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without juggling `cargo tree`, unstable flags, resolver lore, CI shell glue, and semver/policy guesswork:
1. Which packages/versions/sources were selected?
2. Which constraints, overrides, or publish-time / MSRV settings shaped that selection?
3. Which features and optional dependencies became active, and why?
4. Which activations are due to normal runtime use versus dev/build/proc-macro/target/workspace context?
5. Which public/private dependency declarations or API-boundary consumers are likely to care next?
6. Which downstream consumers can import the result without re-inventing dependency truth?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.


## Proposal-layer candidate
The stack now has an explicit proposal-layer candidate in:
- [`proposals/epic-dependency-control-stack.md`](../proposals/epic-dependency-control-stack.md)

That epic intentionally stays above the leaf kits.
It does **not** try to replace Resolution Doctor or Feature Kit; it turns their facts plus boundary/policy attachments into one portable review layer.

## Recommended execution posture
The stack now needs a shared execution layer, captured in:
- [`design/dependency-control-pilot-program.md`](./dependency-control-pilot-program.md)
- [`design/resolution-strategy-stack.md`](./resolution-strategy-stack.md)

The dependency-control rollout still matters first, but the archive should now treat **Resolution Strategy Stack** as the layer immediately above it whenever revisions are about *why this graph was targeted at all* rather than merely *what graph and features Cargo selected*.

That pilot program should prove the stack in the following order:
1. **single-crate graph + feature-why lane**
2. **workspace unification / split-selection lane**
3. **public/private boundary handoff lane**
4. **MSRV / publish-time / upgrade lane**
5. **consumer-import lane**

That ordering is intentional.
The archive should not jump straight to universal lockfile policy, giant dependency dashboards, or a fake “dependency health” score.
It should first prove that Rust projects can publish enough dependency-control evidence to explain ordinary maintainer decisions honestly.

## Design principles
1. **Chosen graph facts come before advice.** A consumer should not have to trust a suggestion engine to know what Cargo selected.
2. **Version/source truth and feature truth stay separate.** They interact, but neither should silently overwrite the other.
3. **Selection policy is first-class.** MSRV precedence, publish-time limits, overrides, and unification posture are part of the subject, not incidental CLI trivia.
4. **Public/private boundary truth is a handoff, not a collapse.** Dependency-control artifacts should inform Public API / Policy consumers without pretending to be the release boundary themselves.
5. **One stack, many consumers.** Public API, semver, policy, build-state, semantic-context, and support tooling should be able to import the same dependency evidence.
6. **Minimization and what-if exploration are optional layers.** Baseline reporting should work even when search/minimization is expensive or inconclusive.

## What an epic contribution would look like in practice
A serious contribution here would:
- publish a stack-level `dependency-control-pack/v0` and `dependency-control-handoff/v0` boundary instead of leaving composition to one-off CI glue;
- import Cargo-native resolver and feature-unification signals instead of replacing them;
- make feature creep and version drift attachable to ordinary PR/release review;
- give Public API / Policy / SemVer consumers a stable handoff instead of bespoke resolver reimplementation;
- preserve workspace-wide unification and split-invocation tradeoffs honestly;
- and make MSRV/publish-time/upgrade decisions easier to inspect without turning the stack into a solver fork.

## Anti-goals
Do not turn this stack into:
- one giant dependency score,
- one universal minimal-feature promise,
- one cargo-resolver replacement project,
- or a premature standardization of every what-if graph.

The stack is a **review boundary**, not a new package manager.
