# Cohort audit checklist (probe/monitor capture resistance)

**Track:** Shared (cross-cutting)


Use this to audit that probe/monitor cohorts are not biased or captured.

## Inputs
- Published ChallengeSchedule + quotas
- Probe cohort selection criteria and diversity metrics
- Recent measurement receipts

## Checks
- Verify challenges match the public randomness seed schedule.
- Verify cohort diversity across ASN/region/device classes.
- Verify monitors publish suppression reports on misses.

## Outputs
- Publish a CohortAuditReport and include it in the evidence bundle.
