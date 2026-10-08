---
id: P-0433
title: MC/DC Coverage Workbench Kit — decision-authority receipts, construct-support matrices, and independence-pair evidence above Rust coverage tooling
status: idea
domains: [testing, safety-critical, coverage, ci, tooling, assurance]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://doc.rust-lang.org/rustc/instrument-coverage.html
  - https://docs.rs/crate/cargo-llvm-cov/latest/source/README.md
  - https://github.com/rust-lang/rust/issues/124118
  - https://llvm.org/docs/CommandGuide/llvm-cov.html
  - https://arxiv.org/html/2409.08708v1
---

# Problem

The archive already had an MC/DC coverage idea, but current Rust sources make the sharper missing value much clearer.

Rust is no longer only talking abstractly about “better coverage someday”.
The 2026 flagship themes now explicitly list **implement MC/DC coverage support** as part of the Safety-Critical Rust story.
At the same time, the practical substrate is still uneven:

- the rustc book documents source-based coverage through `-C instrument-coverage` and still routes detailed mode selection through unstable `-Z coverage-options`;
- `cargo-llvm-cov` already exposes `--branch` and `--mcdc`, but marks them unstable;
- Rust’s own branch-coverage limitations issue is explicit that important constructs such as individual `match` arms, or-patterns, `?`, `.await`, and macro-introduced branches are not yet fully supported;
- and LLVM reporting is real and useful, but raw reports do not tell reviewers whether an MC/DC-looking result covered the right decisions or only the subset that the current toolchain can express.

That means the missing crate is **not** another coverage runner, HTML report skin, or percentage dashboard.
The missing crate is a **qualification-friendly support contract** above coverage runners and reports.
It should help other people answer:

1. which decision family was actually in scope,
2. which language constructs were unsupported or caveat-heavy,
3. whether independence-pair evidence exists for each condition,
4. what concrete test executions produced that evidence,
5. and how results changed across toolchains or source revisions.

# Main judgment

A worthy crate contribution here is an **MC/DC Coverage Workbench Kit** that exports reviewable artifacts instead of just percentages.

This pass now promotes thirteen first-class review objects:

1. `decision-authority.receipt.json` — what source decision inventory was authoritative;
2. `construct-support.matrix.json` — which construct classes were supported, unsupported, or caveat-heavy;
3. `independence-pair.report.json` — whether each condition has witnessed independence pairs;
4. `caveat-basis.receipt.json` — which toolchain / runner / known-limitation facts constrained the result;
5. `evidence-lineage.receipt.json` — which concrete test runs and profile data contributed to the conclusion;
6. `mcdc-drift.diff.json` — what changed across revisions/toolchains/policies;
7. `mcdc-support-bundle.manifest.json` — the portable bundle joining those truths.
8. `campaign-scope.receipt.json` — what packages, targets, test families, and execution lanes were actually in scope.
9. `comparison-basis.receipt.json` — whether two bundles are honestly comparable or blocked by scope/toolchain/support drift.
10. `qualification-basis.receipt.json` — what assurance story the campaign can conservatively support.
11. `profile-compatibility.receipt.json` — whether retained/merged profile inputs are safe for the intended claim.
12. `campaign-policy.receipt.json` — what support-class / construct-family policy the campaign explicitly adopted.
13. `manual-review-debt.report.json` — what unsupported or caveat-heavy work still needs human review.

The key correction is simple:
**MC/DC support is not a scalar.**
It is a contract about decision scope, construct support, independence evidence, caveat basis, and lineage.

# What it should provide other people

1. **Decision-authority truth** — what source decisions are being measured, and whether the inventory came from compiler output, a normalized source walk, or a manual review supplement.
2. **Construct-support honesty** — explicit visibility into unsupported branching forms, partial support, or policy exclusions.
3. **Independence-pair evidence** — a condition-by-condition record of whether MC/DC was actually demonstrated.
4. **Evidence lineage** — a trace from high-level verdicts back to concrete runs, profraw/profdata inputs, and selected runners.
5. **Caveat receipts** — machine-readable reasons why a result is partial, experimental, unstable, or manual-review-required.
6. **Diffable support bundles** — portable artifacts that can be compared across compiler updates, code changes, and policy changes.
7. **Audit-grade summaries** — a small human-readable note that stays aligned with the machine-readable receipts.
8. **Campaign-scope truth** — explicit visibility into which packages, targets, doctest lanes, external harnesses, and execution environments were actually included.
9. **Comparison honesty** — a conservative answer to whether two bundles can be trended together at all.
10. **Qualification honesty** — a conservative statement of whether the evidence is exploratory, evidence-only, mixed host/target, or review-ready-with-caveats.
11. **Profile/input durability truth** — explicit visibility into whether profile artifacts are safe for merge, retention, or cross-run trends.
12. **Campaign-policy truth** — an explicit record of what support bar and exclusions the campaign adopted.
13. **Manual-review debt visibility** — a machine-readable queue of unresolved unsupported or caveat-heavy obligations.

