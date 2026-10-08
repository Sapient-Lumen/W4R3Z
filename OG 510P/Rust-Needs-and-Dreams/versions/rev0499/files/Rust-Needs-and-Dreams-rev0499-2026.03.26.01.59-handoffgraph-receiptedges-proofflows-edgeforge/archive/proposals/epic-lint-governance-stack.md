# Epic Proposal: Lint Governance Stack (`cargo lint-governance` + `lint-governance-pack/v0`)

## One-sentence pitch
Make Rust lint posture boring by standardizing a thin review boundary that keeps **authored guidance, selected policy, observed findings, debt baselines, fix/application receipts, and consumer verdicts** distinct instead of forcing every repo to reinvent its own lint CI semantics.

## Deliverables
- reference command:
  - `cargo lint-governance`
- schemas:
  - `lint-governance-brief/v0`
  - `lint-governance-pack/v0`
  - `lint-governance-diff/v0`
  - `lint-governance-handoff/v0`
  - `lint-policy-lock/v0`
  - `lint-baseline-diff/v0`
  - `lint-fix-handoff/v0`
- adapters/importers for:
  - `guidance-pack/v0`
  - `lint-profile/v0`
  - `lint-baseline/v0`
  - `lint-report/v0`
  - `lint-fixpack/v0`
  - `edit-apply-report/v0`
  - `policy-decision-report/v0`
  - Cargo future-incompat report imports
  - optional Cargo-lint imports
- docs:
  - workspace/profile-lock guide
  - baseline debt / expiry guide
  - fixpack vs apply-receipt guide
  - Cargo future-incompat / Cargo-lint import guide
  - safety/release/policy consumer-lossiness guide

## Why now (signals)
- Rust’s 2026 flagship slate explicitly includes **establishing safety-critical lints in Clippy**, which turns lint posture into assurance-adjacent ecosystem work rather than only style or convenience. That raises the value of portable lint evidence and curated lint subsets.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Stable Cargo now lets packages declare `[lints]` and workspaces declare `[workspace.lints]`, with workspace lint inheritance respected as of Rust 1.74. That means selected lint posture is now manifest-level reviewable metadata, not only `RUSTFLAGS` folklore.
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Nightly Cargo is experimenting with `[lints.cargo]`, which is a direct signal that Cargo-native warning families are moving toward the same policy plane rather than remaining invisible ad hoc console behavior.
  https://doc.rust-lang.org/cargo/reference/unstable.html#lintscargo
- Cargo’s changelog says Cargo 1.94 added the `report` subcommand and renamed the old future-incompat reporting command to `cargo report future-incompatibilities`; the current docs say `cargo report` is the report surface and that `future-incompat` is the currently supported report family. That is enough first-party substrate to justify a lint-governance import lane above raw terminal output.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- rustc’s lint model is already richer than one scalar pass/fail outcome: lint levels include `allow`, `expect`, `warn`, `force-warn`, `deny`, and `forbid`, with precedence rules across attributes and CLI flags. That strongly argues for an explicit policy-lock / finding / verdict boundary instead of flattening lint posture into one score.
  https://doc.rust-lang.org/rustc/lints/levels.html
- Clippy’s current docs still say its `clippy.toml` configuration file is unstable and may be deprecated in the future. That is a concrete signal that ecosystem governance should not be anchored only in hidden tool-local config files.
  https://doc.rust-lang.org/clippy/configuration.html
- The Edition Guide says `cargo fix` can only work with a single configuration at a time and may need multiple passes across targets or feature combinations; Cargo’s docs and release notes also keep elevating auto-fix flows, including suggestions to use `cargo fix` or `cargo clippy --fix` when warnings are auto-fixable. That means fixability is becoming more visible, but still needs reviewable packaging and application receipts.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://doc.rust-lang.org/beta/releases.html
- Clippy already exposes multiple lint groups (`all`, `cargo`, `pedantic`, `restriction`, `nursery`, and others) with different intended usage styles. That is useful power, but it also makes locked group expansion and baseline drift more important than another default profile debate.
  https://rust-lang.github.io/rust-clippy/stable/index.html

## Non-goals
- replacing rustc lints, Clippy, rustdoc linting, `cargo report`, `cargo fix`, or `rustfix`;
- defining one universal lint profile for the Rust ecosystem;
- inventing a scalar repo-cleanliness or lint-trust score;
- pretending Cargo-side report families are identical to rustc/Clippy/rustdoc findings;
- silently auto-applying suggested edits or turning the stack into a hidden codemod engine.

