---
id: P-0514
title: Crate Upgrade Pack Kit — downstream migration recipes, fixup receipts, and release-to-release hazard reports for library authors
status: idea
domains: [crates, upgrades, migration, semver, cargo, diagnostics, docs, supportiveness]
last_reviewed: 2026-03-20
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  - https://doc.rust-lang.org/cargo/reference/semver.html
  - https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
  - https://doc.rust-lang.org/beta/rustc/json.html
  - https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  - https://docs.rs/rustfix/latest/rustfix/
  - https://release-plz.dev/docs/usage/update
  - https://crates.io/crates/cargo-release
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://doc.rust-lang.org/cargo/commands/cargo-package.html
  - https://doc.rust-lang.org/cargo/reference/publishing.html
  - https://doc.rust-lang.org/cargo/commands/cargo-report.html
  - https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
  - https://release-plz.dev/docs/config
  - https://docs.rs/crate/cargo-release/latest
---

# Problem

The archive now has much better answers for:

- **which crate to choose**,
- **what a crate claims to support**,
- **which shared interop profile it fits**,
- **what guidance it gives before or during failure**,
- and **what it hands off after runtime failure**.

But there is still a conspicuous hole in the crate-supportiveness frontier:

- what a crate hands other people when they try to move from **version N** to **version N+1**.

That hole matters because current Rust signals already describe three pieces of the problem clearly:

1. the 2025 vision-doc work explicitly recommends expanding Rust’s extensibility to cover **supportive interfaces from crates**,
2. the 2025 survey says **online documentation** remains the preferred canonical reference, followed by **studying the code itself**,
3. and the Rust project is actively pushing `cargo-semver-checks` toward the `cargo publish` workflow because accidental SemVer violations are common enough to warrant first-class tooling.

Rust also now has real substrate for upgrade assistance, but only in fragments:

- Cargo’s SemVer reference documents what is conventionally breaking,
- the project-goals work around `cargo-semver-checks` focuses on evidence for **whether** a release is compatible,
- the `hint-mostly-unused` write-up reiterates that **feature flags are part of a crate’s stable interface**,
- `rustc` JSON diagnostics carry suggestions and applicability metadata,
- `cargo fix` demonstrates an iterative “apply suggestions, re-check, keep manual review explicit” model,
- and `rustfix` exists as a low-level suggestion applier.

Release tools also exist:

- `release-plz` updates versions and changelogs and can consult `cargo-semver-checks`,
- `cargo-release` automates common publish-time chores,
- changelog generators summarize commits,
- and Cargo itself owns the publish / yank surface.

But those tools still do **not** give library authors one boring workflow for saying:

- here are the upgrade hazards from 1.4 to 1.5,
- here are the feature/config/runtime combinations we checked,
- here are the smallest before/after recipes,
- here are the machine-applicable edits versus manual edits,
- and here is the explicit manual-review boundary.

The missing crate is therefore **not** another semver checker, **not** another changelog tool, and **not** another release bot.
It is a **Crate Upgrade Pack Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What changed between two crate releases in ways that matter to downstream users?**
2. **Which upgrade hazards are already covered by SemVer/public-API analysis, and which fall outside that slice?**
3. **Which fixes are machine-applicable, and which require human migration work?**
4. **Which feature, target, config, or runtime combinations were actually checked?**
5. **What is the smallest known-good migration recipe for each supported upgrade lane?**
6. **What changed in the crate’s upgrade support surface across releases?**
7. **Which imported receipts belong to one coherent review session, and which public claims join evidence across different sessions?**

That is more valuable than another nicely formatted changelog.

# What it provides

## Productization update (2026-03-17)

This pass sharpens the proposal into a more buildable `0.1` by making three previously fuzzy questions explicit review artifacts:

- **What kind of upgrade hazard is this?**
  Not every problem should look like a SemVer break. `0.1` should classify hazards such as `machine_fix_available`, `manifest_edit_required`, `config_edit_required`, `behavior_check_required`, and `manual_review_required`.
- **What fix capability was actually observed?**
  A pack should say whether a fix came from `cargo fix`, `rustfix`, Clippy, a maintainer codemod, or nowhere — and whether it touched Rust source only, manifest/config files, docs snippets, or a wider workspace.
- **How much of the upgrade lane was really checked?**
  A pack should record whether a claimed `from -> to` lane was `fully_observed`, merely `sampled`, recipe-only, docs-only, or still `manual_review_required`, across features, targets, runtimes, and package subsets.

A good `0.1` should therefore standardize these additional artifacts above the original fixture pack:

- `hazard-class.policy.json`
- `fixup-capability.receipt.json`
- `lane-fidelity.report.json`

and should converge on the same boring command set the archive has been favoring elsewhere:

- `cargo upgrade-pack init`
- `cargo upgrade-pack capture`
- `cargo upgrade-pack check`
- `cargo upgrade-pack doctor`
- `cargo upgrade-pack summary`
- `cargo upgrade-pack diff <old> <new>`
- `cargo upgrade-pack pack`

The missing value stays the same: a **receiver-facing migration artifact** above SemVer evidence, release automation, and changelog prose. But this pass makes the implementation target much less hand-wavy.

- `upgrade-pack.toml` — versioned declaration of supported `from -> to` lanes, upgrade families, checked feature/target/runtime matrices, recipe refs, and manual-review zones.
- `upgrade-hazards.report.json` — imported or computed hazards from semver checks, feature-surface changes, manifest/config shifts, deprecations, and release-policy notes.
- `fixup-hints.receipt.json` — observed machine-applicable suggestions, codemod hooks, lint/fix notes, or “no automatic fix available” classifications.
- `migration-recipe.manifest.json` — smallest before/after examples for supported upgrade lanes, including required feature flags, config edits, and expected post-upgrade checks.
- `upgrade-check.report.json` — verifies that recipes still build/check/test under the intended upgrade matrix and classifies `fixable`, `manual_review_required`, `behavior_check_required`, and `unsupported_lane`.
- `upgrade-diff.report.json` — compares two upgrade packs and classifies `hazard_added`, `recipe_changed`, `fixup_improved`, `fixup_removed`, `matrix_changed`, and `manual_review_boundary_changed`.
- `upgrade-notes.summary.md` — compact human-facing upgrade summary derived from the pack.
- `cargo upgrade-pack capture` — capture one release-to-release upgrade bundle.
- `cargo upgrade-pack check` — run the selected recipes and emit receipts.
- `cargo upgrade-pack diff <old> <new>` — compare upgrade-support surfaces across releases.
- `cargo upgrade-pack summary` — render a reviewable human summary from structured artifacts.