# Proposed artifacts

- `decision-authority.receipt.json`
  - decision inventory source (`compiler_export`, `source_normalization`, `manual_augmented`)
  - whether match-arm-like constructs were counted or explicitly excluded
  - normalization/rewrite policy
  - authority class (`exact`, `conservative`, `manual_review_required`)

- `construct-support.matrix.json`
  - rows for construct families such as `if`, `while`, `lazy_bool`, `let_else`, `match_arm`, `or_pattern`, `question_mark`, `await`, `macro_generated`
  - status: `supported`, `partially_supported`, `unsupported`, `excluded_by_policy`
  - evidence refs and review notes

- `independence-pair.report.json`
  - decision id / condition id
  - expected pair count
  - witnessed pair count
  - verdict: `demonstrated`, `partial`, `not_demonstrated`, `not_applicable`, `blocked_by_support_gap`
  - optional witness references back to test cases or coverage data

- `caveat-basis.receipt.json`
  - rustc / llvm / llvm-cov / cargo-llvm-cov versions when known
  - instrumentation mode and unstable flags
  - imported known-limitation references
  - exactness class (`experimental`, `stable_branch_only`, `mcdc_preview`, `manual_review_required`)

- `evidence-lineage.receipt.json`
  - which runs, runners, merged profiles, and filters contributed
  - whether doctests / build scripts / dependencies / external harnesses were included
  - merge policy and exclusions

- `campaign-scope.receipt.json`
  - selected packages / targets / target triples
  - whether unit tests / integration tests / doctests / proc-macros / build scripts / external harnesses were included
  - execution class (`host_only`, `on_target`, `mixed_host_target`)

- `comparison-basis.receipt.json`
  - left/right bundle ids
  - comparability verdict (`like_for_like`, `scope_drift`, `toolchain_drift`, `support_drift`, `not_comparable`, `manual_review_required`)
  - blocking reasons and imported refs

- `qualification-basis.receipt.json`
  - qualification class (`exploratory`, `evidence_only`, `review_ready_with_caveats`, `manual_review_required`)
  - target execution class
  - normative/imported basis refs and notes on host-vs-target gaps

- `profile-compatibility.receipt.json`
  - input profile class (`raw_profraw`, `indexed_profdata`, `mixed`)
  - intended use (`single_campaign_merge`, `cross_run_compare`, `long_lived_retention`)
  - compatibility verdict and producer/tool basis
  - blocking reasons for unsafe retention or comparison claims

- `campaign-policy.receipt.json`
  - policy id / owner
  - required support class and gate posture
  - construct-family requirements (`required`, `allowed_with_caveats`, `excluded_until_supported`, `manual_review_route`)
  - execution requirement for exploratory vs release-gate use

- `manual-review-debt.report.json`
  - debt items for unsupported constructs, macro visibility gaps, profile durability gaps, host-target gaps, or policy exceptions
  - severity / owner / close condition

- `mcdc-drift.diff.json`
  - `decision_inventory_changed`, `support_class_changed`, `independence_gained`, `independence_lost`, `lineage_changed`, `caveat_changed`, `manual_review_required`

- `mcdc-support-bundle.manifest.json`
  - bundle members, hashes/ids, summary counts, and release-review pointers

# Commands / UX sketch

- `cargo mcdc capture`
  - collect source/coverage facts and emit a support bundle
- `cargo mcdc explain <decision>`
  - explain decision authority, construct support, and independence evidence
- `cargo mcdc diff old.bundle new.bundle`
  - compare two runs or revisions
- `cargo mcdc caveats`
  - print concise caveat basis with linked limitation ids
