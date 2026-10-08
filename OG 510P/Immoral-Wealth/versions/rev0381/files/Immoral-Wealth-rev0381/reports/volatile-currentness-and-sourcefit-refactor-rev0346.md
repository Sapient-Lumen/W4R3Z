---
status: audit_report
claim_kind: release_audit
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
- source_governance_core
- temporal_currentness_core
revision_current: rev0355
---

# Volatile currentness and source-fit refactor — rev0355

## Why this release exists

rev0345 repaired front-door truth drift. rev0346 moves back to substance: the cube was most exposed where fast-moving current-law/data surfaces and overstrong source-fit labels could quietly make active cases sound more settled than they are.

## Substantive changes

- Added **S490** for the Federal Reserve Z.1 current release and bound it to the U.S. portfolio case plus the macro-consistent wealth-accounts case.
- Added **S491** for FinCEN's BOI IFR Q&A and bound it to the U.S. BOI reversal case so the U.S.-person reporting exclusion is explicit.
- Added **S492** for FERC RM26-4 and bound it to the AI/data-center grid-water public-backstop case as the live large-load docket.
- Refreshed the medical-debt case so S285 is historical context after vacatur and S458 remains the current-law anchor.
- Marked the CFPB consumer-reporting-company list as coverage-caveated for medical-debt, data-broker, and tenant-screening use.

## Audit/refactor changes

The source-fit refactor corrected these rows: S106, S117, S12, S131, S283, S285, S310, S318, S339, S343, S390, S393, S407, S424. The largest correction is conceptual: `source_type=official` is no longer allowed to hide nonprofit modeling, advocacy/tracker material, professional references, coverage-caveated lists, historical rule notices, or national-lab technical evidence.

A second guardrail corrected a wasteful partial-generation pattern: repeated memo mentions no longer inflate the evidence ledger. Case-memo narrative citations are represented once per case/source pair while scoreboard claim paths remain claim-specific.

## Counts

- Case memos: **95**
- Scoreboards: **95**
- Sources: **492**
- Registered field keys: **367**
- Registered-unused fields: **50**
- Evidence edges: **5435**

## What remains risky

The cube still needs exact DFA/WID share extraction, state/vendor/project-level evidence for credit-reporting and AI/data-center cost allocation, and a broader source metadata migration if `source_type`, provenance, source fit, and evidence role are to be split cleanly across all 492 source rows.

Validation expectation: `PASSED: 0 errors, 0 warnings`.
