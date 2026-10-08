# 845 — Source-review pressure refactor and maintainer-attention map

**Track:** Shared / Release / Source freshness / Refactor  
**Status:** maintainer audit helper, non-authoritative  
**Revision:** v842

## Why this exists

The source-review queue is no longer usefully described as "893 sources due within 30 days." That number is true, but it invites wasteful linear review. The risky work is not to click every vendor support page. The risky work is to separate current election/cyber authority from platform UI sprawl and durable standards.

rev0842 adds a small generator rather than another hand-maintained registry:

```bash
python3 scripts/report_source_review_pressure.py
```

Generated outputs:

```text
artifacts/reports/source-review-pressure-rev0842.csv
artifacts/reports/source-review-pressure-rev0842.json
```

## Current pressure picture

As of the v842 review date, the lockfile still has zero expired source-review windows. The near-term burden remains large: 893 unpinned sources are due within 30 days. The pressure map splits that into action lanes:

```text
current_authority_due_30d: 142
platform_ui_vendor_due_30d: 720
citation_backfill_due_30d: 25
durable_standard_due_30d: 4
legal_reference_due_30d: 1
other_due_30d: 1
```

The key refactor is practical: do not review `platform_ui_vendor_due_30d` linearly. Sample and consolidate that lane, and spend scarce currentness work first on `current_authority_due_30d`, state/local adoption claims, and any voter-facing special-case use.

## How this changes maintainer behavior

The next source-refresh pass should not mechanically extend `review_by` dates. It should choose one of four actions per lane:

1. refresh and keep as current authority;
2. pin immutable bytes where a stable version exists;
3. demote to informative `xref:` when current authority is not needed;
4. remove or consolidate when multiple UI-cue documents are repeating the same point.

The platform-media/authenticity-cue family should be compressed by router and evidence pattern. The audit shows that most near-term source pressure is now platform-vendor behavior, not core election standards.

## Boundary

This report does not refresh any external source. It does not prove current law, current voter instructions, or current platform behavior. It is a maintainer attention map to avoid wasting the next revision on hundreds of low-value support-page checks while higher-risk authority lanes wait.
