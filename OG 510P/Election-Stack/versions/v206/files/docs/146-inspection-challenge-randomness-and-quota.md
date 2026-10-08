# 146 — Public inspection: challenge randomness, quotas, and anti-grinding

**Track:** A (Deployable core)


This document strengthens the **Public Inspection** mechanism (see `140-public-inspection-for-monitors.md`) against two adversary strategies:

1. **Challenge grinding**: a malicious watcher issues *selectively chosen* challenges that are easy for a colluding monitor to answer, while claiming broad coverage.
2. **Selective suppression**: a malicious or compromised monitor answers only a “friendly” subset of challenges and delays/ignores others, while presenting plausible excuses.

The goal is to make inspection **(a)** representative, **(b)** time-bounded, and **(c)** reproducible by independent parties.

## Design requirements

- **Unpredictable but verifiable sampling**: challenge targets must be sampled from a publicly committed seed.
- **Quota fairness**: each watcher has a bounded impact on monitor load; each monitor has bounded discretion to ignore or delay.
- **Coverage SLOs**: the ecosystem must meet minimum coverage across targets, time, and perspectives (see `148-challenge-selection-and-coverage-metrics.md`).
- **Time-bounded accountability**: unanswered challenges become *signed incidents* after the deadline (align with MMD-style deadlines in `145-mmd-style-deadlines-for-evidence-publication.md`).

## Seeded challenge selection (anti-grinding)

Each `ChallengeRound` uses:

- `seed_source`: one of:
  - NIST public randomness pulse (preferred)
  - witness-quorum checkpoint hash (fallback)
  - SCITT receipt hash (optional external anchor)
- `seed_value`: the selected seed bytes
- `round_id`: monotonically increasing identifier

Watchers MUST use deterministic target sampling from `(seed_value, round_id, watcher_id)` and publish:

- `ChallengeSchedule` (planned rounds, quotas)
- `ChallengeQuotaPolicy` (caps and fairness rules)

### Recommended seed: public randomness beacons

Public randomness helps ensure no watcher can precompute “easy” challenge sets. The NIST randomness beacon project explicitly targets public verifiability for randomized procedures (e.g., audit sampling). See `schemas/ChallengeSchedule.json`.

## Quotas and fairness constraints

- **Watcher quota**: maximum challenges per round and per day.
- **Target quota**: maximum challenges per target tuple (e.g., domain/endpoint/monitor API key) per period.
- **Monitor load cap**: maximum total challenge work the ecosystem may impose on a monitor per period, with proportional allocation.

Quotas reduce the risk that a malicious watcher can DoS monitors *or* shape the challenge distribution.

## Deadlines and escalation

Each `PublicInspectionChallenge` includes:
- a `window` (start/end)
- a `response_deadline` (derived from policy)

If a monitor does not provide a `PublicInspectionResponse` by the deadline:
- the watcher MUST publish an `InspectionSuppressionReport`
- witnesses SHOULD countersign the report (where applicable)
- the report is anchored into the evidence log(s)

## Security notes

- This mechanism does **not** create “ground truth”; it creates *detectable inconsistency* and *coverage evidence*.
- Watcher diversity is mandatory: at least N independent watchers must issue challenges using independent infrastructure.