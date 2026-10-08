# 149 — Challenge randomness and inspection auditability

**Track:** A (Deployable core)


This doc ties together:

- deterministic challenge sampling
- public randomness
- auditability of watcher behavior

## Why “randomness” matters

Without a public seed, a watcher can:
- cherry-pick “easy” targets for a colluding monitor
- avoid targets likely to reveal misconfiguration
- inflate “coverage” using redundant targets

## Audit model

Anyone can recompute a watcher’s expected challenge set for a given round:

Inputs:
- `seed_source` + `seed_value`
- `round_id`
- `watcher_id`
- `ChallengeQuotaPolicy`
- allowlist/denylist (published)

Outputs:
- deterministic list of targets and nonces

The watcher must publish:
- `PublicInspectionChallenge` objects matching the derived set
- a signed `MonitorAttestation` summarizing work performed
- coverage reports (doc 148)

Any deviation is a signed, provable inconsistency.

## Recommended public seed sources

- NIST randomness beacon pulse (preferred for independence)
- witness-quorum checkpoint hash (good, but may be influenced by insiders if not diversified)
- SCITT transparency receipt hash (optional external anchor)
