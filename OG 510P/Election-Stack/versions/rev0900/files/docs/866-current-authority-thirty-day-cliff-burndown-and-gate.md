# 866 — Current-authority thirty-day cliff burndown and gate

**Track:** Shared / Source freshness / Maintainer operations
**Status:** v855/v856 release-gate coherence repair

**Release:** `v852`  
**Release-date basis:** `2026-06-05`  
**Boundary:** maintainer source triage only; not current voter instruction, legal advice, certification evidence, or live-pilot authorization.

## What changed

The remaining current-authority source-review cliff was burned down before this release. The rev0852 source-pressure report now shows:

```text
expired_review_count: 0
current_authority_due_30d_count: 0
unexpired_due_within_30_days_count: 750
platform_ui_vendor_due_30d_count: 719
pinned_count: 118
```

The current queue artifacts are `artifacts/reports/current-authority-source-queue-rev0852.*`, `artifacts/reports/current-authority-burndown-batches-rev0852.*`, and `artifacts/reports/source-review-pressure-rev0852.*`.

## Why this is substantive

The previous maintenance queue made it easy to spend effort linearly reviewing mutable platform/vendor help pages while official/current-authority rows aged out. `v852` keeps the current-authority queue at zero near-term rows and preserves the platform tail as bounded sampling:

```text
platform_due_count: 719
sample_count: 57
linear_review_avoided_count: 662
```

`scripts/check_current_authority_review_cliff.py` is now the compact guard for this lane. It should fail future releases before current-authority rows drift back into the near-term cliff.

Boundary: the source lockfile is still not a live current-law or voter-instruction service. Rows moved out of the thirty-day cliff were triaged for release-maintenance pressure; they were not converted into legal advice, official voter instructions, or deployment approval.
