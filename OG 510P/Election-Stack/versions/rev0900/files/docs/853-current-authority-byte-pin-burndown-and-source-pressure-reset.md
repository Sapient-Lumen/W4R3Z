# Current-authority byte-pin burndown and source-pressure reset

**Track:** Shared / Source freshness / Maintainer operations
**Status:** v846 source-risk reduction and queue refactor  
**Scope:** `evidence/lock/external-sources.toml`, `artifacts/reports/current-authority-byte-pin-burndown-rev0846.*`, `artifacts/reports/source-review-pressure-rev0846.*`, `artifacts/reports/current-authority-source-queue-rev0846.*`, `artifacts/reports/platform-source-sampling-plan-rev0846.*`

## What changed

v845 correctly showed that the source problem should not be handled by another linear review queue. v846 follows that rule by pinning durable bytes for a focused current-authority slice first, then regenerating the review-pressure maps.

The burndown report records:

```text
pinned current-authority sources: 31
attempted but left unpinned: 4
expired source-review windows: 0
```

The current v846 pressure snapshot is:

```text
total source rows: 1216
pinned rows: 118
unexpired rows due within 30 days: 862
current-authority due within 30 days: 90
state/local authority due within 30 days: 22
current-authority queue total: 112
platform/UI/vendor due within 30 days: 719-726 depending on host-tail classifier
platform sample rows: 62
linear platform reviews avoided by sampling: 664
```

## Why this matters

The risky failure was not merely stale citations. The risky failure was maintainer attention being swallowed by hundreds of mutable platform/UI/vendor pages while more consequential election, cyber, accessibility, and state/local authority rows waited. v846 reduces the current-authority queue with real byte pins and keeps the platform lane as a sampling/consolidation task.

## Classifier refactor

`artifacts/reports/current-authority-classifier-refactor-rev0846.md` records the audit/refactor side of this pass. The queue no longer treats `official_websites`, broad `ai`, or public-communications tags alone as current election/cyber authority. Vendor/browser/link-preview documentation remains important, but it belongs in the platform/source-tail lane unless hosted by an election, cyber, standards, accessibility, or state/local authority.

## Boundary

Pinned bytes are not current voter instructions, legal advice, live-pilot authorization, or proof that a source remains policy-current. A byte pin only makes a reviewed artifact reproducible. Landing pages and voter-facing current instructions still require jurisdiction-specific review before any live use.

The four attempted-but-unpinned rows remain explicit in `artifacts/reports/current-authority-byte-pin-burndown-rev0846.md`; do not silently extend their `review_by` dates.
