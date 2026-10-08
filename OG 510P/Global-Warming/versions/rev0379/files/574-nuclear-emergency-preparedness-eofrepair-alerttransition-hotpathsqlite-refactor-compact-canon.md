# 574 — Nuclear emergency preparedness: EOF repair proof, alert-transition watch, and hotpath SQLite refactor

Revision: **rev0367**  
Base: **rev0366**  
Status: P0 evidence-admissibility hardening plus one bounded audit/refactor. Public-context-only; no real-site readiness or unreadiness claim.

## Why this revision exists

Rev0366 made the proofcut board visible and elevated the March 2026 Beaver Valley EOF power-loss event. The next risk is more operational: the cube could still receive an official-looking meeting packet and miss the specific proof questions that determine whether emergency-response-facility power, degraded-facility compensatory measures, public alerting, access-and-functional-needs support, and communications were actually demonstrated or dispositioned.

Rev0367 therefore does three practical things:

1. It turns the EOF power-loss notice into an **admissibility matrix** for repair/root-cause, restoral, alternate-facility activation, communications, and corrective-action evidence.
2. It adds an **alert-transition watch** because public context now includes siren/EAS/ENS/IPAWS/route-alerting dependencies and a reported Beaver County siren-decommissioning planning track. This is not failure evidence and not success evidence; it is a must-capture item for the June 2026 exercise/evaluation packet.
3. It builds a **hotpath SQLite snapshot** of the current BVPS evidence-control tables so future sessions can query the live operational surface without repeatedly opening the giant historical matrices.

## P0 rule

No artifact is admissible as readiness evidence unless it has: artifact class, custodian/source, receipt time, jurisdiction/scope, hash, size, sensitivity/redaction state, linked request, and an explicit claim limit. Public notices, preparedness brochures, county plans, newsletters, reactor status pages, and fixture rows remain context or routing evidence only.

The March 2026 EOF power-loss event cannot be closed by inference. It needs dated repair/root-cause records, backup-generator restoration evidence, compensatory-measure drill/evaluation evidence, communications product evidence, and corrective-action disposition. Without those, the only honest statement is that the EOF power lane remains an open follow-up gate.

Alert-system public context cannot be converted into alert success. The admissible proof is activation/delivery/failure evidence, evaluated objective coverage, language/AFN accessibility evidence, backup-route-alerting disposition, and any transition/decommissioning approval or exercise treatment.

## Operational files

- `cube/nuclear-emergency-bvps-eof-repair-admissibility-matrix-rev0367.csv` — concrete follow-up proof questions for the EOF power event.
- `cube/nuclear-emergency-bvps-alert-transition-watchlist-rev0367.csv` — public-alert and warning-system transition watch items.
- `cube/nuclear-emergency-bvps-proofcut-admissibility-tests-rev0367.csv` — artifact-class admissibility tests before any evidence credit.
- `cube/nuclear-emergency-bvps-columbiana-plan-crosswalk-rev0367.csv` — public-plan-to-proofcut routing crosswalk, zero-credit for readiness closure.
- `cube/nuclear-emergency-bvps-real-evidence-hotpath-board-rev0367.csv` — compact active board merging proofcut status, EOF follow-up, and alert transition blockers.
- `cube/bvps-hotpath-sqlite-table-manifest-rev0367.csv` and `cube/datacube-rev0367-hotpath.sqlite` — compact current-risk query snapshot.
- `tools/run_nuclear_emergency_bvps_validator_sweep_rev0367.py` — bounded current-risk validator sweep.

## Refactor boundary

Rev0367 does not delete old matrices, prior SQLite mirrors, or historical field kits. It adds a small operational hotpath database and a manifest so current sessions can work from a strict, bounded surface. Large historical artifacts remain preserved but are not the default working set.

## Current state

The cube still has no real or lawfully anonymized June 2026 Beaver Valley evidence packet. Its honest state is: **capture-ready / chain-of-custody-ready / proofcut-board-ready / EOF-repair-gate-open / alert-transition-watch-open / claim-frozen / no local readiness conclusion**.