# What the crate should provide other people

1. **A crate-authored upgrade contract** above changelogs and below full product migration guides.
2. **A joined upgrade-hazard artifact** that can import SemVer/public-API evidence without pretending that is the whole story.
3. **Machine-fix receipts** that tell people which edits can be automated and which cannot.
4. **Minimal migration recipes** for common lanes such as renamed APIs, feature-policy changes, config changes, or runtime-selection shifts.
5. **An honest matrix report** that says which upgrade combinations were actually checked.
6. **Explicit lane-selection truth** that says whether scope came from ambient workspace defaults, explicit package selection, feature activation, target gating, or a narrower maintainer-declared lane.
7. **Explicit config-basis truth** that says whether the lane depended on checked-in Cargo config, user-home config, environment-variable overrides, `--config` injection, `[patch]`, source replacement, or other resolution/build surfaces that would otherwise stay hidden behind an ordinary-looking command line.
8. **Explicit baseline-state truth** that says whether the checked subject was a pinned published release, a reconstructible package extract, or a mutable/dirty local workspace so release-pair claims do not quietly inherit a fake pristine starting point.
9. **Surface-authorship truth** that keeps Cargo-native outputs, maintainer-authored guidance, reviewer-authored decisions, and archive-derived summaries from quietly inheriting one another's trust surface.
10. **Durable public-cue truth** that keeps blocking warnings, supersession, and other decisive public meanings visibly present on exported entry surfaces instead of trapping them in registers.
11. **Session-honesty truth** that keeps same-session evidence distinct from mixed-session synthesis and forces public disclosure when one summary joins receipts captured at different times.
12. **Replay-bridge truth** that keeps direct replay, native-storage rerender, copied attachments, and manual-only snapshots from collapsing into one fake “replayable evidence” claim.
13. **A diffable upgrade-support surface** so maintainers can review whether releases are becoming easier or harder to adopt.
14. **A reusable import layer** for docs portals, support bots, release PRs, and pathfinder-style tooling.

# Persona / who it’s for

- maintainers of widely used library crates
- framework teams shipping regular minor releases
- workspace owners coordinating internal crate migrations
- tooling authors building release-review bots or docs surfaces
- downstream teams who want something better than “read the changelog and hope”

# Users & user stories

- **Library maintainer**: “Show me what a downstream team must change when moving from 1.4 to 1.5, and which parts we can auto-fix.”
- **Framework maintainer**: “Keep feature-policy and runtime-profile migrations explicit instead of scattering them across release notes, docs, and support threads.”
- **Downstream adopter**: “Give me one compact upgrade pack with hazards, recipes, and explicit manual-review boundaries.”
- **Release reviewer**: “See whether the migration surface improved or regressed compared with the previous release.”
- **Tool author**: “Import a stable upgrade artifact instead of scraping changelog prose and CI logs.”

# Prior art (and why it’s insufficient)

- `cargo-semver-checks` and Cargo’s SemVer guidance are the best current substrate for deciding **whether** a change is breaking.
- `cargo fix`, the edition-migration machinery, and `rustfix` prove that suggestion-driven upgrade workflows can be both real and reviewable.
- `release-plz`, `cargo-release`, and changelog generators help maintainers **publish** releases and summarize them.

What remains missing is the joined, receiver-facing artifact that says:

- which upgrade lane is being described,
- what hazard classes exist,
- which suggestions are machine-applicable,
- which before/after recipes were checked,
- and where the maintainer still needs the user to read carefully and decide.

That is a different lane from:

- **P-0244** semver witness evidence,
- **P-0483** public-API readiness bundles,
- release automation,
- compile-time guidance packs,
- runtime handoff packs,
- or domain-specific migration kits.

# Design goals

1. **Receiver-facing first** — optimize for downstream upgrade clarity, not maintainer vanity metrics.
2. **Join, don’t replace** — import semver/public-API/suggestion substrate where possible.
3. **Machine-fix honesty** — distinguish machine-applicable edits from advisory guidance and manual migration.
4. **Matrix honesty** — preserve which feature/target/runtime/config lanes were checked.
5. **Recipe-backed** — the best upgrade claim is a small passing recipe, not a prose paragraph.
6. **Release-to-release narrowness** — stay focused on one crate’s upgrade surface, not whole-org release orchestration.
7. **Manual-review explicitness** — a real `manual_review_required` lane is part of the value.

# MVP surface

