# 850 — Platform-source maintenance sampling plan and no-linear-review guard

**Track:** Shared / Source freshness / Refactor  
**Status:** v845 maintainer-load reduction  
**Scope:** `scripts/report_platform_source_sampling_plan.py`, `artifacts/reports/platform-source-sampling-plan-rev0845.csv`, `artifacts/reports/platform-source-sampling-plan-rev0845.json`

## Why this exists

v843 and v844 showed that the near-term source-review queue is dominated by mutable platform/UI/vendor help pages. Reviewing hundreds of vendor pages one by one is a maintainability failure mode: the project can look current while maintainers spend scarce attention on low-authority platform tails instead of current election-authority rows.

v845 adds a bounded generated sampling plan. It groups platform/UI/vendor rows by host and high-value risk bucket, then selects a small host-balanced sample. The sample is not a freshness waiver. It is a triage tool for deciding whether a host/product family changed materially enough to justify deeper refresh.

## Current generated result

Run:

```bash
python3 scripts/report_platform_source_sampling_plan.py \
  --csv artifacts/reports/platform-source-sampling-plan-rev0845.csv \
  --json artifacts/reports/platform-source-sampling-plan-rev0845.json
```

Current v845 output:

- platform/UI/vendor rows due within 30 days: **720**
- distinct platform hosts: **24**
- selected host-balanced samples: **59**
- linear review avoided count: **661**

## Maintainer rule

Review current-authority rows first. Use the platform sample only to detect material host/product changes. Refresh, pin, or demote the subset actually supporting active voter-facing surfaces; do not spend a release turn clicking 720 platform pages linearly.

## Boundary

This refactor does not refresh sources, prove current platform behavior, prove current voter instructions, or authorize live-pilot/legal reliance. It reduces maintainer load so the higher-risk current-authority queue gets attention first.
