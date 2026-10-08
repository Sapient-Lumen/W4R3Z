# Epic proposal: Resolution Strategy Stack

## Why this stack matters now
Rust dependency resolution is no longer one silent "latest wins" choice.
Cargo now has a real MSRV-aware resolver posture, unstable minimal-version validation lanes, active exploration of publish-time and minimum-release-age-style controls, and explicit groundwork for a richer extension ecosystem around resolution itself.

That means the ecosystem gap is bigger than one better explanation command and smaller than a replacement package manager.
The missing layer is a **reviewable strategy boundary** above the chosen graph:
- what objective profile was active,
- what constraints and heuristics shaped the outcome,
- what alternative candidates mattered,
- what tradeoffs were accepted,
- and what downstream consumers may safely import.

The archive already has the ingredients for this:
- [`design/resolution-strategy-kit.md`](../design/resolution-strategy-kit.md)
- [`design/resolution-strategy-stack.md`](../design/resolution-strategy-stack.md)
- [`design/resolution-strategy-pilot-program.md`](../design/resolution-strategy-pilot-program.md)
- [`design/dependency-control-stack.md`](../design/dependency-control-stack.md)
- [`gaps/resolution-strategy-objectives-and-reviewable-lockfile-decisions.md`](../gaps/resolution-strategy-objectives-and-reviewable-lockfile-decisions.md)

What is still missing is the explicit stack-level execution target that says:
> this is not only a good kit idea — it is a coherent ecosystem contribution.

## Why the stack boundary is real
Current upstream signals make this seam stronger than when the archive first introduced the kit:
- the PubGrub-in-Cargo goal explicitly frames the work as groundwork for **better MSRV support, CVE-aware resolution, and a richer ecosystem of Cargo extensions**;
- the Rust 2024 resolver path makes `resolver.incompatible-rust-version = "fallback"` ordinary workspace posture rather than niche nightly lore;
- Cargo’s resolver docs now emphasize that `Cargo.lock` generation happens **as if all features of all workspace members are enabled**, followed by a second pass for actual compile-time features;
- Cargo’s `rust-version` docs keep warning that mixed-policy workspaces are complicated because shared dependencies are unified across policies;
- Cargo’s unstable lane still exposes `minimal-versions` and `direct-minimal-versions`, and keeps `msrv-policy` experimental;
- Cargo 1.93 is actively exploring publish-time-aware resolution and `minimumReleaseAge`-style constraints;
- downstream tooling like `cargo-semver-checks` still reports that active recursive dependency features are not available via the lockfile or any Cargo interface.

Together, those signals mean strategy truth can no longer stay hidden in lockfiles, CI flags, and maintainer folklore.

## Deliverables
### 1) Reference CLI
A thin reference command such as:
- `cargo resolve-plan`
- or `cargo resolution-strategy`

The job is **not** to replace Cargo’s resolver.
The job is to capture, verify, diff, and hand off strategy evidence.

### 2) Stable artifact family
- `resolution-objective/v0`
- `resolution-candidate-report/v0`
- `resolution-decision-report/v0`
- `resolution-strategy-diff/v0`
- `resolution-strategy-pack/v0`

### 3) Required imports
Import rather than recompute:
- `resolve-report/v0`
- `feature-report/v0`
- workspace/config posture
- manifest-truth posture
- toolchain / rust-version posture where relevant

### 4) Downstream handoff adapters
Bounded handoffs for:
- Migration Truth
- Public API / Package Admission
- Policy / Trust
- Support Envelope / Compatibility Claims
- Release / Distribution / Incident consumers

### 5) Ranked pilot execution
Follow the rollout from [`design/resolution-strategy-pilot-program.md`](../design/resolution-strategy-pilot-program.md):
1. direct-minimal validation,
2. workspace multi-MSRV strategy,
3. publish-time / release-age exploration,
4. release-admission / semver handoff,
5. migration / support / policy consumer reuse.

## What makes this epic instead of merely helpful
An epic contribution here would make it normal to review dependency choices with the same seriousness that teams already apply to API diffs, CI results, and release artifacts.

Concretely, it would give Rust:
- lockfile review that preserves **objective and tradeoff truth**;
- multi-MSRV workspace reports that stop living in tribal knowledge;
- a bounded way to compare `latest`, `direct-minimal-check`, `msrv-fallback`, and publish-time-shaped outcomes;
- and a strategy substrate that later Cargo-native work could plausibly import rather than replace.

That is unusually durable ecosystem infrastructure.
It helps maintainers, release reviewers, semver tooling, support engineers, and policy consumers without pretending all of them want the same final verdict.

## Shape of a first credible implementation
A strong first implementation should:
- support a small set of **named profiles** rather than open-ended policy scripting;
- attach imported chosen-graph / feature reports rather than regenerate them;
- allow **bounded candidate comparison** with explicit incompleteness;
- preserve uncertainty around registry history, yanks, and publish-time replay;
- and emit consumer-handoff notes that say what may be reused without silently turning strategy into policy.

That means the first version can already be useful even while Cargo’s own resolution surfaces keep evolving.

## Non-goals
Do not make this:
- a solver fork,
- a universal dependency policy engine,
- a cargo-vet replacement,
- a giant dependency dashboard,
- or a promise that one "best graph" exists for every project.

The narrower and stronger thesis is:
**make dependency-resolution strategy reviewable, portable, and honestly bounded.**
