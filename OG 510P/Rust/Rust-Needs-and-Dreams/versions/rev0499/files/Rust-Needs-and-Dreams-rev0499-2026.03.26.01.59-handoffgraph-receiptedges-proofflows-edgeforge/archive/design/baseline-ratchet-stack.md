# Design: Baseline Ratchet Stack (Migration Truth + Compatibility Claims + Lifecycle Ledger + Release Truth)

## Goal
Treat **project baseline changes** as a first-class ecosystem seam.

Rust projects keep making consequential support-floor decisions:
- raising `edition`,
- raising `rust-version`,
- opting into or out of resolver behavior,
- changing toolchain pinning,
- splitting development and maintenance branches,
- and deciding whether “latest dependencies”, published manifests, and local repo state are meant to track the same baseline.

Today those choices are usually smeared across PR descriptions, CI YAML, `Cargo.toml` edits, `rust-toolchain.toml`, `cargo fix` runs, release notes, and maintainer memory.
The missing contribution is therefore **not** another upgrader, another CI matrix template, another “should I bump MSRV?” blog post, or another policy argument hidden in release notes.
It is a thin `cargo ratchet` / `baseline-pack/v0` layer that keeps these truths separate:
- **current baseline truth** — which edition / `rust-version` / resolver / toolchain / manifest-parse expectations / release lines are active now;
- **ratchet intent truth** — which floor is being raised, why, for which packages or branches, and with which explicit non-goals;
- **workspace variance truth** — which members, targets, features, or maintained release lines intentionally remain on older policies;
- **verification truth** — which CI matrix, latest-deps, MSRV, docs, and package/release checks actually exercised the new baseline;
- **migration truth** — which code/config edits and upgrade receipts were part of the change program;
- **consumer handoff truth** — what later support, lifecycle, package-admission, release, or adoption consumers may now honestly claim.

The point is to stop treating “we bumped the baseline” as one blob.

## Why this seam matters now
Official Rust/Cargo signals are unusually aligned here:
- Rust 1.85 stabilized **Rust 2024**, and the Edition Guide says edition migration is staged: `cargo fix --edition` runs lint-driven edits and may need repeated runs, multiple configurations, and manual help before you finally change `Cargo.toml` to the new edition.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo’s `rust-version` docs make MSRV policy much more explicit than older folklore. They say changing `rust-version` is assumed to be a minor incompatibility, recommend choosing and documenting a policy, explain that drift from policy creates user confusion, and note that workspaces can intentionally have multiple policies.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Rust 1.84 stabilized MSRV-aware dependency selection, says resolver `3` can require raising your MSRV, and says projects on the 2024 edition get the new resolver behavior by default. That means edition choice, resolver choice, and MSRV policy are now coupled in a way many older upgrade guides did not need to model.
  https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/
- The resolver docs say mixed-policy workspaces are only handled heuristically: one member’s Rust version can force lower versions for another member, or version unification can still force a higher shared version. That is direct evidence that “the workspace baseline” and “each member’s baseline” must stay separate.
  https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo’s CI guide now explicitly documents two adjacent but distinct checks: **verifying latest dependencies** and **verifying `rust-version`**. That means baseline review is no longer just “does the lockfile build?” but also “what happens when we test the newest compatible graph, and what do we claim as our floor?”
  https://doc.rust-lang.org/cargo/guide/continuous-integration.html
- Cargo 1.94 adds another sharp edge: TOML 1.1 support means users can accidentally write manifests that require a newer Cargo parser, and the Cargo team explicitly points to verifying `rust-version` in CI as a mitigation. The same post also shows Cargo still working through workspace/config discovery because broken parent files can poison unrelated builds.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The 2025 State of Rust survey says people mostly develop on stable and keep up with releases, while nightly is used out of necessity. That means baseline ratchets are not edge-case niche maintenance work; they are part of ordinary stable-first Rust life.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, ideal Rust needs a reviewable layer for **baseline ratchets** above one-off migration mechanics and below broad release/support lore.

## What belongs in the baseline vector
Not every project uses every field, but the stack should be able to name them explicitly:
- crate or workspace **edition**;
- declared **`rust-version`** policy;
- resolver family / precedence posture where relevant;
- pinned or inherited **toolchain** posture (`rust-toolchain.toml`, CI channel assumptions, beta/nightly test lanes);
- authored-manifest versus published-manifest **parse-floor** assumptions where relevant;
- active **release lines** and which of them intentionally preserve older support floors;
- latest-deps / lockfile / scheduled-update posture for baseline verification.

A project does not become more honest by pretending these always move together.

