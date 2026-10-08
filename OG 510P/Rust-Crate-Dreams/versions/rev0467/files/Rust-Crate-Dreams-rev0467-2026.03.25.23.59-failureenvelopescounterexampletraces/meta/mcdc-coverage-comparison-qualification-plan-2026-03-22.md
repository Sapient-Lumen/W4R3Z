# MC/DC coverage workbench — comparison and qualification plan (2026-03-22)

## Product goal

Deepen **P-0433 MC/DC Coverage Workbench Kit** so that a bundle can answer not only “what evidence exists?” but also:

1. what exact campaign scope produced it,
2. whether two bundles are honestly comparable,
3. and what qualification class the evidence can support.

## New first-class artifacts

- `campaign-scope.receipt.json`
  - selected packages / targets / test families
  - whether doctests, proc-macros, build scripts, external harnesses, and FFI coverage were in scope
  - execution class (`host_only`, `on_target`, `mixed_host_target`)
  - profile merge boundaries and exclusions

- `comparison-basis.receipt.json`
  - left/right bundle ids
  - comparability verdict (`like_for_like`, `scope_drift`, `toolchain_drift`, `support_drift`, `not_comparable`, `manual_review_required`)
  - blocking reasons and imported evidence refs
  - human-readable summary safe to paste into release review notes

- `qualification-basis.receipt.json`
  - qualification class (`exploratory`, `evidence_only`, `review_ready_with_caveats`, `manual_review_required`)
  - target execution class
  - normative/imported basis refs
  - notes on unstable flags, host-vs-target gaps, and manual review obligations

## Suggested commands / UX

- `cargo mcdc scope`
  - emit the campaign-scope receipt before or after a run
- `cargo mcdc compare old.bundle new.bundle`
  - emit a comparison-basis receipt before showing deltas
- `cargo mcdc qualify bundle`
  - emit a qualification-basis receipt from current caveat/scope/import facts

## Theory-of-practice rule

Never show a trend line, regression, or improvement claim unless a `comparison-basis.receipt.json` exists and says the bundles are either `like_for_like` or conservatively comparable with explicit caveats.

Never let a host-only run masquerade as an on-target qualification story.

Never let omitted doctests, external harnesses, or target-family differences hide inside raw percentages.

## MVP order

1. stabilize `campaign-scope.receipt.json`,
2. stabilize `comparison-basis.receipt.json`,
3. stabilize `qualification-basis.receipt.json`,
4. teach `mcdc-support-bundle.manifest.json` to carry them,
5. add tiny scenario fixtures and diff output,
6. only then add stronger CI/release gating.
