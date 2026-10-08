---
revision_current: rev0355
status: audit_report
claim_kind: source_lineage_refactor
route_role: evidence_lineage_core
canonical_anchor: false
route_refs:
- evidence_lineage_core
- temporal_currentness_core
source_refresh_due: 2026-09-30
---

# rev0340 source-alias and memo-citation lineage repair

## Why this was risky

rev0339 repaired the validator callchain and active-case currentness coverage, but the source-use layer still had a blind spot: case memos could cite sources in narrative text without those citations appearing in `SOURCES.json`, `source-use-register.json`, or `EVIDENCE_LEDGER.json` lineage. That meant a source could be substantively used by a case while the source register treated it as unused or less broadly used.

A second risk was duplicate-source drift. Several high-pressure current-law sources had two active IDs for the same URL. That is especially dangerous for BOI, estate/gift, charitable vehicles, Treasury insurance, JCT tax expenditures, and household-credit sources, because the wrong duplicate row can carry weaker source type, stale date, or looser refresh cadence.

## What changed

- Canonicalized active case payloads and case memos from retained duplicate aliases to canonical source IDs.
- Preserved all source rows for historical traceability; aliases are now marked `retained_alias` and `alias_of`.
- Integrated case-memo `[S###]` citations into source-use lineage and the evidence ledger.
- Tightened the BOI current-status source and the paired U.S. BOI reversal case to a `2026-09-30` refresh date.
- Added validator checks so retained aliases cannot silently return to active case payloads or case memos.

## Counts

- Scoreboard source-id replacements: **124**
- Case-memo source-reference replacements: **35**
- Canonicalized duplicate alias groups: **19 aliases** across **19 canonical source rows**
- Case-memo citation edges added to `EVIDENCE_LEDGER`: **466**
- Remaining active alias references: **0**

## Substantive effect

The cube now treats narrative case citations as live evidence lineage, not just human-readable prose. This matters because many of the oldest portfolio memos contain broad narrative source strings that shape the case theory even when the structured scoreboard has already been hardened.

The highest-risk current-law repair is BOI. `S169` is now the canonical current-status page, with refresh due `2026-09-30`, and `united-states-beneficial-ownership-reversal-rev0309` now shares that cadence. This prevents a domestic-company BOI exemption source from being carried on a slower, generic annual refresh schedule.
