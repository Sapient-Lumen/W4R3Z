# 575 — Nuclear emergency preparedness: siren-transition approval gate, EOF LER watch, and records-request queue

## Current state

Rev0368 makes the active BVPS branch stricter and more practical. It does not add a local readiness conclusion. It narrows the work to two blocking operational risks and one acquisition path:

1. the alert/notification transition risk created by public siren-decommissioning planning while public plans still describe sirens as the primary warning channel;
2. the March 2026 EOF power-loss follow-up, including possible 10 CFR 50.73/ADAMS/inspection/corrective-action traces;
3. a public-records request queue for the exact artifacts that would turn the cube from capture-ready into candidate-evidence-ready.

Current honest state: **capture-ready / records-request-ready / ANS-transition-gate-open / EOF-LER-watch-open / claim-frozen / no local readiness conclusion**.

## What changed

The prior revision had a watchlist for sirens, EAS, ENS/IPAWS/WEA, AFN, and EOC/EOF/JIC issues. Rev0368 converts that watchlist into an admissibility gate. No alert-success statement may be made unless the package has official transition approval or current-system status, evaluated ANS demonstration evidence, delivery/failure logs, message scope, backup route-alerting evidence, and accessibility/AFN handling artifacts.

The EOF issue is also kept open. The NRC event notification is a trigger, not a completed finding. Rev0368 therefore tracks root cause, restoral, generator retest, compensatory measure activation, exercise scope, reportability/disposition, and ADAMS/NRC inspection follow-up as separate evidence needs.

A new records-request queue names the most useful next artifacts by likely custodian. This is deliberately more useful than another doctrine layer: it tells the next operator what to request, from whom, why it matters, and what claim remains frozen until it is received and hashed.

## Hard gates

- **ANS / siren transition gate.** Planning to decommission sirens is not approval; approval is not delivery proof; delivery proof is not whole-exercise readiness proof.
- **EOF recovery gate.** Compensatory measures and later restoral cannot be assumed from the initial notification. Root-cause, repair, retest, recurrence-control, and exercise-scope evidence remain required.
- **Preliminary findings gate.** A public meeting notice is only a clock. Preliminary findings, AAR/IP, ANS demonstration disposition, and open-deficiency status remain evidence needs.
- **Source boundary gate.** Public plans, brochures, local news, and newsletters route questions; they do not close performance claims.
- **Hotpath gate.** Work from the rev0368 hotpath SQLite or the internal hotpath capsule before scanning giant historical matrices.

## Primary artifacts

- `cube/nuclear-emergency-bvps-ans-transition-admissibility-matrix-rev0368.csv`
- `cube/nuclear-emergency-bvps-eof-ler-adams-watch-rev0368.csv`
- `cube/nuclear-emergency-bvps-public-meeting-evidence-packout-rev0368.csv`
- `cube/nuclear-emergency-bvps-public-records-request-queue-rev0368.csv`
- `cube/nuclear-emergency-bvps-closure-blocker-board-rev0368.csv`
- `cube/datacube-rev0368-hotpath.sqlite`
- `evidence-bags/bvps-hotpath-capsule-rev0368.zip`

## Non-closure rule

This revision is allowed to say the cube is better prepared to receive and test evidence. It is not allowed to say Beaver Valley offsite readiness is adequate, inadequate, demonstrated, repaired, approved, or closed. Those are still candidate conclusions that require real or lawfully anonymized evidence packets.
