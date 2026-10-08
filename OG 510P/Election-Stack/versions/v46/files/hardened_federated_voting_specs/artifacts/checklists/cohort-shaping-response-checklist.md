# Cohort Shaping Response Checklist

## Trigger conditions
- [ ] `CohortShapingAlert` severity HIGH/CRITICAL
- [ ] Credible allegation that evidence differs by ISP/region/language/device
- [ ] Persistent unreachability affecting a subset of vantages

## Immediate actions (0–30 minutes)
- [ ] Rotate cohorts (external + internal) and expand diversity constraints.
- [ ] Add control targets (unrelated high-availability endpoints) to distinguish general outages from selective suppression.
- [ ] Publish a signed public statement that includes:
  - checkpoint ID/hash
  - evidence bundle manifest hash
  - alert hash(es)

## Follow-up (30–120 minutes)
- [ ] Launch additional measurement types (HTTP content-hash fetch; DNS; OHTTP) from expanded cohorts.
- [ ] Cross-anchor evidence bundle hashes into independent logs (if configured).
- [ ] Re-run simulation to estimate detection probability under the observed partition severity and publish `SimulationReport`.

## Decision gates
- [ ] If suppression persists beyond MAAD thresholds, trigger failover policy (alternate submission channels / supervised override / paper-of-record).

