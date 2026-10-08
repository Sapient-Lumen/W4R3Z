# Design: Support Envelope Pilot Program (`cargo support pilot`, `support-pilot-pack/v0`)

## Goal
Make the **Support Envelope Kit** executable through a ranked pilot program that starts with honest, high-value support lanes instead of trying to standardize every possible platform/support claim at once.

The archive already has a strong thesis for support contracts:
- support must be lane-specific,
- runtime floors must be explicit,
- docs surfaces are part of support,
- and support drift must become diffable.

What was still missing is the execution layer:
- which support lanes should go first,
- which claims need `cargo build` / `package` / runtime evidence rather than `cargo check`,
- how docs-target truth should relate to real support instead of floating beside it,
- and what a successful support pilot would look like in practice.

A worthy contribution here is **not** another cross-build wrapper, CI matrix generator, or target badge.
It is a disciplined rollout that proves Rust projects can publish **portable support truth** for a few concrete lanes before widening the schema surface.

## References (signals)
- The rustc platform-support book says target support is tiered, with Tier 1 meaning “guaranteed to work” and Tier 2 meaning “guaranteed to build”. It also records platform notes such as minimum kernel / libc floors for mainstream targets.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- Rust 1.91 promoted `aarch64-pc-windows-msvc` to Tier 1 and restated the tier guarantees in release notes. That is a concrete reminder that support posture changes over time and must be diffable.
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- docs.rs metadata already lets crate authors control `default-target`, `targets`, and `additional-targets`, and docs.rs changed its default target list in October 2025. That means docs surfaces are an ecosystem-facing support signal, not just a rendering detail.
  https://docs.rs/about/metadata
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The 2025 State of Rust survey says online documentation remains the canonical reference while editor/agentic tooling is rising, which raises the value of explicit docs-surface truth instead of leaving docs targets implicit.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s `cargo check` policy explicitly says only `cargo build` is covered by Rust’s standard stability guarantee, and that linker errors or monomorphization issues may not appear in `cargo check`. That is crucial for support claims: some lanes need build/package/run evidence, not “check passed”.
  https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- Cargo’s 1.94 development-cycle update reiterates that Cargo plugins matter because Cargo cannot be everything to everyone, which strengthens the case for a `cargo support` companion rather than waiting for one giant built-in feature.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Why this needs its own design layer
The archive already has [`design/compatibility-claims-pilot-program.md`](./compatibility-claims-pilot-program.md), but that pilot deliberately spans both halves of the broader stack:
- Support Envelope Kit for platform/runtime/docs/release support truth
- Acceptance Surface Kit for solver-/borrow-check-sensitive pattern truth

That shared pilot is still right.
But Support Envelope now deserves its **own** execution layer because the support half has become strategically denser:
- target-tier language is evolving,
- docs target defaults are evolving,
- runtime floors matter more as Rust adoption broadens,
- and `cargo check` vs `cargo build` discipline is a real policy boundary.

Without a support-specific pilot layer, this seam risks two bad outcomes:
1. **matrix theater** — projects export bigger and prettier support tables without clarifying lane identity or evidence strength;
2. **artifact drift without review** — runtime floors, docs defaults, and packaging posture change silently between releases.

## Design principles
1. **Pilot support lanes, not “platform support” in the abstract.** Every pilot must say which support lane it is proving.
2. **Prefer claims that users bet real work on.** Released binaries, source-build lanes, and docs defaults matter more than speculative matrix completeness.
3. **Treat docs as a support surface.** Docs target choices and default landing targets are part of what a project is telling users.
4. **Require build/package/run evidence when the lane demands it.** `cargo check` is useful but not sufficient for artifact or runtime claims.
5. **Keep provisioning backend distinct from support status.** `cross`, `zigbuild`, `xwin`, `build-std`, and custom-target-json are evidence about how a lane was attempted, not proof that it is fully supported.
6. **Runtime floors are first-class.** Kernel/libc/SDK/ABI/CPU assumptions must not remain hidden in CI images or maintainer memory.
7. **Support drift must be reviewable.** Raising a runtime floor or changing a docs target is a support change even when the code still compiles.

## Artifact family
### 1. `support-pilot-brief/v0`
Why this support lane is being piloted.

Should record:
- pilot id and summary
- primary lane (`release-artifact`, `source-build`, `docs-surface`, `runtime-floor`, `long-lived-support`)
- why the lane matters now
- why it is tractable now
- intended consumers and decision points

### 2. `support-evidence-policy/v0`
What evidence counts for the pilot.

Should record:
- accepted evidence modes (`check`, `build`, `test`, `package`, `run-smoke`, `field-observed`, `manual-review`)
- which evidence modes are required for the lane
- which evidence modes are advisory only
- what raw attachments are canonical
- how missing evidence is rendered (`unknown`, `partial`, `not-run`, `inconclusive`)

Design rule: **a support claim must not inherit its evidence policy from vibes**.
If a lane requires artifact or runtime truth, encode it.

### 3. `support-docs-profile/v0`
How docs relate to the support contract.

Should record:
- docs.rs `default-target`
- docs.rs `targets`
- docs.rs `additional-targets`
- whether docs targets are `representative`, `compatibility-probe`, or `convenience-only`
- whether the default target is intended as the canonical user entrypoint
- expected docs/render drift rules

