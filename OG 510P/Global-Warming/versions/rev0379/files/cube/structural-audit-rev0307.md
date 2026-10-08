# Structural audit rev0307 — applicability normalization and emergency-preparedness substance

Revision: rev0307  
Created: 2026-06-04T02:56:41-04:00

## What changed materially

This revision attacks the riskiest open defect from rev0306: the universal nuclear gate crossproduct. The three large nuclear all-gate matrices are preserved for compatibility, but they are no longer the intended primary model. Rev0307 adds a normalized layer:

- `cube/nuclear-service-family-taxonomy-rev0307.csv`
- `cube/nuclear-service-floor-family-map-rev0307.csv`
- `cube/nuclear-gate-applicability-rule-rev0307.csv`
- `cube/nuclear-gate-applicability-summary-rev0307.csv`
- `cube/nuclear-gate-applicability-proof-summary-rev0307.csv`

The current crossproduct is 114,494 pairs per large matrix (437 nuclear service floors × 262 gates). The normalized rule layer estimates 84,842 generated applicable pairs and suppresses 29,652 non-default pairs unless explicitly routed or localized.

## Emergency-preparedness substance added

The revision also adds substance that is difficult to recover later if postponed:

- `cube/nuclear-emergency-planning-standard-crosswalk-rev0307.csv` — 16 operational planning-standard rows.
- `cube/nuclear-epz-operational-readiness-evidence-rev0307.csv` — 16 local EPZ evidence variables covering population, mobility, schools, healthcare/LTC, routes, alerts, shelter, KI, reception centers, responders, food/water and recovery records.
- `cube/nuclear-ki-anti-theater-guardrail-rev0307.csv` — hard rules preventing KI from substituting for evacuation, shelter, monitoring, decontamination, food/water controls, or medical readiness.
- `cube/nuclear-recovery-population-monitoring-claims-evidence-rev0307.csv` — recovery, monitoring, claims, cleanup, registry, mental-health and trust-repair evidence.
- `cube/nuclear-compound-disaster-emergency-loadcase-rev0307.csv` — 10 scenario injects for wildfire smoke, heat, flood, blackout, cyber/public-information confusion, hospital surge, ingestion-pathway crisis, winter storm, resource contention and reentry/claims trust failure.

## Audit/refactor performed

The audit/refactor artifacts added in this revision are:

- `cube/nuclear-crossproduct-refactor-audit-rev0307.csv`
- `cube/cube-risk-burnup-rev0307.csv`
- `cube/source-freshness-audit-rev0307.csv`
- `cube/cloudtainer-hygiene-audit-rev0307.csv`
- `cube/refactor-backlog-rev0307.csv`

The refactor backlog marks REF-001, REF-004, REF-006, REF-007, REF-008 and REF-010 as partially or template-layer closed in rev0307, and adds REF-011 through REF-013 for applicability validation, local evidence status and exercise outcomes.

## What still should change next

The next high-value move is not another doctrine packet. It is `nuclear-local-evidence-status.csv`: one row per project/site/jurisdiction/gate with owner, artifact, date, freshness, exercise result, deficiency, corrective action, maturity cap and counterevidence path. That would turn the template layer into local readiness evidence.

The second move is to regenerate the three 114,494-row crossproduct files as filtered generated views from `nuclear-gate-applicability-rule-rev0307.csv` and `nuclear-service-floor-family-map-rev0307.csv`, with a compatibility alias period.

## Known caution

The service-family classification is intentionally conservative and keyword-derived. It is good enough to stop the universal-default error and to locate evidence burden, but it is not a substitute for human review of edge cases. Generic floors are deliberately not allowed to inherit all specialist gates by default.
