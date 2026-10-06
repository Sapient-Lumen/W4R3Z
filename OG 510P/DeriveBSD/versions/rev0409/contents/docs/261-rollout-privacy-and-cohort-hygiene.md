# Rollout privacy and cohort hygiene

Staged rollouts require cohorts, but cohorts can become a **tracking vector** if we’re sloppy.

DeriveBSD’s `rollout.policy` already models cohort assignment via deterministic hashing with a salt. This document adds explicit privacy constraints and operational hygiene.

## Lessons to steal (Omaha-shaped)

The Omaha protocol (used by Chromium updaters) models three cohort strings (`cohort`, `cohortname`, `cohorthint`) and explicitly allows the server to update cohort hints and names over time.

That flexibility is operationally useful, but it can also leak long-lived identifiers if the cohort space or hints are too specific.

## DeriveBSD design goals

1) **Bound cohort entropy**
   - policy should bound the number of cohorts and the “bits of uniqueness” a cohort assignment can encode.

2) **Prefer random stable IDs over hardware fingerprints**
   - default stable ID should be a locally generated random identifier (stored in state) rather than a hardware fingerprint.

3) **Salt rotation is normal**
   - allow rotation per release, per channel epoch, or on demand.
   - rotation should not silently fragment cohorts; it should be explicit in policy.

4) **Cohort hints are policy-scoped and receipted**
   - if `cohort_hint_allowed` is true, hints must be:
     - signed/receipted
     - length-bounded
     - free of direct identifiers

5) **Receipts avoid raw identifiers**
   - `rollout.receipt.device` should prefer hashes; never require raw device IDs.

## Schema impact

- `rollout.policy.cohorting` gains an optional `privacy` object:
  - `max_cohorts`
  - `min_bucket_size`
  - `entropy_budget_bits`
  - `salt_rotation` (epoch duration and rotation triggers)
  - `allow_hw_fingerprint` (explicit opt-in)

These fields do not make cohorting “perfectly private”, but they make privacy constraints **reviewable** and enforceable.

## Operational guidance

- Treat cohort salts as secrets when the stable ID is long-lived.
- Export policies should treat cohort identifiers as sensitive unless explicitly allowed.
- Transparency monitors can flag releases that unexpectedly change cohort privacy parameters.

## Related docs

- `docs/258-staged-rollouts-and-cohorts.md`
- `docs/195-deterministic-redaction-transforms.md`
- `docs/254-export-transparency-logs.md`
