# Epic Proposal: Dependency Control Stack (`cargo dependency-control` + `dependency-control-pack/v0`)

## One-sentence pitch
Make Rust dependency behavior boring by standardizing a portable layer that keeps **chosen graph facts, feature-activation facts, selection-policy facts, and public/private-boundary handoffs** distinct instead of forcing every tool to tell its own partial dependency story.

## Deliverables
- reference command:
  - `cargo dependency-control`
- schemas:
  - `dependency-control-brief/v0`
  - `dependency-control-pack/v0`
  - `dependency-control-diff/v0`
  - `dependency-control-handoff/v0`
  - `selection-policy-report/v0`
  - `boundary-handoff-report/v0`
- adapters/importers for:
  - `resolve-report/v0`
  - `feature-trace/v0`
  - `feature-report/v0`
  - optional `conflict-report/v0`
  - optional `resolve-repro/v0`
  - public/private dependency declarations and boundary posture imports
  - workspace-selection and config imports where feature unification or split invocation matter
- docs:
  - chosen-graph vs activated-capability guide
  - workspace-unification vs split-invocation guide
  - public/private dependency handoff guide
  - MSRV / publish-time / upgrade-policy guide
  - consumer-lossiness guide for API / policy / build-state / SBOM imports

## Why now (signals)
- Rust’s 2026 flagship slate keeps **public/private dependencies** and **SBOM support** active under the secure-supply-chain work, which means dependency-boundary meaning is now part of first-party roadmap work rather than optional ecosystem polish.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private dependencies goal exists specifically to help users catch accidental implementation-detail exposure and help tooling identify what constitutes an API. That is a direct argument for keeping graph truth and API-boundary handoff explicit.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- The PubGrub-in-Cargo goal is not merely an implementation cleanup: it explicitly frames the work as groundwork for better error messages, better MSRV support, CVE-aware resolution, and a richer ecosystem of Cargo extensions. That is a strong signal that the missing contribution is above the resolver, not another resolver fork.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Cargo 1.93 reports that dependency resolution is gaining publish-time support in the registry summary format and discusses “time traveling dependency resolution”. That makes selection policy and replay posture part of ordinary dependency reasoning.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s unstable docs now expose `resolver.feature-unification`; without `-Z feature-unification` the config is ignored, but with it the workspace’s feature-unification posture becomes a reviewable configuration seam instead of folklore.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo’s resolver docs are explicit that workspace builds unify features across selected packages and that separate Cargo invocations may be needed to avoid that unification. That means workspace package selection and capability activation are already coupled in user-visible ways.
  https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo’s build-performance guide says feature-unification can increase dependency-build reuse. That means feature posture is not just semantic surface area; it also changes workflow economics.
  https://doc.rust-lang.org/cargo/guide/build-performance.html
- Cargo’s `rust-version` docs say multiple policies in one workspace can make verification complicated because shared dependencies are still unified across policies. That ties dependency control directly to support-policy reality.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo’s feature docs explicitly warn that default features can be hard to keep off when a dependency appears multiple times in the graph. That is a direct signal that activation truth must remain attachable instead of hidden inside ad hoc debugging.
  https://doc.rust-lang.org/cargo/reference/features.html

## Non-goals
- replacing Cargo’s resolver or becoming a second package manager;
- promising one universal minimal-feature or latest-version policy;
- flattening chosen graph, activated capabilities, and public API exposure into one score;
- pretending publish-time replay, upgrade exploration, and ordinary workspace builds are the same lane;
- making Public API / Policy / Trust / SBOM consumers re-exported clones of dependency-control truth.

## Strategic value
This deserves promotion because it gives the archive a missing **dependency continuity seam**.
With it:
- maintainers can review what Cargo actually selected without losing why capabilities turned on;
- feature-unification and split-invocation tradeoffs can be attached to ordinary review instead of living in shell history and CI folklore;
- public/private dependency posture can become an explicit handoff rather than an inferred afterthought;
- API, policy, build-state, semver, SBOM, and support consumers can import one pack and state their lossiness explicitly;
- future resolver improvements can land underneath a stable review boundary instead of every tool rebuilding a private explanation layer.

The prize is not a nicer dependency tree.
The prize is a durable record of **what Cargo chose, why capabilities turned on, what policy shaped that result, and what downstream tools may honestly conclude next**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `dependency-control-brief/v0` the canonical declaration of subject, lane family, resolver/toolchain posture, and intended consumers;
2. import `resolve-report/v0` as the canonical chosen-graph / source / override / conflict boundary;
3. import `feature-trace/v0` and `feature-report/v0` as the canonical activation / why-chain / unification boundary;
4. make `selection-policy-report/v0` the canonical attachment for MSRV, publish-time, override, upgrade, and workspace-selection posture;
5. make `boundary-handoff-report/v0` the canonical handoff to Public API / Policy / Admission consumers for public/private dependency interpretation;
6. emit `dependency-control-pack/v0`, `dependency-control-diff/v0`, and `dependency-control-handoff/v0` so downstream stacks can import dependency facts without silently re-deriving them.

## Critical design bet
The critical bet is that **dependency control becomes useful before Cargo settles every future resolver, MSRV, or policy question**.
That means:
- chosen-graph facts are still worth preserving while resolver internals evolve,
- activation facts are still worth preserving while feature-unification controls remain unstable,
- policy notes can attach without pretending they are the solver,
- public/private dependency posture can stay a downstream handoff instead of being forced into one giant dependency schema,
- and consumer tools can already benefit from portable lossiness reports even while some first-party dependency-boundary features are still stabilizing.

Without that boundary, the stack either stays too thin to matter or bloats into a fake one-true dependency platform.

## Milestones
1. **v0 subject + chosen-graph lane**
   - `dependency-control-brief/v0`
   - imports from `resolve-report/v0`
   - single-crate examples
2. **v0.2 activation / feature-why lane**
   - imports from `feature-trace/v0` and `feature-report/v0`
   - explicit unification / split-invocation notes
3. **v0.3 boundary-handoff lane**
   - `boundary-handoff-report/v0`
   - public/private dependency posture imports
4. **v0.4 policy lane**
   - `selection-policy-report/v0`
   - MSRV / publish-time / upgrade / override posture
5. **v1 consumer handoffs**
   - `dependency-control-pack/v0`, `dependency-control-diff/v0`, `dependency-control-handoff/v0`
   - API / semver / policy / build-state / SBOM / support consumers

## Execution order
Use [`design/dependency-control-pilot-program.md`](../design/dependency-control-pilot-program.md) as the stack-level rollout:
1. single-crate graph + feature-why lane,
2. workspace unification / split-selection lane,
3. public/private boundary handoff lane,
4. MSRV / publish-time / upgrade lane,
5. consumer-import lane.

Use [`proposals/epic-resolution-doctor-kit.md`](./epic-resolution-doctor-kit.md) and [`proposals/epic-feature-kit.md`](./epic-feature-kit.md) as the leaf-level execution guides beneath it.

## Success metrics
- maintainers can distinguish chosen graph, activation why-chains, and policy posture without reading Cargo source or replaying shell history;
- workspace selections can explain when feature unification changed behavior and when separate invocations are required;
- public/private dependency posture can be handed off to API and policy tooling without silently redefining resolver truth;
- consumer stacks can import `dependency-control-pack/v0` and say what they omitted or transformed;
- the ecosystem gets one explainable dependency continuity seam instead of multiple incompatible partial views.
