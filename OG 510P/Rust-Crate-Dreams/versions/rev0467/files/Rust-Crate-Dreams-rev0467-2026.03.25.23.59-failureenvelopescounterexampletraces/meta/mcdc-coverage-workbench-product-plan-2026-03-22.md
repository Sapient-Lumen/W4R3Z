# MC/DC Coverage Workbench Kit — product plan (2026-03-22)

## Product goal

Ship a crate and cargo-adjacent tool that turns one Rust coverage campaign into a portable, reviewable **MC/DC support bundle**.

The bundle should answer nine questions cleanly:

1. What decision inventory was actually in scope?
2. Which construct classes were supported or unsupported?
3. Which conditions have witnessed independence pairs?
4. What caveat basis constrained the result?
5. What concrete runs and merged profiles back the conclusion?
6. Are two bundles honestly comparable?
7. What qualification story is actually being told?
8. Are the underlying profile artifacts safe for the intended merge/retention/trend claim?
9. What explicit campaign policy and manual-review debt still shape the result?

## v0.1 artifact set

- `decision-authority.receipt.json`
- `construct-support.matrix.json`
- `caveat-basis.receipt.json`
- `mcdc-support-bundle.manifest.json`
- `qualification.note.md`

v0.1 should prefer capture and explanation over ambitious analysis.

## v0.2 additions

- `independence-pair.report.json`
- `evidence-lineage.receipt.json`
- `mcdc-drift.diff.json`
- `campaign-scope.receipt.json`
- `comparison-basis.receipt.json`
- `qualification-basis.receipt.json`
- tiny scenario corpus and release-review diff output

## v0.3 additions

- `profile-compatibility.receipt.json`
- `campaign-policy.receipt.json`
- `manual-review-debt.report.json`
- portable bundle export carrying those receipts

## Suggested crate shape

- core library for schemas and bundle assembly
- cargo subcommand for capture/explain/diff/gate flows
- thin adapters for `cargo-llvm-cov` JSON and selected raw `llvm-cov` export inputs

## Product constraints

- never upgrade `branch_only` evidence into MC/DC evidence
- always preserve unstable/toolchain/known-limitation facts
- keep manual-review-required states explicit
- keep construct support and independence evidence separate
- keep profile-durability claims explicit
- keep policy exclusions separate from support gaps

## Adoption path

1. teams already using source-based coverage capture one bundle per release candidate;
2. CI gates on independence regressions and support-gap disclosures rather than only totals;
3. downstream assurance/reporting tools import the stable JSON artifacts.


## Comparison rule

A future CLI/report surface must refuse to present a simple “improved” or “regressed” verdict unless a `comparison-basis.receipt.json` exists and the comparison is explicitly allowed.

## Durability rule

A future CLI/report surface must refuse to present a retained or long-lived trend claim unless a `profile-compatibility.receipt.json` says the chosen profile inputs are acceptable for that use.
