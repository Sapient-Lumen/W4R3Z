# MC/DC coverage workbench — profile compatibility and review-debt plan (2026-03-22)

## Product goal

Deepen **P-0433 MC/DC Coverage Workbench Kit** so that a bundle can answer not only “what evidence exists?” and “are two bundles comparable?” but also:

1. whether the underlying profile artifacts are safe for the intended merge / retention / trend claim,
2. what construct-policy bar the campaign explicitly adopted,
3. and what manual-review debt still remains after automation stops.

## New first-class artifacts

- `profile-compatibility.receipt.json`
  - input profile classes (`raw_profraw`, `indexed_profdata`, `mixed`)
  - producer basis (`rustc`, `llvm-profdata`, `llvm-cov`, wrapper version when known)
  - compatibility verdict (`same_producer_only`, `indexed_backward_only`, `not_forward_compatible`, `not_durable_for_trend`, `manual_review_required`)
  - intended use (`single_campaign_merge`, `cross_run_compare`, `long_lived_retention`)
  - notes on blocking reasons

- `campaign-policy.receipt.json`
  - policy id and owner
  - required support class (`branch_only`, `mcdc_preview`, `manual_review_required`)
  - construct-family requirements (`required`, `allowed_with_caveats`, `excluded_until_supported`, `manual_review_route`)
  - execution requirement (`host_ok_for_exploration`, `target_required_for_gate`)
  - gate posture (`advisory`, `review_gate`, `release_gate`)

- `manual-review-debt.report.json`
  - debt items with class (`unsupported_construct`, `macro_visibility_gap`, `profile_durability_gap`, `host_target_gap`, `policy_exception`)
  - affected decisions / construct families / scope refs
  - severity and owner
  - close condition / expected evidence

## Suggested commands / UX

- `cargo mcdc inspect-inputs`
  - emit `profile-compatibility.receipt.json`
- `cargo mcdc policy show`
  - emit the active `campaign-policy.receipt.json`
- `cargo mcdc debt`
  - emit `manual-review-debt.report.json` derived from support gaps, scope gaps, and policy rules

## Theory-of-practice rule

Never present a retained MC/DC bundle as durable evidence unless a `profile-compatibility.receipt.json` says the underlying inputs are acceptable for that use.

Never let “unsupported by toolchain” silently become “ignored by campaign” unless a `campaign-policy.receipt.json` says so.

Never let a green automated run imply that review debt is zero; publish a `manual-review-debt.report.json` even when the queue is empty.

## MVP order

1. stabilize `profile-compatibility.receipt.json`,
2. stabilize `campaign-policy.receipt.json`,
3. stabilize `manual-review-debt.report.json`,
4. teach `mcdc-support-bundle.manifest.json` to carry them,
5. add tiny scenario fixtures and diff output,
6. only then add stronger release gating.
