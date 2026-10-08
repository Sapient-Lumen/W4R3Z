# 847 — Platform/UI source-tail audit and consolidation map

**Track:** Shared / Source freshness / Refactor  
**Status:** maintainer audit helper, non-authoritative  
**Revision:** v843

## Why this exists

The v842 source-pressure report showed that the source queue is not one queue. The largest near-term burden is platform/UI/vendor documentation, not election-authority currency. Reviewing that lane linearly would spend scarce maintainer time on mutable support pages while higher-risk current-authority rows still need attention.

rev0843 adds:

```bash
python3 scripts/report_platform_source_tail.py
```

Generated outputs:

```text
artifacts/reports/platform-source-tail-rev0843.csv
artifacts/reports/platform-source-tail-rev0843.json
```

## Current result

As of the 2026-06-04 release review date:

```text
platform_due_count: 720
distinct_platform_hosts: 24
top_10_hosts_due_count: 673
top_10_hosts_share: 0.9347
```

The refactor implication is direct: this is a host/product-family consolidation problem, not a click-through-every-row problem.

The largest host clusters are currently support.google.com, developer.mozilla.org, support.microsoft.com, w3.org, help.vimeo.com, designsystem.digital.gov, developers.google.com, helpx.adobe.com, support.apple.com, and digital.gov.

## How to use the report

Use this report to decide which platform pages should remain release-blocking evidence, which should become sampled watchlist rows, and which should be collapsed into router docs or durable invariants.

Recommended action pattern:

```text
current authority rows -> review first
state/local adoption rows -> review before any local use
platform/UI rows -> consolidate by host/product family; sample high-risk voter-facing behavior
vendor media-player minutiae -> demote unless directly voter-facing
accessibility standards/guidance -> prefer durable pinned standards over repeated article refresh
```

## Boundary

The report does not refresh sources, prove current platform behavior, prove current voter instructions, or authorize voter-facing deployment. It prevents waste by making the platform tail visible as a small number of host clusters rather than 720 unrelated tasks.