- Minimal types: `UpgradePack`, `UpgradeLane`, `UpgradeHazardsReport`, `FixupHintsReceipt`, `MigrationRecipeManifest`, `UpgradeCheckReport`, `UpgradeDiffReport`, `UpgradeNotesSummary`
- Minimal functions:
  - `load_upgrade_pack()`
  - `import_upgrade_hazards()`
  - `capture_fixup_hints()`
  - `validate_migration_recipes()`
  - `check_upgrade_lane()`
  - `diff_upgrade_bundles()`
  - `render_upgrade_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `semver-import`
  - `rustfix`
  - `docs-links`
  - `markdown`


## 2026-03-20 revalidation / freshness refresh

The previous passes made packs honest about **what they know now**.
They still lacked one reviewable answer to a simpler downstream question:

> **When does this pack stop being current enough to trust as the active migration contract?**

Two more review objects should now become first-class:

- `revalidation-window.policy.json` — declares the pack's review clock, the material-change triggers that expire it, and whether newer current packs automatically supersede older ones.
- `freshness-state.report.json` — says whether a pack is `current`, `stale_but_usable`, `expired`, `superseded`, or `unknown`, plus why.

That distinction matters because a pack can be internally coherent, freeze-ready, and even previously public while still no longer being the right active contract after:

- a migration-guide head moves,
- the resolved dependency/workspace graph changes,
- feature/default policy shifts,
- recipes or behavior witnesses change,
- or a newer revalidated pack already exists.

Without these objects, the lane still permits two ordinary lies:

1. **approval fossilization** — an old pack keeps reading as if its old review still matches the live lane,
2. **parallel truth drift** — an older public summary quietly competes with a newer revalidated pack because nothing explicitly marks the older one as superseded.

A worthy crate here should therefore provide not only hazards, recipes, scope truth, readiness, export posture, deviations, and warnings, but also one honest answer to:

- how long a pack stays current,
- which changes force revalidation,
- whether stale packs remain usable only for internal/manual reference,
- and when a newer pack has formally replaced an older one.

## 2026-03-20 summary-claim traceability refinement

The lane can now be honest about inputs, readiness, export, deviations, warnings, and freshness while still leaving one quiet lie available:

> a polished public `upgrade-notes.summary.md` can float more than the receipts beneath it.

Two donor moves make that gap hard to ignore:

- the smallest durable public surface often needs a **compact claim register** rather than prose-only trust,
- and a first-contact summary should carry an explicit **fallback path** when one sentence compresses several exact receipts.

A sharper `0.1` should therefore elevate one more review object:

- `summary-claim.register.json` — records each exported summary claim with a stable claim id, section id, claim class, audience, status, authoring mode, exact evidence refs, active warning/deviation links, and one fallback ref when the summary sentence is too compressed to act on safely.

## 2026-03-20 session-honesty refinement

The lane can now be exact about source lineage, capture context, coverage matrices, lane selection, publication surfaces, and claim traceability while still leaving one ordinary lie available:

> several imported receipts can be presented as one coherent review moment even when they were captured in different sessions.

A sharper `0.1` should therefore elevate one more review object:

- `session-honesty.report.json` — records whether imported evidence belongs to one native session, one explicit capture family, a cross-session comparison, or a mixed-session synthesis that requires visible warning/disclosure on public surfaces.

This is the missing honesty layer between "all evidence refs are present" and "these refs can safely be read as one review moment".

The practical consequence is that a good pack should now be able to say:

- “this public summary sentence is backed by these exact hazard, scope, fixup, or freshness receipts,”
- “this sentence is a mixed maintainer synthesis rather than a native import,”
- and “if the summary is partial, follow this fallback receipt/queue item/manual-boundary ref instead of treating the sentence as a complete authority surface.”

That keeps the lane honest at the moment where exported summary prose is most tempted to outrun the exact receipts that made it reviewable.

# Compatibility story

- Should work in a stable-first mode by importing SemVer/public-API findings and recipe checks available on stable toolchains.
- Higher-fidelity lanes may import machine-applicable suggestions from compiler diagnostics or lint runs.
- Must preserve which hazards were **imported**, which were **measured**, and which were **maintainer-authored**.
- Should remain useful whether the release workflow uses plain Cargo, `release-plz`, `cargo-release`, or custom CI.
- Must remain honest when a crate cannot promise smooth upgrades across all feature/target/runtime lanes.

# 0.1 upgrade families

1. `renamed_or_replaced_api`
   - imports semver/public-API hazard facts
   - attaches smallest before/after recipe
   - records whether a machine-applicable fix exists
2. `feature_policy_shift`
   - records changed defaults, removed/added required features, or new runtime-neutral recommendations
   - explicitly marks whether the lane is breaking or just support-policy drift
3. `config_or_manifest_shift`
   - tracks env/config key changes, builder setup changes, or generated-code assumptions
   - recipe shows the smallest corrected config
4. `runtime_or_interop_shift`
   - records changed runtime selection, adapter path, or shared ecosystem profile expectations
   - upgrade pack points to the expected interop profile or fallback adapter
5. `manual_review_required`
   - reserved for behavior or integration changes that cannot be honestly reduced to a machine recipe yet

# Conformance & fixtures

- one renamed-API fixture with a small machine-applicable fixup hint
- one feature-policy fixture showing a changed default or required feature lane
- one config/runtime-profile fixture with a before/after recipe
- one fixture that deliberately stays `manual_review_required`
- goldens for `hazard_present`, `fixup_machine_applicable`, `recipe_missing`, `matrix_gap`, `unsupported_lane`, and `manual_review_required`

# Path to boring stability

- Stabilize the pack/check/diff schemas before adding fancy editor integrations or changelog generation.
- Start with import + recipe verification rather than universal codemod ambition.
- Keep the first hazard vocabulary small and sharp.
- Treat “unsupported upgrade lane” as honest output, not failure.
- Add deeper adapters only after maintainers trust the basic artifact vocabulary.

# Why this could matter

This is the crate that would let maintainers say:

- “Here is the supported migration path from our last minor release.”
- “Here are the specific hazards, not just the commit log.”
- “Here is what tooling can auto-fix.”
- “Here is the smallest working example after the upgrade.”
- “Here is what we checked, and what still needs a human.”

That is the sort of boring, high-leverage supportiveness layer that makes ecosystem upgrades feel less like folklore.

# Why now

1. The official Rust vision work now names supportive crate interfaces directly.
2. The survey still says docs and code are the main learning surfaces, which means upgrade support needs better structure.
3. Cargo wants semver checking closer to publish time, which raises the value of a downstream-facing upgrade artifact above raw verdicts.
4. Cargo/edition migration already proved that iterative suggestion-backed upgrades can work.
5. Release tools are getting better at publishing and changelogs, but not at crate-authored migration receipts.

# Sharp edges / open questions

- How should upgrade packs represent behavior changes that are semver-legal but still operationally painful?
- How much codemod ambition is helpful before the crate turns into a refactoring framework?
- How should recipe verification handle multi-feature or multi-target combinatorics without pretending total coverage?
- What is the smallest useful hazard taxonomy that still covers feature-policy and runtime-profile changes?
- Which upgrade notes should remain local docs anchors versus copied into exported summaries?

# Suggested 0.1 deliverable

A crate and cargo subcommand that load one `upgrade-pack.toml`, import a release-to-release hazard slice, validate a few before/after recipes, capture any machine-applicable fix hints, and emit:

- one `upgrade-hazards.report.json`,
- one `hazard-authority.receipt.json`,
- one `source-lineage.receipt.json`,
- one `hazard-arbitration.report.json`,
- one `import.receipt.json`,
- one `fixup-hints.receipt.json`,
- one `fixup-posture.report.json`,
- one `source-heads.report.json`,
- one `package-scope.report.json`,
- one `followthrough-state.report.json`,
- one `pack-readiness.report.json`,
- one `review-queue.report.json`,
- one `cross-register-consistency.report.json`,
- one `export-posture.report.json`,
- one `publication-surface.manifest.json`,
- one `deviation-ledger.receipt.json`,
- one `warning-register.report.json`,
- one `redaction.receipt.json`,
- one `summary-claim.register.json`,
- one `omission-register.report.json`,
- one `public-trace-path.report.json`,
- one `migration-recipe.manifest.json`,
- one `upgrade-check.report.json`,
- one `upgrade-diff.report.json`,
- and one short `upgrade-notes.summary.md`.

That would already be enough to prove the lane is real.

# Adoption plan

## 0.1
- schema + recipe verification
- semver/public-API hazard import
- compact summary generation

## 0.2
- rustfix / suggestion capture adapters
- richer feature/target/runtime matrix reporting
- CI templates for release PRs

## 1.0
- stable bundle schema
- curated fixtures across three distinct upgrade families
- downstream-tool import examples

# Non-goals

- Not a replacement for `cargo-semver-checks` or public-API diff tools.
- Not a generic changelog generator or release bot.
- Not a universal codemod framework.
- Not a domain-specific migration kit for databases, protocols, or editions.
- Not a promise that every release can be safely auto-upgraded.

# Architecture & API sketch

```rust
pub struct UpgradeVerdict {
    pub status: String,
    pub reasons: Vec<String>,
}

