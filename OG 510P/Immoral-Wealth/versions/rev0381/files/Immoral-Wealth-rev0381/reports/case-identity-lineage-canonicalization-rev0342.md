---
status: report
claim_kind: audit_refactor
route_role: source_currentness_core
route_refs:
- source_currentness_core
- case_work_core
canonical_anchor: false
supersedes: []
depends_on:
- reports/source-alias-and-memo-citation-lineage-repair-rev0340.md
- reports/case-memo-status-drift-and-stale-seed-language-repair-rev0341.md
---

# Case identity lineage canonicalization — rev0355

Revision: `rev0342`  
Base revision: `rev0341`  
Generated: `2026-06-13T10:27:00Z`

## Why this mattered

After the seed-status and memo-source-lineage repairs, the next hidden failure was identity drift. 51 active scoreboards still used memo-style identifiers ending in `-case`, while the file-pairing convention used the canonical case slug without that suffix. That meant the cube could appear internally linked while source-use, field-use, evidence, currentness, and case-ledger rows were not all speaking the same case identity language.

This is a substance problem, not a cosmetic naming issue: case-level evidence can be counted under one ID, currentness under another, and file pairing under a third convention. That makes it easier for a live case to lose proof burdens during later audits.

## Repair performed

- Canonicalized the `case_id` field in 51 scoreboards to match the scoreboard/memo filename base.
- Canonicalized `CASE_LEDGER`, `EVIDENCE_LEDGER`, `currentness-ledger`, `source-use-register`, `SOURCES.json` usage metadata, `field-use-ledger`, and `field-registry`.
- Rebuilt memo-level and scoreboard-level evidence edges using canonical case IDs.
- Preserved memo filenames such as `*-case.md`; only case identity fields and lineage references were normalized.

## Results

```text
pre_repair_scoreboard_case_id_mismatch_count: 51
post_repair_scoreboard_case_id_mismatch_count: 0
post_repair_authoritative_case_id_suffix_count: 0
evidence_edge_count_after_rebuild: 5272
new_sources: 0
new_cases: 0
new_schema_fields: 0
```

## Validator invariant added

The validator now fails if an active scoreboard's `case_id` differs from its filename base, or if authoritative ledgers reintroduce memo-style `-case` identities for active cases.