Design rule: **docs targets are not a side channel**.
They are part of what users infer about support.

### 4. `support-runtime-floor-profile/v0`
The runtime-floor posture for a pilot.

Should record:
- minimum OS / kernel / libc / CRT / SDK / ABI / CPU assumptions when known
- which of those are maintainer-declared versus observed or derived
- which floors are still unknown
- reason codes for ambiguity
- attachment pointers for symbol/version scans, package metadata, or runner environments

### 5. `support-pilot-scorecard/v0`
Decides whether the pilot worked.

Should ask:
- did the pilot keep lane identity explicit?
- did it require sufficient evidence for the lane?
- did it keep docs posture tied to the support contract?
- did it keep runtime floors explicit or honestly unknown?
- did a real consumer use the result?
- did it produce intentional diffs when the support story changed?

### 6. `support-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- evidence policy
- docs profile
- runtime-floor profile
- support artifacts
- current scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Released-binary support lane
**Why first**
- This is where users most directly rely on support claims.
- Tier guarantees, packaging posture, and runtime floors are immediately relevant.
- It forces the archive to distinguish “we can cross-build it” from “we ship and support it”.

**Core artifacts**
- `support-envelope`
- `support-observation-report`
- `support-evidence-policy`
- `support-runtime-floor-profile`
- `support-diff-report`
- `support-pilot-scorecard`

**Primary consumers**
- release engineering
- downstream packagers
- support/docs pages
- policy and trust tooling

### 2) Source-build / custom-target lane
**Why second**
- Rust’s real-world adoption includes custom-target, `build-std`, and cross-build stories that matter even when no official binary is shipped.
- This is the cleanest place to show that provisioning backend truth is evidence, not the support contract itself.
- It helps prevent support contracts from becoming biased toward only tier-1 desktop artifacts.

**Core artifacts**
- `support-envelope`
- `support-observation-report`
- `support-evidence-policy`
- `support-runtime-floor-profile`
- attachment pointers for `build-std`, custom-target-json, or wrapper backends

**Primary consumers**
- embedded/system projects
- larger build-system integrators
- safety/security review
- ecosystem atlas/navigation surfaces

### 3) Docs-surface lane
**Why third**
- docs.rs defaults and per-crate target choices are now materially part of how users experience crate support.
- The survey’s “docs remain canonical” result makes this more important, not less.
- This pilot proves docs target curation can become explicit support truth instead of an accidental side effect.

**Core artifacts**
- `support-envelope`
- `support-docs-profile`
- `support-observation-report`
- `support-diff-report`
- `support-pilot-scorecard`

**Primary consumers**
- docs maintainers
- users choosing supported platforms
- atlas/recommendation surfaces
- editor/assistant consumers that cite docs

### 4) Runtime-floor derivation lane
**Why fourth**
- Runtime floors are often the most operationally important hidden detail.
- This pilot proves the archive can represent observed, derived, declared, and unknown floors without overclaiming certainty.
- It also gives the release lane more honest footing.

**Core artifacts**
- `runtime-floor-report`
- `support-runtime-floor-profile`
- `support-observation-report`
- `support-diff-report`
- `support-pilot-scorecard`

**Primary consumers**
- release engineering
- distro/ops consumers
- long-lived product teams
- compatibility/policy tooling

### 5) Long-lived / support-window lane
**Why fifth**
- This is where support contracts become operationally serious for real products.
- It ties lifecycle, release truth, support claims, and drift review together.
- It should come after the archive proves the lower-level lanes first.

**Core artifacts**
- `support-envelope`
- `support-diff-report`
- linked lifecycle / release / policy attachments
- `support-pilot-scorecard`

**Primary consumers**
- maintainers supporting multiple release lines
- enterprise / safety-oriented adopters
- policy and succession tooling

## What should wait
Do **not** start by trying to standardize one giant compatibility badge, a universal platform matrix page, or a debugger-support super-manifest.
Those views become useful later, but starting there would pressure the pilot to flatten lane identity, evidence strength, docs posture, and runtime floors too early.

Also avoid claiming that every support lane must immediately include field validation on every platform.
The point of the first pilots is to prove the artifact boundaries and evidence policies, not to simulate infinite CI budget.

## Success bar
A support-envelope pilot should be considered successful when it can show all of the following:
1. a concrete support lane with explicit lane identity;
2. a declared evidence policy matching the lane;
3. docs posture linked to the support contract when relevant;
4. runtime floors explicit or honestly unknown;
5. intentional support diffs between releases or observations;
6. at least one real downstream consumer;
7. no hidden collapse of provisioning backend into support status.

## Why this is an ecosystem contribution
The official Rust signals are unusually aligned now:
- target guarantees remain important but evolve over time,
- docs.rs defaults are changing to reflect platform reality,
- documentation remains canonical even as agentic/editor consumers rise,
- and Cargo policy is explicit that `build`, not `check`, defines the stable compile guarantee.

That combination makes a support-envelope pilot program much more than a documentation nicety.
It is a way to turn platform support from folklore and matrix screenshots into portable, reviewable, diffable evidence.
