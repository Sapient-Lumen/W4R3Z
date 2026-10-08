# Design: Preview Adoption Stack (Baseline Ratchet + Migration Truth + Workspace Environment + Canonical Learning)

## Goal
Treat **preview/unstable Rust usage** as a first-class ecosystem seam.

Rust projects increasingly need to do real work with things that are **not yet fully stable**:
- nightly language feature gates,
- nightly Cargo `-Z` flags and `cargo-features`,
- unstable edition previews,
- beta-channel validation before a stable release,
- unstable rustdoc/test/build-std pathways,
- and targeted feature experiments that need a credible path either to stabilization or to removal.

Today those choices are usually smeared across `rust-toolchain.toml`, ad hoc `#![feature(...)]` lists, CI YAML, tracking-issue links in PRs, internal upgrade folklore, and “just use nightly for now” README notes.
The missing contribution is therefore **not** another feature-tracker dashboard, another nightly distro, another generic “use stable unless you must” essay, or another one-off migration guide.
It is a thin `cargo previewadopt` / `preview-pack/v0` layer that keeps these truths separate:
- **preview subject truth** — which unstable feature / edition preview / Cargo flag / rustdoc or compiler pathway is actually in use;
- **activation truth** — which channel, toolchain pin, `cargo-features`, `-Z` flags, `#![feature(...)]`, components, or environment assumptions activate it;
- **adoption scope truth** — which packages, targets, branches, CI jobs, contributors, or downstream users are expected to cross that unstable boundary;
- **guardrail truth** — which fallback, support boundary, non-goals, risk posture, or “do not publish / do not promise” rules apply while the preview is live;
- **watch/landing truth** — which tracking issues, release notes, beta-testing lanes, stabilization blockers, or removal triggers are being watched;
- **exit/handoff truth** — whether the preview is meant to land on stable, remain quarantined to a local/dev-only lane, or be removed, and which Baseline Ratchet / Migration Truth / Compatibility / docs consumers may later import the result.

The point is to stop treating “we use nightly for this” as one blob.

## Why this seam matters now
Official Rust/Cargo signals are unusually aligned here:
- The Rust book’s release-train appendix says Rust releases every six weeks, explicitly encourages using beta to catch regressions before stable, and explains that unstable features land in nightly behind feature flags while stable/beta deliberately reject them. That means preview usage is a real designed lane, not an embarrassing exception.
  https://doc.rust-lang.org/book/appendix-07-nightly-rust.html
- Cargo’s unstable-features docs say nightly-only features are there for experimentation, require explicit activation (`cargo-features`, `-Z unstable-options`, or `-Z` flags), recommend checking tracking issues, and describe stabilization as a separate later step. That is already a control-plane surface, just not a reviewable one.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The Unstable Book says its docs are best-effort and may be inaccurate or out of date and tells readers to consult each feature’s tracking issue for the latest developments. That is direct evidence that a project using unstable Rust needs an explicit watch/landing layer instead of assuming the docs themselves are the durable contract.
  https://doc.rust-lang.org/unstable-book/
- The Edition Guide says that during the roughly three-year window before the next edition, new edition features may be tested on nightly, require explicit `cargo-features`, and may not yet have automatic migrations or a finished design. That means “previewing the next edition” is not just another migration run.
  https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
- The 2025 State of Rust survey says most people use stable and keep up with releases, while nightly use is mostly out of necessity. That means unstable adoption should be treated as a constrained exception with an honest boundary, not as the invisible default.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2024 State of Rust survey says almost a third of users used nightly, mostly to access unstable language features, and explicitly encourages beta use in CI because it is underused. It also says a material share of users want features stabilized faster. That combination means the ecosystem has real demand for previews but weak shared machinery for managing them.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Rust-for-Linux’s stable-support goals say unstable features have no reliability guarantee and that dependence on them is a blocker because it forces specific pinned compiler versions. That is the clearest proof that preview usage must stay separable from long-term support claims.
  https://rust-lang.github.io/rust-project-goals/2024h2/rfl_stable.html
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Several active goals are explicitly framed as **nightly experiments with a path toward stabilization** or as unstable features seeking an MVP suitable for stabilization: scalable vectors / SVE, `build-std`, and more. That means the “preview → stabilized or retired” route is no longer niche; it is part of Rust’s strategic motion.
  https://rust-lang.github.io/rust-project-goals/2025h1/arm-sve-sme.html
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html

Taken together, ideal Rust needs a reviewable layer for **preview adoption** above raw unstable feature switches and below baseline ratchets, migration programs, compatibility claims, and public support language.

## What belongs in preview subject truth
Not every project needs every field, but the stack should be able to name them explicitly:
- language features behind `#![feature(...)]`;
- Cargo `-Z` flags and `cargo-features` syntax;
- unstable edition previews;
- nightly-only rustdoc / libtest / build-std / sanitizer / codegen lanes;
- beta-validation lanes for soon-to-stabilize behavior;
- pinned toolchain / component assumptions tied specifically to the preview.

A project does not become more honest by treating these as just “toolchain details”.

