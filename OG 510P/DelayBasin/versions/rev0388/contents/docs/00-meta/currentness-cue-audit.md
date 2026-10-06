# Currentness cue audit

This generated surface exposes high-risk current/latest/head cues so stale terse keys cannot hide behind a green lint count.

- Revision: `rev0374`
- Bundle: `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`
- Resolved question: `OQ-0265`
- Live successor: `OQ-0266`
- Failures: `0`

## Non-claim
currentness-cue-court, latest-head-tribunal, status-sovereign, bundle-revision-notary, recency-court, landing-cue-authority, green-lint-currentness-waiver, and current-key-senate are forbidden; this surface detects stale current cues but does not certify semantic truth or continuation authority.

## Status fields
- `SURFACE-STATUS.json#revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#current_revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#current_head` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#latest_revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#operational_head.revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#citation_head.revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#status_lanes.revision` — expected `rev0374`, observed `rev0374`: `pass`
- `SURFACE-STATUS.json#latest_bundle` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#current_bundle` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#latest_archive` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#frozen_public_surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#current_release_surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#operational_head.surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#citation_head.surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#status_lanes.current_release_surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#status_lanes.frozen_public_surface` — expected `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, observed `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`: `pass`
- `SURFACE-STATUS.json#previous_revision` — expected `rev0373`, observed `rev0373`: `pass`

## Landing cues
- `README.md` — revision `rev0374`, bundle `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, successor `OQ-0266`: `pass`
- `START_HERE.md` — revision `rev0374`, bundle `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, successor `OQ-0266`: `pass`
- `AGENTS.md` — revision `rev0374`, bundle `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, successor `OQ-0266`: `pass`
- `docs/README.md` — revision `rev0374`, bundle `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`, successor `OQ-0266`: `pass`

## Known repaired findings
- `rev0327-surface-status-current-revision-stale` — SURFACE-STATUS.json carried current_revision=rev0325 while the package head was rev0327; prior green lint did not catch that terse currentness key. Repair: rev0328 sets SURFACE-STATUS.current_revision to the current revision and adds generated currentness-cue auditing plus a direct status-field guard.

## Scan policy
- Scope: high-risk current/latest/head revision and bundle cues plus exact compact hot-current-support lists in root reentry surfaces
- Historical exclusions: previous_revision, origin_revision, anchor.expected_head, anchor.observed_head, historical_witness=true subtrees, older ledger rows
- Repair: fail closed on terse current-key drift; route semantic overclaim to the successor question instead of creating a currentness court