- `cargo mcdc gate`
  - fail on policy-relevant states such as `blocked_by_support_gap`, `manual_review_required`, or independence regressions

# Persona / who it’s for

- safety-critical software teams
- verification and validation engineers
- toolchain qualification teams
- maintainers of coverage-reporting / assurance tooling
- library or platform teams who need conservative evidence rather than optimistic percentages

# User stories

- **Assessor**: “Show me which decision families were actually in scope, and which language constructs the current toolchain still does not support.”
- **QA engineer**: “Open one bundle and see decision inventory, independence evidence, caveats, and lineage without recreating the run.”
- **Maintainer**: “Compare this compiler upgrade against the previous run and tell me whether support improved, only caveats changed, or results became incomparable.”
- **CI owner**: “Gate on independence regressions and unsupported construct classes, not on one raw overall percentage.”
- **Downstream integrator**: “Import a compact JSON bundle instead of scraping `llvm-cov` text output.”

# Prior art (and why it’s insufficient)

- rustc source-based coverage already instruments functions and branches and emits profile data.
- `cargo-llvm-cov` already wraps the workflow and exposes unstable `--branch` and `--mcdc` switches.
- LLVM’s `llvm-cov` already emits reports/export formats.
- Rust’s branch-coverage issue tracker already documents concrete unsupported constructs.

What is still missing is the **support-contract layer** above those primitives.
None of the existing pieces by itself says whether a reported MC/DC result covers the right decision inventory, whether unsupported constructs were excluded, or what lineage backs each independence claim.

# Design goals

1. **Decision-first** — percentages are secondary to decision/condition truth.
2. **Caveat-first** — limitations are core artifacts, not footnotes.
3. **Lineage-first** — verdicts must trace back to concrete runs and profile inputs.
4. **Support-matrix-aware** — unsupported construct classes are normal results, not hidden failures.
5. **Diffable** — results must compare cleanly across toolchains and revisions.
6. **Qualification-friendly** — stable, conservative receipts over flashy dashboards.
7. **Runner-neutral above substrate** — import existing runners and reporting tools rather than replacing them.

# MVP surface

- Minimal types: `DecisionAuthorityReceipt`, `ConstructSupportMatrix`, `IndependencePairReport`, `CampaignScopeReceipt`, `CaveatBasisReceipt`, `ComparisonBasisReceipt`, `QualificationBasisReceipt`, `ProfileCompatibilityReceipt`, `CampaignPolicyReceipt`, `ManualReviewDebtReport`, `EvidenceLineageReceipt`, `McdcDiff`, `McdcSupportBundle`
- Minimal functions:
  - `capture_decision_authority()`
  - `classify_construct_support()`
  - `collect_independence_pairs()`
  - `record_caveat_basis()`
  - `record_campaign_scope()`
  - `record_profile_compatibility()`
  - `record_campaign_policy()`
  - `derive_manual_review_debt()`
  - `record_evidence_lineage()`
  - `compare_bundles()`
  - `qualify_bundle()`
  - `diff_support_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo-llvm-cov`
  - `llvm-cov-json`
  - `nextest`
  - `doctests`
  - `serde`

# Compatibility story

- Stable-first mode can still record decision authority, construct-support gaps, and lineage for ordinary `-C instrument-coverage` runs.
- Higher-fidelity mode can import unstable branch/MC/DC modes when present.
- Must preserve whether a result is `branch_only`, `condition_only`, `mcdc_preview`, or `manual_review_required`.
- Must preserve whether evidence was host-only, on-target, or mixed host/target.
- Must never trend two bundles together without an explicit comparison-basis receipt.
- Should remain useful before and after eventual upstream MC/DC maturation because support receipts and lineage still matter.

# Conformance & fixtures

