---
project: Immoral Wealth
status: substantive_risk_sprint
claim_kind: archive_refactor_and_claim_migration
route_role: archive_governance_core
canonical_anchor: true
revision_current: rev0357
base_revision: rev0356
codename: substantive-risk-claim-migration-and-field-pruning-sprint
generated_at: 2026-06-18T08:54:15Z
---

# Substantive risk, claim migration, and field-pruning sprint — rev0357

## Executive result

This revision does not add more doctrine, sources, cases, or schema fields. It moves the archive toward the work that is most likely to remain unfinished if deferred: **claim-level evidence migration, case maturity honesty, report-provenance quarantine, and schema pruning.**

The central correction is that the cube now carries its epistemic status in live machine files, not only in a narrative audit:

- `cases/EVIDENCE_LEDGER.json` declares its rows as mechanical associations and sets `verified_claim_edge_count` to **0**.
- `cases/CASE_LEDGER.json` now separates `workflow_status` from `evidentiary_maturity`, `certification_status`, and `claim_lineage_status`.
- `cases/MECHANICAL_EVIDENCE_SUMMARY.json` and `cases/CLAIM_ATOM_BACKLOG.json` give the next operator a ranked claim-migration queue.
- `docs/00-meta/report-provenance-quarantine.json` hashes historical reports and marks unreliable revision metadata instead of letting old reports roll forward.
- `docs/00-meta/field-retirement-candidate-ledger.json` turns zero-use schema sprawl into a staged retirement list.

## Counts that matter now

| Measure | Value |
|---|---:|
| Case memos | 95 |
| Scoreboards | 95 |
| Sources | 537 |
| Registered schema fields | 367 |
| Registered unused fields | 50 |
| Mechanical evidence associations | 6793 |
| Unique case-source pairs | 670 |
| Verified claim edges | 0 |
| P0 claim-lineage cases | 10 |
| Zero-use retirement candidates | 50 |

## Riskiest work advanced

### 1. Claim evidence migration is no longer optional

The archive can no longer pass while silently allowing an operator to treat association rows as verified evidence. The new evidence summary names the mechanical-association count, the unique-pair compression, the source-quality mix, and the top cases by evidence multiplication. The claim atom backlog selects the first cases and claim seeds to migrate.

The practical next move is not to add sources. It is to take the top P0 items and produce exact locator-bounded claim edges with relationship codes: support, qualification, contradiction, context-only, or method-only.

### 2. Case maturity now blocks certification

All cases remain in workflow, but they are not certified current. The case ledger now carries `evidentiary_maturity: working_claim_lineage_needed` and `certification_status: not_certified_current` for every case. This prevents portfolio membership from being mistaken for proof.

### 3. Historical reports are quarantined without rewriting them

The report quarantine records **60** JSON revision mismatches and **61** Markdown revision mismatches, plus the shared report-generation timestamp cluster. The repair preserves bytes and hashes, while stopping old report metadata from driving current counts or truth claims.

### 4. The schema refactor has begun without breaking scoreboards

The field registry still supports existing case files, but all **50** zero-use fields are marked as retirement candidates. The acceptance test is concrete: if a field remains unused through the observation window, remove it or alias it instead of letting schema surface area grow forever.

## Audit/refactor files to use next

1. `docs/00-meta/high-risk-substantive-work-queue.md`
2. `cases/CLAIM_ATOM_BACKLOG.md`
3. `cases/MECHANICAL_EVIDENCE_SUMMARY.md`
4. `cases/CASE_MATURITY_LEDGER.md`
5. `docs/00-meta/field-retirement-candidate-ledger.md`
6. `docs/00-meta/report-provenance-quarantine.md`

## What deliberately did not change

No source was added, no case was added, no verdict was upgraded, and no schema field was removed. That restraint is intentional: deleting or certifying before locator migration would create a new false-clean state.
