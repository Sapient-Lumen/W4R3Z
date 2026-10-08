# Design: Dependency Review Stack (Trust Decision + effect audit + runtime capability + artifact linkage)

## Goal
Treat **Trust Decision Stack**, **effect-audit imports**, **Runtime Capability Kit**, and **artifact-linked dependency inventory** as one shared **Dependency Review Stack** for dependency intake and upgrade review.

The missing contribution is not another advisory feed, another crate score, another malware dashboard, another `cargo vet` replacement, or another static-analysis research demo.
It is a portable, reviewable stack that keeps five truths distinct while letting them compose:
- **subject truth** — which crate/version/lockfile/release/binary slice is under review;
- **trust / advisory / policy truth** — what publisher/advisory/freshness/imported-audit facts and local decisions apply;
- **effect-review truth** — what potentially dangerous code paths exist and whether they are safe, unsafe, or caller-checked;
- **runtime-authority truth** — what filesystem/network/process/plugin/runtime powers the reviewed code appears to need if executed;
- **artifact-link truth** — which shipped binaries or release artifacts can be tied back to the reviewed dependency set.

That separation matters because Rust dependency review is rarely one thing:
- sometimes the question is “does this version have a known advisory or trusted audit?”;
- sometimes it is “what dangerous code or side effects are actually here?”;
- sometimes it is “what powers could this code exercise if we ship it?”;
- sometimes it is “can we tie this review to the binary we actually built?”;
- and sometimes it is all four at once.

## Why this seam matters now
Current ecosystem signals are unusually aligned here:
- crates.io now shows RustSec advisories on crate pages, supports GitLab Trusted Publishing, offers Trusted Publishing-only mode, blocks risky GitHub Actions triggers, and exposes `pubtime` in index entries;
- crates.io’s malicious-crate policy now says routine malware removals will always be reflected in RustSec advisories, making durable artifacts more important than broadcast noise;
- Cargo Vet already minimizes review effort, imports trusted audits, computes smallest useful diffs, and treats exemption shrinkage as attack-surface reduction;
- Cargo Scan’s 2026 paper says 69.2% of flagged effects can be decided locally, median review burden can drop to 0.2% of lines of code, 3.5K of the top 10K crates can be auto-classified as safe, and most effects are concentrated in roughly 3% of crates;
- Rust Foundation / Alpha-Omega security work says crate-scanning pilots are underway and a Rust-focused Capslock implementation exists, while the `cargo-capslock` path is already being used to discuss generated seccomp posture for Rust services;
- `cargo-auditable` already embeds dependency-tree JSON into compiled executables and explicitly states that the end goal is Cargo-native binary embedding.

Taken together, ideal Rust needs a more executable story for **dependency intake and upgrade review** than the archive had previously written down.

## What each input lane should own
### Trust Decision Stack
[`design/trust-decision-stack.md`](./trust-decision-stack.md) owns:
- publisher, freshness, advisory, typosquat, and lifecycle-adjacent trust facts;
- local policy decisions, waivers, and thin trust views.

Its question is:
> what trust-relevant facts and policy decisions apply to this dependency subject?

### Effect-audit imports
External lanes such as Cargo Scan own:
- effect model and detection semantics,
- safe/unsafe/caller-checked judgments,
- call-graph-sensitive review artifacts,
- reusable effect-audit files.

Their question is:
> what potentially dangerous code paths exist here, and which require local versus caller-context review?

### Runtime Capability Kit
[`design/runtime-capability-kit.md`](./runtime-capability-kit.md) owns:
- declared authority surfaces,
- inferred powers,
- candidate/generated enforcement,
- deployed enforcement and checks.

Its question is:
> if this code runs, what powers does it appear to need or exercise?

### Artifact-linked inventory / binary linkage
[`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md), `cargo-auditable`, and related inventory lanes own:
- dependency inventory capture,
- package ↔ artifact linkage,
- binary-recovered dependency truth,
- format projection and lossiness notes.

Their question is:
> which built artifacts actually correspond to the reviewed dependency set?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without juggling crates.io tabs, RustSec links, `cargo vet`, research prototypes, binary scanners, and release notes:
1. What exact dependency subject is under review?
2. What trust/advisory/publisher facts and local policy decisions apply?
3. What dangerous effects or caller-checked paths were found?
4. What runtime authority or least-privilege posture is implied?
5. What artifact or binary linkage exists for the reviewed subject?
6. What changed versus the previous reviewed point?
7. What may a PR/release/policy/assistant consumer safely summarize?

If the stack cannot answer those seven questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs both a ranked execution layer and an explicit epic candidate, captured in:
- [`design/dependency-review-pilot-program.md`](./dependency-review-pilot-program.md)
- [`proposals/epic-dependency-review-stack.md`](../proposals/epic-dependency-review-stack.md)

That pilot program should prove the stack in this order:
1. **lockfile / version-bump review lane**
2. **effect-attached review lane**
3. **capability-attached review lane**
4. **artifact / binary attachment lane**
5. **PR / release / policy / assistant consumer lane**

That ordering is intentional.
The archive should not jump straight to a giant supply-chain portal, a universal allowlist, or a fake one-number dependency health score.
It should first prove that Rust projects can publish enough dependency-review truth to make ordinary dependency intake and upgrade review honest.

## Design principles
1. **The reviewed subject comes first.** Do not start from aggregated ecosystem scores.
2. **Trust facts are not effect facts.** An advisory-free crate can still deserve effect review.
3. **Effect review is not capability review.** Dangerous code and authority posture are linked but not identical.
4. **Artifact linkage stays explicit.** Reviewing a lockfile is not yet the same as reviewing a shipped binary.
5. **Waivers remain visible.** Local decisions should not silently rewrite imported evidence.
6. **Thin consumers come last.** PR badges, registry hints, release notes, and assistants must import bounded conclusions.

## What an epic contribution would look like in practice
A serious contribution here now looks like a thin `cargo dep-review` / `dependency-review-pack/v0` layer that links trust-decision evidence, effect-review evidence, capability evidence, and artifact linkage without flattening them.

Concretely, it should:
- attach crates.io/RustSec/Trusted-Publishing/pubtime facts without turning them into the whole decision;
- import `cargo vet` and effect-review artifacts rather than replacing them;
- let Capslock-style capability analysis remain explicit and optional where coverage is partial;
- cross-link package review to binary or release inventory where available;
- make upgrade review diffable instead of re-reading issue comments and shell transcripts;
- and give PR, security, release, policy, and assistant consumers a bounded handoff artifact.

## Anti-goals
Do not turn this stack into:
- one universal supply-chain score,
- one mandatory approval registry,
- one `cargo vet` successor,
- one malware-only detector,
- or one giant hosted security portal.

The stack is a **review boundary**, not a replacement for advisories, vetting tools, effect analyzers, capability analyzers, or inventory tools.