## What each neighboring stack owns
### Baseline Ratchet Stack
[`design/baseline-ratchet-stack.md`](./baseline-ratchet-stack.md) owns:
- current stable floor,
- proposed ratchet delta,
- workspace variance,
- verification matrix,
- release-line policy.

Its question is:
> what supported baseline are we claiming now or next?

The Preview Adoption Stack should feed Baseline Ratchet only when the preview actually lands or is intentionally policy-carrying.

### Migration Truth Stack
[`design/migration-truth-stack.md`](./migration-truth-stack.md) owns:
- source state,
- destination intent for a concrete transition,
- selected edits,
- executed checks,
- outcome receipts.

Its question is:
> what concrete transition program ran?

The Preview Adoption Stack owns the period **before** or **around** stabilization where the project is still carrying unstable assumptions.

### Workspace Environment Stack
[`design/workspace-environment-stack.md`](./workspace-environment-stack.md) owns:
- local realization in toolchain/config/editor/credentials/runtime terms,
- actual machine setup,
- activation mechanics.

Its question is:
> how is this preview actually realized on developer and CI machines?

It should realize preview choices, not silently define their policy.

### Canonical Learning / Compile Guidance
[`design/canonical-learning-stack.md`](./canonical-learning-stack.md) and [`design/compile-guidance-kit.md`](./compile-guidance-kit.md) own:
- user-facing explanation,
- examples,
- official-looking guidance,
- diagnostic help.

Their question is:
> how do we explain the preview honestly without laundering it into default Rust?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. Which preview subject is actually being used?
2. How is it activated and pinned?
3. Who is expected to cross that boundary — all users, only CI, only maintainers, only one package, only one branch?
4. What support/publication/fallback guardrails apply while it remains unstable?
5. What upstream watchpoints and landing/removal triggers exist?
6. What happens next: stable landing, local quarantine, or removal?

If the stack cannot answer those six questions, it is still just unstable-feature folklore.

## Recommended execution posture
The archive should prefer a ranked rollout like this:

### 1. Single preview feature with explicit quarantine
Prove the stack on one unstable language or Cargo feature used only in a bounded scope, with explicit “not part of public support guarantee” language.

### 2. Beta validation lane
Prove that upcoming stable behavior can be tested in CI or release prep without being confused with current stable policy.

### 3. Edition-preview lane
Prove that unstable next-edition work can be represented as preview subject + guardrails + watchpoints instead of being flattened into a migration run.

### 4. Tooling / compiler-option preview lane
Prove that unstable build-std / rustdoc / sanitizer / target-feature experiments can keep activation details, risk posture, and exit criteria visible.

### 5. Stable landing or retirement handoff
Only after the above are explicit should a preview produce a Baseline Ratchet, Migration Truth program, Compatibility claim update, or public docs/support language.

That order matters.
The archive should not jump straight from one nightly experiment to “this is now part of our supported Rust platform.”

## Design principles
1. **Preview subject first.** Do not start with the pinned toolchain before naming what is being previewed.
2. **Activation is not policy.** `rust-toolchain.toml`, `-Z`, and `#![feature]` lines are realization details until the policy is made explicit.
3. **Scope stays explicit.** One nightly-only maintainer task is not the same as asking downstream users to use nightly.
4. **Guardrails stay visible.** Publishing, support promises, package admission, and compatibility claims must know whether a preview is quarantined or public.
5. **Watchpoints matter.** Tracking issues, release notes, beta testing, and stabilization blockers are part of the seam, not optional trivia.
6. **Exit posture must exist.** Every preview should point toward stable landing, bounded long-term quarantine, or removal.
7. **Downstream consumers inherit bounded authority.** Docs, support pages, release notes, compatibility claims, and baseline ratchets should import preview facts rather than improvising them.

## What an epic contribution would look like in practice
A serious contribution here would publish a compact artifact family such as:
- `preview-subject/v0` — unstable feature / edition-preview / Cargo-flag identity and scope
- `preview-activation/v0` — channel pin, toolchain, `cargo-features`, `-Z` flags, `#![feature]`, components, env assumptions
- `preview-guardrail/v0` — support/publication boundary, fallback, explicit non-goals, audience
- `preview-watch/v0` — tracking issues, relevant release notes/goals, beta-testing posture, stabilization blockers, review cadence
- `preview-exit-handoff/v0` — stable-landing receipt, quarantine renewal, or removal / ratchet / migration handoff

That contribution should:
- consume official tracking-release-goal material instead of mirroring it into another dashboard,
- keep nightly/beta/stable lanes visibly different,
- make public-support consequences explicit,
- and let Baseline Ratchet / Migration Truth / Compatibility / docs consumers import only what is actually justified.

## Anti-goals
Do not turn this stack into:
- one feature-tracker portal,
- one “use nightly safely” brand package,
- one magical auto-stabilization watcher,
- one policy that forbids all previews everywhere,
- or one generic migration guide that forgets the preview period ever existed.

The stack is a **review boundary for preview adoption**, not a replacement for Rust’s release train or stabilization process.
