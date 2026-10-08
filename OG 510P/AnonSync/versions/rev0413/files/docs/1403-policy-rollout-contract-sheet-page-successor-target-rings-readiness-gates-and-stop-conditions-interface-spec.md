# Policy-rollout contract sheet page: successor target rings, readiness gates, and stop conditions interface spec

## Purpose

The archive already has pages for policy profiles, waivers, lifecycle, and supersession.
What it still lacked was one ordinary page for the narrower question:

> now that a successor policy exists, how exactly are we shipping it, to whom, in what stages, under which gates, with which stop conditions, and what is the strongest truthful sentence at this moment?

Current official Resilio docs make this seam concrete.
They separately describe mixed-major linked risk, Business/v3 incompatibility, installation-posture-specific update steps, service migrate-vs-clean-install branches, restart-required settings, platform-envelope splits, and subset-only feature availability.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Policy-rollout contract sheet** whenever a policy successor is intended to move across more than one subject, world, seat, or ring.

The sheet exists to answer nine things in one place:

1. which predecessor and successor revisions are in play
2. which subjects are targeted
3. which ring each subject currently belongs to
4. which readiness gates govern promotion
5. which stop conditions can freeze expansion
6. what rollback class applies
7. what outcome counts exist by ring
8. what feature sentence is safe at this stage
9. what stronger sentence remains blocked

## Fixed page order

1. **Rollout header**
2. **Target and ring card**
3. **Readiness-gate card**
4. **Stop-condition card**
5. **Rollback class card**
6. **Blocked stronger sentence**

### 1) Rollout header

Show at minimum:

- `policy_rollout_id`
- predecessor revision
- successor revision
- policy family id
- strongest safe sentence
- blocked stronger sentence
- rollout state
- last evaluated time

Supported headline states must include:

- `planned`
- `canary-live`
- `pilot-live`
- `broad-live`
- `frozen`
- `rolling-back`
- `completed`
- `unknown`

Example safe sentence:

- `Successor policy is active only in canary and pilot rings; broader rollout remains blocked by one Business-held v2 lane and one restart-required service cohort.`

### 2) Target and ring card

Show explicit rows for at least:

- total targeted subjects
- canary subjects
- pilot subjects
- broad subjects
- holdback subjects
- frozen subjects
- rollback subjects
- not-yet-classified subjects

Each row must show:

- subject count
- representative members
- governing blockers if any
- current stage result

The operator must be able to answer:

> who exactly is already on the successor, who is merely planned, and who is intentionally held back?

### 3) Readiness-gate card

Separate these gate classes explicitly:

- `version_floor_gate`
- `platform_lane_gate`
- `waiver_gate`
- `restart_or_cold_apply_gate`
- `world_continuity_gate`
- `feature_claim_gate`
- `evidence_freshness_gate`
- `unknown_gate`

Every gate row must show:

- verdict (`pass`, `partial`, `fail`, `unknown`)
- governing subjects
- why the gate exists
- what stronger sentence it blocks

The operator must be able to answer:

> what exactly must be true before the next ring is allowed to move?

### 4) Stop-condition card

Supported stop classes must include:

- `new-governing-blocker`
- `mixed-major-linked-risk`
- `waiver-expired`
- `cold-apply-not-completed`
- `storage-world-fork-detected`
- `subset-claim-only`
- `unknown-regression`

Each stop row must show:

- whether armed now
- trigger evidence
- affected rings
- automatic consequence (`freeze`, `rollback`, `holdback-only`, `manual-review`)

The operator must be able to answer:

> what would automatically stop broadening this rollout right now?

### 5) Rollback class card

Separate rollback truth explicitly:

- `hot-revert`
- `restart-bound-revert`
- `rebind-required`
- `reinstall-preserving-data`
- `config-discontinuous-revert`
- `no-safe-rollback`
- `unknown`

Each row must show:

- applicable rings
- data continuity class
- config continuity class
- whether subject bindings survive
- whether waivers must be reopened

The operator must be able to answer:

> if we stop, what kind of rollback do we actually have?

### 6) Blocked stronger sentence

Examples:

- `Successor policy is safe cohort-wide` blocked because one linked family remains mixed-major.
- `Promotion is continuity-preserving for all subjects` blocked because one service branch requires clean install.
- `This feature is now broadly available` blocked because availability remains subset-only by version/entitlement.

## Hard rules

- rollout state must never be inferred from policy publication alone
- ring counts must never collapse into one optimistic `rolled out` badge
- canary success must never overclaim broad readiness
- stop conditions must be printable before they trigger, not reconstructed afterward
- rollback class must be chosen before promotion, not invented after failure