## What each neighboring stack owns
### Migration Truth Stack
[`design/migration-truth-stack.md`](./migration-truth-stack.md) owns:
- source state,
- destination intent for a specific migration program,
- selected edits,
- executed checks,
- outcome receipts.

Its question is:
> what concrete transition program ran?

### Compatibility Claims + Support Envelope
[`design/compatibility-claims-stack.md`](./compatibility-claims-stack.md) and [`design/support-envelope-kit.md`](./support-envelope-kit.md) own:
- source-build/runtime/docs/debug/support claims,
- observed compatibility evidence,
- support diff reports.

Their question is:
> what compatibility/support claims does this baseline actually justify?

### Lifecycle Ledger
[`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md) owns:
- maintained release lines,
- support windows,
- deprecations,
- successor and handoff posture.

Its question is:
> which lines remain supported, for how long, and by whom?

### Release Truth Stack
[`design/release-truth-stack.md`](./release-truth-stack.md) owns:
- what release artifacts were produced,
- what release notes and receipts existed,
- what publication/distribution facts happened.

Its question is:
> what did we actually ship and announce?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What is the current baseline vector?
2. Which part of that vector is being ratcheted, and why now?
3. Which packages, targets, or maintained branches intentionally remain on an older floor?
4. Which verification lanes actually tested the new floor and latest-deps consequences?
5. Which concrete migration artifacts back the ratchet?
6. Which release/support/lifecycle claims are now justified — and which are still out of scope?

If the stack cannot answer those six questions, it is still just upgrade folklore.

## Recommended execution posture
The archive should prefer a ranked rollout like this:

### 1. Single-package edition + MSRV ratchet
Prove the stack on one package changing edition and/or `rust-version` with explicit CI evidence and explicit non-goals.

### 2. Workspace mixed-policy ratchet
Prove that a workspace can describe one member lagging behind or a maintenance tool/package staying on an older floor without laundering that into the whole workspace story.

### 3. Development-branch vs maintained-release-line split
Prove that “main is on a newer floor, release branch remains older” can be represented cleanly instead of living only in tribal knowledge.

### 4. Latest-deps and parser-floor lane
Prove that lockfile stability, latest compatible dependencies, and manifest/parser floor assumptions can remain visible rather than silently coupled.

### 5. Release / support / package-admission handoff
Only after the above are reviewable should the ratchet become an input to release announcements, support pages, package-admission policy, or adoption overlays.

That order matters.
The archive should not jump straight to one magical “raise baseline safely” bot.

## Design principles
1. **Baseline vector first.** Do not start with the diff before naming the floor.
2. **Ratchet intent is not the migration run.** A policy change may survive multiple partial migration attempts.
3. **Workspace variance stays explicit.** One member or branch lagging behind is not failure; hiding it is.
4. **Verification lanes stay named.** MSRV checks, latest-deps checks, docs/package checks, and release receipts are related but not interchangeable.
5. **Release lines matter.** Development-branch policy and maintained-release-line policy should not be collapsed.
6. **Published and authored floors can differ.** Local repo syntax and published manifest/parser expectations may diverge; preserve that fact instead of narrating one fake parse floor.
7. **Downstream consumers inherit bounded authority.** Release notes, support pages, package-admission decisions, and adoption briefs should import the ratchet rather than reinvent it.

## What an epic contribution would look like in practice
A serious contribution here would publish a compact artifact family such as:
- `baseline-vector/v0` — current edition / `rust-version` / resolver / toolchain / release-line posture
- `baseline-ratchet-intent/v0` — proposed delta, reasons, affected packages/branches, explicit non-goals
- `baseline-variance-map/v0` — members, targets, or release lines intentionally on different floors
- `baseline-verification-report/v0` — MSRV/latest-deps/docs/package/release checks and their outcomes
- `baseline-ratchet-report/v0` — the linked human review bundle importing migration, compatibility, lifecycle, and release evidence
- `baseline-pack/v0` — checksummed pointer set linking all of the above

That contribution should:
- compose with `cargo fix`, `cargo update`, CI jobs, and maintenance branches rather than replacing them;
- make edition / MSRV / resolver / toolchain changes discuss the same subject;
- let support and release consumers import explicit baseline truth instead of scraping release notes;
- and make it possible to say “main moved, release/1.x did not” without hand-written archaeology.

## Anti-goals
Do not turn this stack into:
- one universal MSRV policy,
- one “always latest Rust” manifesto,
- one upgrade bot that silently edits manifests and branches,
- one fake compatibility score,
- or one release note template pretending to be the source of truth.

The stack is a **review boundary for support-floor change**, not a replacement for migration tooling, CI, or maintainer judgment.
