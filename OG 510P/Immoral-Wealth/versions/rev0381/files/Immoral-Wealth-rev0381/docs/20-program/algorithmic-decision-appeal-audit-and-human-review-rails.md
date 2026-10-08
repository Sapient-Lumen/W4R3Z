---
status: active_bridge
claim_kind: program_protocol
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Algorithmic decision, appeal, audit, and human-review rails

Use this rail for consequential automated or semi-automated decisions in benefits, employment, housing, credit, insurance, public services, fraud detection, and identity verification.[S288][S295][S296][S297][S298][S299][S300]

## Minimum rail

1. **Inventory:** agency or regulator knows which algorithm, vendor, data sources, and decision points are in use.
2. **Notice:** the affected person is told that a model, score, or automated rule materially contributed.
3. **Reason:** the person receives specific reasons and data sources, not generic model language.
4. **Pre-deprivation review:** when loss is severe, human review occurs before denial, termination, account closure, or benefit stop.
5. **Emergency continuation:** subsistence, health, housing, and utility claims continue when error would create irreversible harm.
6. **Appeal:** appeal is accessible by phone, in person, language support, disability accommodation, and paper/offline routes.
7. **Audit:** agency/regulator tests false positives, false negatives, disparate impact, model drift, data quality, vendor updates, and override behavior.
8. **Vendor accountability:** contracts permit inspection, logging, documentation, correction, and public-interest disclosure.
9. **Sunset:** models expire unless recertified under observed outcomes.

## Hard fail

Gate 17 fails when a consequential decision is effectively automated but the claimant cannot see the reason, contest the data, reach a human, preserve the claim, or get correction before losing the threshold moment.