- `match_arms_excluded_even_when_if_paths_have_mcdc_evidence` — partial decision inventory because match-arm constructs remain unsupported.
- `independence_pairs_need_test_lineage_not_just_percentages` — independence evidence is present only if linked back to concrete runs.
- `cargo_llvm_cov_mcdc_preview_requires_caveat_basis` — unstable runner flags require explicit caveat receipts.
- `branch_and_mcdc_results_must_not_share_authority_without_receipt` — a branch-coverage result and an MC/DC claim must not silently share the same authority class.
- `macro_generated_branches_need_manual_review_route` — macro-introduced branches can force a conservative/manual-review verdict.
- `doctest_omission_changes_campaign_scope_even_when_decision_counts_look_similar` — doctest scope changes must block silent trend claims.
- `toolchain_and_support_drift_block_like_for_like_mcdc_trend_claim` — scope/support/toolchain drift must be surfaced before diffing.
- `host_run_only_is_not_the_same_qualification_story_as_on_target_execution` — host evidence and target qualification are not the same story.
- `raw_profraw_is_not_durable_trend_input_without_profile_receipt` — raw profiles are useful for a campaign, but unsafe as unqualified long-lived trend inputs.
- `campaign_policy_excludes_match_arms_until_upstream_support_arrives` — unsupported constructs need explicit campaign policy, not silent omission.
- `unsupported_question_mark_and_macro_paths_create_manual_review_debt` — a green automation run can still leave blocking review debt.

# Path to boring stability

- Stabilize `decision-authority.receipt.json`, `construct-support.matrix.json`, and `independence-pair.report.json` before richer dashboards.
- Treat unsupported construct classes as first-class outcomes.
- Keep imported tool outputs and known-limitations references explicit.
- Prefer conservative summaries over optimistic global percentages.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that capture one coverage campaign, emit a decision-authority receipt, a construct-support matrix, an independence-pair report, a caveat basis, and a lineage receipt, and then package them into a diffable support bundle.

# De-risk plan

1. Start with evidence capture and comparison, not report theming.
2. Import known compiler limitations as explicit receipts instead of trying to outsmart them.
3. Keep profile-compatibility and long-lived-retention claims explicit instead of implicit.
4. Publish review debt even when the automated run is green.
4. Prove the schemas on a tiny scenario corpus before adding broader CI/policy automation.

# Non-goals

- Not a replacement for rustc or LLVM coverage instrumentation.
- Not a replacement for `cargo-llvm-cov`.
- Not a certification package by itself.
- Not a promise that current MC/DC support is complete across all Rust constructs.
- Not a generic test coverage dashboard.

# Architecture & API sketch

```rust
pub enum SupportClass {
    BranchOnly,
    ConditionOnly,
    McdcPreview,
    ManualReviewRequired,
}

pub fn capture_decision_authority(root: &Path) -> Result<DecisionAuthorityReceipt>;
pub fn classify_construct_support(receipt: &DecisionAuthorityReceipt) -> Result<ConstructSupportMatrix>;
pub fn collect_independence_pairs(bundle: &CoverageInputs) -> Result<IndependencePairReport>;
pub fn record_caveat_basis(inputs: &CoverageInputs) -> Result<CaveatBasisReceipt>;
pub fn record_evidence_lineage(inputs: &CoverageInputs) -> Result<EvidenceLineageReceipt>;
```

Bundle draft: `decision-authority.receipt.json`, `construct-support.matrix.json`, `independence-pair.report.json`, `caveat-basis.receipt.json`, `evidence-lineage.receipt.json`, `mcdc-drift.diff.json`, `mcdc-support-bundle.manifest.json`, `qualification.note.md`.

# Security / safety model

- Preserve exact toolchain and runner provenance so evidence stays reviewable.
- Support redaction of private paths and internal test names in exported bundles.
- Never silently upgrade branch-only evidence into MC/DC evidence.
- Keep manual-review-required states explicit and sticky.

# Maintenance & governance plan

- Track upstream rustc / LLVM / cargo-llvm-cov support changes and limitation issues.
- Maintain a compact construct-support taxonomy and tiny scenario corpus.
- Keep adapters thin and schema-first.
- Publish guidance for interpreting independence evidence conservatively.

# Milestones

## 0.1
- decision-authority receipt
- construct-support matrix
- caveat-basis receipt
- bundle export

## 0.2
- independence-pair report
- evidence-lineage receipt
- diff support bundles
- tiny scenario corpus

## 1.0
- stable core schemas
- release-review templates
- downstream import guidance

# Open questions

- What is the smallest decision inventory that still helps real reviews?
- How should the crate encode “construct unsupported” vs “construct excluded by policy”?
- Which lineage granularity is enough for independence-pair review without becoming too noisy?
- Which upstream limitation ids deserve first-class taxonomy in the MVP?
