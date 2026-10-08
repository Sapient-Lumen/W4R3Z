# 576 — Nuclear emergency preparedness: records-request templates, deadline clock, and reproducible hotpath builder

## Current state

Rev0369 keeps the BVPS branch on the operational path rather than adding another doctrine layer. The package still has no real Beaver Valley exercise evidence packet, so it still cannot reach a local readiness or unreadiness conclusion. The point of this revision is to make the next real-world step hard to miss: capture the June 12 preliminary-findings materials, dispatch targeted records requests, and import any response through the chain-of-custody intake path before adjudicating it.

Current honest state: **capture-ready / request-template-ready / deadline-clock-open / EOF-LER-watch-open / ANS-transition-gate-open / claim-frozen / no local readiness conclusion**.

## What changed

The records-request queue in rev0368 named likely custodians and artifacts. Rev0369 turns that queue into sendable templates, an absolute-date clock, a gap-to-request map, and a meeting-capture runbook. Every P0 blocker now routes to at least one request template and one proofcut class. The cube therefore has a direct path from blocker -> request -> artifact class -> intake metadata -> adjudication state.

The EOF power issue remains a P0 gate. Event Notification 58200 is treated as a trigger for a proof chain: event notice, restoral, root cause, repair work order, post-maintenance test, compensatory measures, exercise scope, and LER/no-LER/regulatory disposition. None of those stages may be inferred from the initial notification.

The alerting issue also remains a P0 gate. Siren decommissioning planning, official approval, current siren status, ANS demonstration results, EAS/WEA/IPAWS/ENS logs, route-alerting backup, AFN accessibility, and corrective-action retest are separated so that an approval letter cannot be misused as delivery proof.

## Audit/refactor

Rev0369 replaces the manually curated hotpath capsule pattern with a reproducible builder:

- `cube/bvps-hotpath-source-list-rev0369.csv` is the single source list.
- `tools/build_bvps_hotpath_artifacts_rev0369.py` rebuilds both `cube/datacube-rev0369-hotpath.sqlite` and `evidence-bags/bvps-hotpath-capsule-rev0369.zip`.
- `tools/validate_bvps_hotpath_artifacts_rev0369.py` verifies the capsule, SQLite manifest, hashes, and required current-risk tables.

This is a waste-control refactor, not a destructive cleanup. The historical matrices and mirrors remain in the full package, but the active work path now has a bounded, reproducible default.

## Hard gates

- **Request gate.** A records request draft is not evidence. It only creates a traceable acquisition path.
- **Deadline gate.** A clock or expected release date cannot be counted as a finding.
- **EOF proof-chain gate.** Restoral, root cause, repair, retest, exercise scope, and LER/no-LER disposition are separate admissibility items.
- **Alerting proof-chain gate.** ANS approval, siren state, alert delivery, EAS follow-on, route alerting, AFN accessibility, and CAP retest are separate admissibility items.
- **Hotpath builder gate.** Active work should use the reproducible rev0369 hotpath artifacts before scanning giant historical matrices.

## Primary artifacts

- `cube/nuclear-emergency-bvps-deadline-clock-rev0369.csv`
- `cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv`
- `cube/nuclear-emergency-bvps-meeting-capture-runbook-rev0369.csv`
- `cube/nuclear-emergency-bvps-gap-to-request-map-rev0369.csv`
- `cube/nuclear-emergency-bvps-eof-corrective-action-proofchain-rev0369.csv`
- `cube/nuclear-emergency-bvps-alerting-proofchain-rev0369.csv`
- `cube/bvps-hotpath-source-list-rev0369.csv`
- `tools/build_bvps_hotpath_artifacts_rev0369.py`

## Non-closure rule

This revision is allowed to say the cube is better prepared to request, capture, hash, and adjudicate evidence. It is not allowed to say Beaver Valley offsite readiness is adequate, inadequate, demonstrated, repaired, approved, or closed.
