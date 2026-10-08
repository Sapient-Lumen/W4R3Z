# Public inspection — randomness & quota checklist

**Track:** Shared (cross-cutting)


## Before the election
- Publish `ChallengeQuotaPolicy` (caps for watchers, monitors, targets).
- Publish `ChallengeSchedule` for at least the critical election phases.
- Pin both into the EPB (parameter transparency).

## During the election
- For each round:
  - Fetch the public seed (e.g., NIST beacon pulse) and record the locator.
  - Generate deterministic target list with `challenge_sampler.py`.
  - Publish `PublicInspectionChallenge` objects for all sampled targets.
  - Enforce response deadlines; publish `InspectionSuppressionReport` if missed.

## After the election
- Publish `InspectionCoverageReport` and a summary of missed deadlines and suppression incidents.