## Strategic value
This deserves promotion because it gives the archive a missing **policy-to-finding-to-edit continuity seam**.
With it:
- maintainers can review what policy they actually selected, how group expansion resolved, and which debt is knowingly accepted;
- CI and migration workflows can import baseline-aware findings without rebuilding bespoke diff logic;
- fix suggestions can stay portable and reviewable while applied edits remain separate facts;
- safety, release, package-admission, and support consumers can import curated lint posture without pretending linting is the whole decision engine;
- Cargo-native warning families can join the same evidence flow without displacing rustc / Clippy / rustdoc as separate emitters.

The prize is not another preset.
The prize is a durable record of **what guidance was authored, what policy was selected, what findings were observed, what debt was accepted, what fixes were suggested or applied, and what downstream consumers may honestly conclude**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `lint-governance-brief/v0` the canonical declaration of subject, engine mix, manifest/workspace origin, and intended consumers;
2. import `guidance-pack/v0` as the canonical authored-guidance lane;
3. import `lint-profile/v0`, `lint-baseline/v0`, and `lint-report/v0` as the canonical selected-policy / debt / finding lane;
4. import `lint-fixpack/v0` plus `edit-apply-report/v0` as the canonical suggestion-vs-application boundary;
5. import `policy-decision-report/v0` as the canonical higher-stakes verdict layer;
6. emit `lint-policy-lock/v0`, `lint-baseline-diff/v0`, `lint-governance-pack/v0`, `lint-governance-diff/v0`, `lint-fix-handoff/v0`, and `lint-governance-handoff/v0` so downstream stacks can consume lint governance without silently recomputing it.

## Critical design bet
The critical bet is that **lint governance becomes useful before Cargo and Clippy converge on one universal config model or one universal fix architecture**.
That means:
- stable manifest/workspace lint posture is already enough to anchor profile locks;
- Cargo-side report families are already enough to justify import lanes;
- Clippy’s own config instability is a reason to favor explicit exported artifacts over hidden local configuration;
- suggested fixes are already valuable even while selective application remains awkward;
- higher-stakes consumers can already benefit from bounded handoffs without waiting for a one-true linter platform.

Without that boundary, the stack either stays too thin to matter or bloats into a fake mega-linter.

## Milestones
1. **v0 policy-lock lane**
   - `lint-governance-brief/v0`
   - `lint-policy-lock/v0`
   - imports from `lint-profile/v0`
2. **v0.2 baseline/finding lane**
   - imports from `lint-baseline/v0` and `lint-report/v0`
   - `lint-baseline-diff/v0`
3. **v0.3 fix handoff lane**
   - imports from `lint-fixpack/v0` and `edit-apply-report/v0`
   - `lint-fix-handoff/v0`
4. **v0.4 Cargo import lane**
   - future-incompat and optional Cargo-lint import notes
   - explicit comparability/lossiness markers
5. **v1 consumer handoffs**
   - `lint-governance-pack/v0`, `lint-governance-diff/v0`, `lint-governance-handoff/v0`
   - safety / release / migration / package-admission / support consumers

## Execution order
Use [`design/lint-governance-pilot-program.md`](../design/lint-governance-pilot-program.md) as the stack-level rollout:
1. workspace/profile-lock lane,
2. baseline-drift / debt-budget lane,
3. fixpack / apply-receipt lane,
4. Cargo future-incompat / Cargo-lint import lane,
5. safety/release/policy consumer lane.

Use [`proposals/epic-lint-baseline-kit.md`](./epic-lint-baseline-kit.md), [`proposals/epic-compile-guidance-kit.md`](./epic-compile-guidance-kit.md), [`proposals/epic-edit-workflow-kit.md`](./epic-edit-workflow-kit.md), and [`proposals/epic-policy-kit.md`](./epic-policy-kit.md) as the leaf-level execution guides beneath it.

## Success metrics
- reviewers can distinguish authored guidance, selected policy, baseline debt, observed findings, suggested fixes, applied edits, and final verdicts without reading CI shell glue;
- group expansion and workspace inheritance remain reviewable instead of drifting silently between toolchain bumps;
- Cargo-native future-incompat or later Cargo-lint imports can join the same pack with explicit caveats;
- at least two downstream consumers can import the same lint-governance pack without bespoke scraping;
- the ecosystem gets one explainable lint-governance seam instead of scattered manifest tables, console logs, suppression comments, and codemod folklore.