pub fn load_upgrade_pack(path: &Path) -> Result<UpgradePack>;
pub fn import_upgrade_hazards(root: &Path) -> Result<UpgradeHazardsReport>;
pub fn validate_migration_recipes(pack: &UpgradePack) -> Result<UpgradeCheckReport>;
pub fn diff_upgrade_bundles(old: &UpgradePack, new: &UpgradePack) -> UpgradeDiffReport;
```

Bundle draft: `upgrade-pack.toml`, `upgrade-hazards.report.json`, `hazard-authority.receipt.json`, `source-lineage.receipt.json`, `hazard-arbitration.report.json`, `import.receipt.json`, `fixup-hints.receipt.json`, `fixup-posture.report.json`, `source-heads.report.json`, `package-scope.report.json`, `followthrough-state.report.json`, `pack-readiness.report.json`, `review-queue.report.json`, `cross-register-consistency.report.json`, `export-posture.report.json`, `publication-surface.manifest.json`, `redaction.receipt.json`, `deviation-ledger.receipt.json`, `warning-register.report.json`, `summary-claim.register.json`, `surface-authorship.report.json`, `lane-selection.receipt.json`, `config-basis.receipt.json`, `public-trace-path.report.json`, `durable-cue.report.json`, `migration-recipe.manifest.json`, `upgrade-check.report.json`, `upgrade-diff.report.json`, `upgrade-notes.summary.md`, `notes.md`.

## 2026-03-19 implementation refresh

This lane now looks sharper when treated as a contract about three additional truths:

1. **hazard authority** — whether an upgrade hazard came from SemVer/public-API analysis, feature/default-policy drift, config/runtime policy drift, a behavior witness, or only a maintainer note,
2. **package-scope truth** — which workspace members, binaries, examples, and non-published companions were actually exercised,
3. **follow-through coverage** — whether a machine fix touched only Rust source or truly covered manifest/config/docs follow-through.

That refresh is better grounded now because `release-plz` explicitly integrates `cargo-semver-checks` while warning it does not catch every SemVer violation; `cargo fix` and `rustfix` remain source-suggestion substrate rather than whole-upgrade substrate; Cargo’s external-tools and `cargo metadata --format-version` surfaces make workspace-aware import realistic; and the July 2025 `hint-mostly-unused` write-up made the language around feature flags as stable interface unusually explicit.

The practical consequence is that a buildable `0.1` should no longer stop at hazard classes + fixup receipts + lane fidelity.
It should also publish:

- `hazard-authority.receipt.json`
- `package-scope.report.json`
- `source-lineage.receipt.json`
- `hazard-arbitration.report.json`
- `followthrough-state.report.json`

and should treat “source fix observed, but manifest/docs still manual” and “previous-lane completion cannot silently close the current lane” as first-class output rather than footnotes.

The crate should therefore provide other people:

- one compact upgrade contract,
- one explicit map of **where each hazard came from**,
- one explicit report of **which package/example/binary lanes were really checked**,
- one explicit account of **what automation actually touched**,
- and one honest manual-review boundary where the lane stops being witnessed.

## 2026-03-20 cross-archive refinement

The next refinement is not another hazard class.
It is a better answer to three archive mistakes that still remain possible after the 2026-03-19 pass:

1. **source surfaces collapse together** — a floating release page, an anchored changelog entry, a migration guide, and an issue-thread comment get treated as if they carried the same authority;
2. **adjacent authorities get polished into one winner** — SemVer/public-API evidence, feature-policy drift, maintainer notes, and behavior witnesses disagree, but the pack still emits one clean story;
3. **old follow-through gets mistaken for current completion** — a docs/config/example step completed on an older lane silently closes the same step on a newer `from -> to` pair.

A sharper `0.1` should therefore treat three more review objects as first-class:

- `source-lineage.receipt.json` — records the canonical locator, fetched locator, pin status, review status, and promotion status for imported human-authored release surfaces;
- `hazard-arbitration.report.json` — records candidate authorities, confusability class, arbitration rule, abstain baseline, and honest outcome when adjacent authorities do not collapse;
- `followthrough-state.report.json` — records step membership, current request state, completion state, and prior-lane receipts so the pack can say `rerequest_needed` explicitly.

The practical consequence is that the crate should no longer stop at “here is the hazard source, here is the package scope, here is the source-only fix.”
It should also say:

- “here is whether the imported release surface was pinned tightly enough to count,”
- “here is where the authorities disagreed and why we abstained or downgraded to manual review,”
- and “here is which docs/config/example/manual steps are still actively requested on this exact lane.”

That makes the bundle more honest in the places where upgrade support usually starts lying.

## 2026-03-20 source-head and pack-readiness refinement

A still-deeper donor read found two remaining gaps after the lineage / arbitration / follow-through / import / fixup-posture passes:

1. **latest operational guidance still gets mistaken for citation-ready guidance** — the pack can know several imports in one migration-guide family without saying which one is merely the current operational head and which one, if any, is actually frozen tightly enough to cite;
2. **overall pack maturity still has to be inferred by hand** — reviewers can see floating imports, active follow-through work, partial scope claims, unstable imports, and approval-gated fixes, but the bundle still lacks one fused answer about whether the pack should stay on hold or can be frozen.

A sharper `0.1` should therefore elevate two more review objects:

- `source-heads.report.json` — records lineage-level operational heads, citation heads, and warnings when the current useful head is still floating, ambiguous, or not yet citation-ready;
- `pack-readiness.report.json` — fuses citation-head gaps, floating imports, authority conflicts, scope partiality, active follow-through, posture blockers, and unstable imports into one explicit `hold` / `candidate` / `freeze_ready` / `manual_review_only` verdict.

The practical consequence is that a good pack should now be able to say:

- “this docs `latest` migration guide is the operational head, but there is still no citation-ready frozen head for this release pair,”
- “the pack is still useful as a candidate review surface, but it honestly remains `hold` because citation, scope, and follow-through debt are still open,”
- and “here is the single safest next move before we freeze this lane for downstream users.”

That keeps the lane honest at the moment where maintainers are most tempted to polish a half-ready migration story into a shipped contract.


## 2026-03-20 native-import and fixup-posture refinement

A deeper cross-datacube read still found two false merges inside this lane even after the source-lineage / arbitration / follow-through pass:

1. **native tool import and later summary still collapse together** — a machine-native `cargo semver-checks`, `cargo fix`, `cargo metadata`, or future Cargo report surface can get flattened into a later prose summary as if they carried the same truth;
2. **fix capability and allowed execution posture still collapse together** — the pack can honestly say “a source fix exists” while still failing to say whether the lane is manual-only, suggestion-only, approval-required, or safe for any bounded autonomous step.

A sharper `0.1` should therefore elevate two more review objects:

- `import.receipt.json` — records which upgrade facts came from machine-native tool/report surfaces, whether they were imported verbatim or normalized later, and whether the underlying lane was stable, unstable, external, or mixed;
- `fixup-posture.report.json` — records the allowed execution posture for each fix family so a pack never confuses “automation exists” with “unattended migration is safe”.

The practical consequence is that a good pack should now be able to say:

- “this hazard slice came from a native tool import, not from the release-note summary,”
- “this workspace/package truth came from `cargo metadata`, not from hand-maintained notes,”
- “this future-incompat or build-analysis import is still unstable and must stay marked as such,”
- and “this source rewrite is approval-required while manifest/docs follow-through remains manual or bounded by stricter stop conditions.”

That keeps the lane honest in two places where support artifacts often start cheating:
summary replaces import, and fix presence gets mistaken for permission to run.

## 2026-03-20 review-queue and cross-register-consistency refinement

One more donor sweep still found two places where the pack could remain honest in pieces but dishonest in the whole:

1. **review debt still lives as prose instead of queued work** — `pack-readiness.report.json` can say `hold` and offer one `next_safest_step`, but maintainers still lack a compact action queue for the specific source-pinning, arbitration, scope, follow-through, and approval work that remains;
2. **the pack can still contradict itself across artifacts** — a future summary could claim `freeze_ready` while `source-heads.report.json` still warns `citation_head_missing`, `followthrough-state.report.json` still has active steps, or `package-scope.report.json` still records a partial workspace lane.

A sharper `0.1` should therefore elevate two more review objects:

- `review-queue.report.json` — records the remaining freeze-blocking or candidate-blocking actions as explicit queue items with class, status, required-before boundary, blocker refs, and the safest next action for each item;
- `cross-register-consistency.report.json` — binds the constituent pack receipts and emits a bounded set of pass/fail/unknown checks so the pack can loudly reject impossible combinations instead of leaving consistency to hand review.

The practical consequence is that a good pack should now be able to say:

- “the pack remains `hold`, and here are the exact queued actions needed before it can become a candidate or freeze-ready surface,”
- “this citation-head gap and this active docs follow-through step are still open, so no freeze-ready claim is allowed,”
- and “this already-typed lane stays exact rather than quietly borrowing claims from a broader workspace or a looser source family.”

That keeps the lane honest in two more ordinary failure modes: hidden review work, and self-contradictory public contracts.

## 2026-03-20 export-posture and publication-surface refinement

One more donor sweep still found two places where the pack could be honest about migration facts yet dishonest about export:

1. **internal maturity still gets mistaken for public-shareable posture** — a pack can be reviewable enough for maintainers while still carrying local paths, internal package aliases, private examples, or working notes that make public export dishonest;
2. **the working tree still gets mistaken for the public contract** — even a frozen lane can fail to say which files or receipts actually belong on the stable downstream surface.

A sharper `0.1` should therefore elevate two more review objects:

- `export-posture.report.json` — records audience class, exposure scope, sensitivity flags, redaction status, and the honest private/public decision state for the lane;
- `publication-surface.manifest.json` — records the exact public entry points, supporting context refs, omitted internal refs with reasons, and compact warning labels that travel with the public contract;
- `deviation-ledger.receipt.json` — records expiring, numbered overrides when a pack intentionally proceeds under non-default freeze/export/consistency posture;
- `warning-register.report.json` — records the compact active warning set with severity, audience, source refs, surfaced-on refs, and optional deviation links.

The practical consequence is that a good pack should now be able to say:

- “this lane is strong enough for internal review, but still stays `private_candidate` until local paths and package aliases are redacted,”
- “the public contract is this frozen summary + recipe + supporting receipts, not the whole working directory,”
- and “these floating imports or private working notes stay off the exported surface even though they remain useful to maintainers.”

That keeps the lane honest in two more ordinary failure modes: private working material masquerades as public contract, and public contract scope stays implicit instead of exact.

## 2026-03-20 capture-context and coverage-matrix refinement

One more donor sweep still found two places where the pack could speak honestly about individual receipts while bluffing about the actual checked lane:

1. **dimension lists still collapse into fake matrix coverage** — `lane-fidelity.report.json` can say which features, targets, runtimes, or package subsets were touched, but it still cannot say which exact cells were observed, left unknown, or intentionally out of scope;
2. **native imports can still float free of the exact capture session** — `import.receipt.json` can preserve native-vs-summary truth, yet a `cargo fix`, `cargo metadata`, or `cargo-semver-checks` import can still be over-read unless the pack binds it to the exact package/target/feature/toolchain/lockfile context that produced it.

A sharper `0.1` should therefore elevate two more review objects:

- `capture-context.receipt.json` — records the exact capture session or command context for imported upgrade evidence, including package/target/feature selection, toolchain posture, lockfile posture, native ids, and replay posture;
- `coverage-matrix.report.json` — records the exact sparse matrix cells the pack is willing to speak about, together with their coverage state, evidence refs, and capture-context bindings.

The practical consequence is that a good pack should now be able to say:

- “this `cargo fix` or SemVer import came from this exact capture context, not from a whole-workspace or all-target claim,”
- “the default library lane was observed, but the `required-features` CLI target remains unknown,”
- and “these matrix cells are observed, these are recipe-only, and these remain manual review or unrequested.”

That keeps the lane honest in two more ordinary failure modes: dimension lists that sound like whole-matrix coverage, and machine-native imports that quietly outgrow the exact selection that produced them.

## 2026-03-20 public-trace-path refinement

One more donor sweep still found one place where the pack could be honest about export posture, public surface, warnings, freshness, and summary-claim traceability while still bluffing about what a public reader can actually inspect:

1. **public summary claims can still point at non-public or non-resolving routes** — `summary-claim.register.json` can name exact evidence refs and `publication-surface.manifest.json` can list exported files, but a frozen/public claim can still end up backed only by internal receipts, a missing public fragment, or a fallback path that no public reader can actually follow;
2. **trace misses can still lose their own surface name** — when a promised public route fails, the pack still needs a typed miss that says “public trace path failed here” rather than collapsing into one generic missing-ref complaint.

A sharper `0.1` should therefore elevate one more review object:

- `public-trace-path.report.json` — records, for each public or downstream-facing summary claim, the actual public trace posture, the primary/fallback public refs, the resolution status, and a typed miss kind when the promised route fails at the fragment/target/private-only layer.

The practical consequence is that a good pack should now be able to say:

- “this public hazard claim routes to this exported receipt and actually lands on a real public anchor,”
- “this warning-bearing claim routes through the public warning register and exported queue item instead of pointing at private maintainer notes,”
- and “this pack is only a public candidate, not frozen public, because the trace route currently fails with a typed `public_trace_fragment_missing` miss.”

That keeps the lane honest in one more ordinary failure mode: a polished public summary that sounds traceable while its promised inspection path is private, broken, or anchorless.

## 2026-03-20 lane-selection refinement

One more donor sweep still found one place where the pack could be honest about exact capture contexts and sparse coverage while still bluffing about why the lane was that size in the first place:

1. **ambient Cargo selection can still masquerade as intentional upgrade scope** — `package-scope.report.json` can say which packages were covered and `coverage-matrix.report.json` can say which cells were observed, yet a lane can still quietly inherit workspace `default-members`, current-directory package choice, or manifest-root defaults and sound like a deliberate maintainer-reviewed boundary;
2. **feature/target coverage can still be over-read without one normalized selection cause** — raw command lines and capture receipts can mention features or targets, but they still do not by themselves tell a downstream reviewer whether the lane came from explicit `-p` / `--workspace` / `--exclude` choices, default-feature activation, or target gating through `required-features`.

A sharper `0.1` should therefore elevate one more review object:

- `lane-selection.receipt.json` — records the invocation subject, manifest-walk posture, workspace attachment/default-member posture, normalized package selection, feature selection, target selection, and any ambient-selection warnings that keep the lane from sounding more deliberate than it was.

The practical consequence is that a good pack should now be able to say:

- “this lane was selected because the reviewer stood at the workspace root and Cargo used `workspace.default-members`, not because maintainers explicitly signed off on omitting sibling members,”
- “this wider lane exists because explicit `-p` selection overrode ambient defaults,”
- and “this target stayed outside the lane because `required-features` kept it gated, not because it was observed and found clean.”

That keeps the lane honest in one more ordinary failure mode: ambient Cargo selection behavior quietly posing as reviewed upgrade-scope intent.

## 2026-03-20 durable-public-cue refinement

One more donor sweep still found one place where the pack could be honest about export posture, publication surface, summary-claim traceability, public trace paths, and warning provenance while still bluffing about what a human reader will actually keep in view:

1. **decisive public meanings can still live only in compact or machine-readable surfaces** — `warning-register.report.json` can classify a blocker, `freshness-state.report.json` can say `superseded`, and `publication-surface.manifest.json` can export exact files, yet a downstream reader can still miss the controlling meaning if it survives only as a label, register entry, or supporting receipt instead of a durable visible cue on the exported entry surface;
2. **public traceability is not the same thing as durable public visibility** — `public-trace-path.report.json` can prove that a reader *could* chase a route into the right receipt, but a blocking warning or replacement notice can still be too easy to miss if the visible summary surface does not carry an unmistakable durable equivalent.

A sharper `0.1` should therefore elevate one more review object:

- `durable-cue.report.json` — records which warning/readiness/freshness/deviation/manual-review meanings govern the public surface, which durable exported surface refs keep those meanings visible, and whether the pack still falls back to compact-only or register-only posture.

The practical consequence is that a good pack should now be able to say:

- “this blocking manual-review warning is not just present in the warning register; it also survives as a visible callout on the exported summary surface,”
- “this superseded public pack does not merely carry a machine-readable freshness state; it keeps a durable replacement notice visible at entry,”
- and “this compact warning label is advisory-only because the governing meaning already has a durable visible equivalent elsewhere on the exported public surface.”

That keeps the lane honest in one more ordinary failure mode: decisive public meaning that is technically present somewhere in the bundle while still being too easy for a real reader to miss.

## 2026-03-20 redaction-receipt refinement

One more donor sweep still found one place where the pack could be honest about export posture, publication-surface exactness, public trace routes, and durable public cues while still bluffing about **how** a formerly private pack became safe to share:

1. **`redaction_status` can still float as a verdict string** — `export-posture.report.json` can say redaction is required or applied, yet the bundle can still lack one bounded record of what private material was dropped, generalized, or moved off the public surface;
2. **public export can still rely on silent sanitization** — a public candidate/frozen pack can sound clean while readers and reviewers still cannot inspect whether local paths, private registry locators, internal package aliases, or internal-only notes were handled by a reviewable transformation rather than ad hoc editing.

A sharper `0.1` should therefore elevate one more review object:

- `redaction.receipt.json` — records the source surfaces that needed sanitization, the target public surfaces, the redaction status, the concrete transformation operations, and the verification posture that justifies public export without leaking the raw private values themselves.

The practical consequence is that a good pack should now be able to say:

- “this pack became candidate-public only after local paths were generalized and internal aliases were rewritten under a bounded redaction receipt,”
- “this public summary is safe to share because the transformation basis is reviewable even though the raw private notes remain omitted,”
- and “this claimed public export fails consistency because it says redaction was applied but ships no exact receipt for the transformation.”

That keeps the lane honest in one more ordinary failure mode: a public-looking migration contract whose sanitization story remains silent, unreviewable, or purely implied.


## 2026-03-20 omission-register refinement

One more donor sweep still found one ordinary bluff available even after export-posture, publication-surface, redaction, summary-claim, public-trace-path, durable-cue, and surface-authorship refinements:

1. **public surfaces can still sound more complete than they really are** — `publication-surface.manifest.json` can already say what *is* exported, and `redaction.receipt.json` can already say what was sanitized, yet a reader can still be left guessing about known hazards, receipts, or local-only context that were intentionally left off the entry surface for non-redaction reasons;
2. **silence about exclusion is not the same thing as honest narrowing** — a maintainer can keep a summary compact or keep local-only context out of public bundles, but the pack still owes one bounded answer to *what kind of thing was left out, why, and where the nearest safe fallback lives*.

That sharpens **P-0514** one step further with one more review object:

- `omission-register.report.json` — records known-but-not-exported claims, hazards, receipts, or local-only context together with omission reason, target public surface, disclosure posture, and fallback public route.

This keeps the lane honest in two cases that redaction alone does not cover:

- “this candidate-public pack stays compact by leaving local-only rerun notes off the entry summary, and the omission register tells readers that exclusion is intentional rather than accidental,”
- and “this public pack fails consistency because a blocking warning exists somewhere in the bundle but was omitted from the entry surface without one typed omission record.”


# Security / safety model

- Treat imported semver/public-API/suggestion outputs as untrusted input.
- Keep machine-native imports distinguishable from later summaries; `import.receipt.json` must preserve stability posture, consumption mode, and native identity where available.
- Treat imported release-note/changelog/docs/thread surfaces as untrusted until `source-lineage.receipt.json` records a canonical locator and adequate pin status.
- Never synthesize one hazard winner when adjacent authorities disagree but the pack lacks an explicit arbitration rule; degrade to honest abstention/manual review instead.
- Never let a previous-lane manual completion silently satisfy the current lane without an explicit current-lane follow-through state.
- Never claim a machine-fix exists unless its applicability and recipe lane were observed.
- Never let a successful source-only fix imply unattended or whole-lane execution rights; `fixup-posture.report.json` must keep approval and stop conditions explicit.
- Keep remaining review debt structured rather than vibes-based; `review-queue.report.json` must make freeze-blocking work explicit instead of burying it in prose.
- Never permit a freeze verdict or polished summary that contradicts the pack’s own receipts; `cross-register-consistency.report.json` must fail when readiness, source heads, scope, follow-through, posture, export posture, publication surface, public trace paths, or durable public cues disagree.
- Preserve exact tool versions, source identities, checked matrix cells, and capture contexts so upgrade bundles stay auditable.
- Never let an import receipt imply more than its exact package/target/feature/toolchain capture context can justify.
- Never let ambient workspace/default-member/package-selection behavior masquerade as deliberate upgrade-scope intent; `lane-selection.receipt.json` must keep invocation root, workspace attachment, and normalized selection causes explicit.
- Never let hidden Cargo config layers, user-home overrides, `--config` injection, or `[patch]` / source-replacement surfaces masquerade as the ordinary reviewed baseline; `config-basis.receipt.json` must keep resolution/build influence explicit.
- Never let dimension lists masquerade as whole-lane coverage; `coverage-matrix.report.json` must keep unknown and unrequested cells explicit.
- Keep export posture explicit: a pack can be epistemically strong yet still remain private because paths, package aliases, or internal notes need redaction.
- If redaction is claimed as applied on any public surface, ship a `redaction.receipt.json` that records the transformation basis instead of relying on silent sanitization.
- Keep the public surface exact: `publication-surface.manifest.json` should say what is actually exported instead of implying that the whole working tree is the contract.
- Keep decisive public meanings durably visible: `durable-cue.report.json` should stop blockers, supersession, and manual-review boundaries from surviving only as labels or machine-readable register entries.
- Keep public trace routes exact too: `public-trace-path.report.json` should say which public claim routes actually resolve, and should keep fragment/target/private-only misses typed instead of generic.
- If maintainers proceed under an exception, record it as an expiring `deviation-ledger.receipt.json` entry instead of burying it in summary prose.
- Do not let warning labels float free of provenance; `warning-register.report.json` should back the public warning surface with severity, audience, and source refs.
- Support redaction of local paths and internal package names when bundles leave a private workspace.

# Maintenance & governance plan

- Track Cargo semver-check integration, `cargo fix` behavior, suggestion JSON drift, and release-tool ecosystem changes.
- Keep the schema compact and explanation-heavy.
- Maintain fixtures for renamed APIs, feature-policy shifts, config/runtime-profile shifts, explicit review queues, cross-register consistency failures, private-to-public export posture, frozen public-surface exactness, expiring deviations, public warning registers, exact capture contexts, sparse coverage matrices, explicit lane-selection receipts, explicit config-basis receipts, resolvable public trace paths, and typed public trace misses.
- Publish guidance on which upgrade verdicts should block release, stay advisory, or remain local-only.

## 2026-03-20 review-provenance refinement

Two donor pressures kept surviving scrutiny after the earlier passes:

1. **consequential public support can still look more trustworthy than it is** — the bundle can already become exact about lineage, scope, readiness, export posture, redaction, warnings, freshness, and public cues while still leaving one ordinary bluff available: a frozen/public pack can read like a reviewed contract even when nobody independent checked it;
2. **mechanical verification and social review still collapse together** — the lane can already prove that a package builds, that imports were pinned, and that claims trace to receipts, but it still cannot say whether the public freeze surface remained maker-only, passed an independent checker, or only moved forward under a bounded fallback review/deviation.

So this refinement adds one more review object:

- `review-provenance.report.json` — records the maker/checker posture for internal-candidate, public-candidate, or frozen-public surfaces; whether the checker was same-author, same-team, independent, or fallback; whether challenge stayed open or closed; and what decision each review surface actually reached.

That gives the pack one honest way to say:

- “this is still maker-authored working material, not an independently checked frozen contract,”
- “the frozen public surface passed an independent checker and closed without unresolved objection,”
- and “this lane moved under fallback review only, so public trust stays explicitly narrower.”

## 2026-03-20 replay-bridge refinement

One more donor sweep still found one place where the pack could be exact about import truth, capture context, session honesty, and public traceability while still bluffing about how a reviewer actually gets back to the underlying evidence:

> a lane can still read as replayable even when the pack only ships a copied snapshot or a posture label rather than one reviewable replay route.

That gap matters because the current archive already distinguishes **where evidence came from** from **whether several captures belong to one review moment**. What it still did not standardize was the bounded contract for:

- direct command rerun,
- native-storage rerender,
- copied attachment inspection,
- and manual reconstruction or summary-only dead ends.

So this pass adds one more review object:

- `replay-bridge.receipt.json` — records the replay or reconstruction route for imported upgrade evidence, including bridge kind, native locator or attachment refs, copy provenance, expected fidelity, and current usability/blockers.

That lets the pack say, in one compact place:

- “this future-incompat report can still be re-rendered from native Cargo storage by id,”
- “this timing artifact is only inspectable as a copied attachment and should not be described as direct replay,”
- and “this lane advertises replay posture but fails consistency because no actual replay bridge was recorded.”

Without that artifact the pack still permits one ordinary lie: **evidence can sound replayable when the bundle only contains a copied snapshot or an ungrounded posture label**.

## 2026-03-20 config-basis refinement

One more donor sweep still found one place where the pack could be exact about lane selection, capture context, session honesty, replay bridges, and public traceability while still bluffing about why the lane behaved like *this* Cargo invocation rather than another one:

> a lane can still read like an ordinary registry/default/toolchain baseline even when hidden Cargo config layers, environment-variable overrides, or dependency replacement surfaces materially shaped what was resolved or built.

That gap matters because the current archive already distinguishes **which packages/features/targets were selected** from **which capture/session produced the evidence**.
What it still did not standardize was the bounded contract for:

- checked-in versus user-local Cargo config,
- `--config` / environment-variable influence versus ordinary command-line scope,
- and `[patch]` / source-replacement / local-path override surfaces that make a lane less portable or less upstream-representative than it first appears.

So this pass adds one more review object:

- `config-basis.receipt.json` — records which Cargo config layers and override surfaces materially influenced the lane, whether they were repo-checked-in, CI-injected, user-local, or ephemeral, which influence domains they touched, and whether the outcome should be read as portable, repo-local, CI-only, or user-local/nonportable.

That lets the pack say, in one compact place:

- “this lane used a checked-in mirror plus `[patch]` override and should not be summarized as a pure crates.io/default-resolution witness,”
- “this build matched a user-home source replacement and therefore fails consistency until the hidden config basis is disclosed,”
- and “the package/feature selection was explicit, but the resolver/toolchain basis was still ambient and needed its own receipt.”

Without that artifact the pack still permits one ordinary lie: **an upgrade lane can sound like ordinary reviewed Cargo behavior when hidden config or override state materially shaped the witness family**.



## 2026-03-20 baseline-state refinement

One more donor sweep still found one place where the pack could be exact about lane selection, config basis, capture context, session honesty, and replay bridges while still bluffing about what *subject* was actually checked:

> a lane can still sound like a clean release-to-release contract even when the reviewed workspace already contains unpublished edits, partial migration work, or another local drift away from the published baseline.

That gap matters because the current archive already distinguishes **which command/config/session produced the evidence** from **how a reviewer can replay it**.
What it still did not standardize was the bounded contract for:

- pinned published releases versus mutable local workspaces,
- reconstructible package extracts versus already-edited working trees,
- and release-pair claims versus comparison-only or local-only migration notes.

So this pass adds one more review object:

- `baseline-state.receipt.json` — records which subject the lane actually checked, whether it came from a pinned published release, a crate-package extract, a git checkout, or a live workspace, whether that subject was pristine, dirty, partially migrated, or generated, and whether downstream claims remain safe as a release-pair contract or only as a local/comparison note.

That lets the pack say, in one compact place:

- “this lane was checked from a reconstructible extract of the published 1.4.0 crate and may speak as a release-pair contract,”
- “this lane is still useful, but the checked subject was a partially migrated mutable workspace and must not masquerade as a pristine published baseline,”
- and “public summary claims fail consistency until the baseline state is honest about dirty-tree or partial-migration drift.”

Without that artifact the pack still permits one ordinary lie: **an upgrade lane can sound like a clean published release-pair contract when the actual checked subject was already locally drifted or partially migrated**.


## 2026-03-20 surface-authorship refinement

One more donor sweep still found one place where the pack could be exact about source lineage, native imports, review provenance, public summaries, and replay bridges while still bluffing about **what kind of bytes** a reader was actually looking at:

> a lane can still make Cargo-native tool output, maintainer-authored migration guidance, reviewer-authored freeze decisions, and archive-derived summaries feel more interchangeable than they really are.

That gap matters because the current archive already distinguishes **where evidence came from**, **who reviewed the pack**, and **how public claims trace to receipts**.
What it still did not standardize was the bounded contract for:

- tool-generated/native observation,
- maintainer-authored project guidance,
- reviewer-authored governance decisions,
- and archive-derived presentation/synthesis.

So this pass adds one more review object:

- `surface-authorship.report.json` — records the authorship bucket and trust plane for each surfaced receipt or exported surface so native tool output, maintainer guidance, review decisions, and archive-derived summaries cannot quietly inherit one another's meaning.

That lets the pack say, in one compact place:

- “this SemVer JSON is Cargo-native evidence, not maintainer intent,”
- “this migration guide is maintainer-authored guidance, not a native compiler witness,”
- “this freeze result is reviewer-authored governance, not one more release note,”
- and “this public summary sentence is archive-derived presentation even though it traces to exact receipts.”

Without that artifact the pack still permits one ordinary lie: **well-structured receipts can sound like one trust surface even when the bytes were authored by very different actors**.
