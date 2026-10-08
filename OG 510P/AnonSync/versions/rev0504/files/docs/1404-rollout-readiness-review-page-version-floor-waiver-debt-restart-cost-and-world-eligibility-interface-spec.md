# Rollout-readiness review page: version floor, waiver debt, restart cost, and world eligibility interface spec

## Purpose

This page exists for the moment when a successor policy is plausible but not yet safely promotable.
It is the focused review for answering:

> are we actually ready to move the next ring, or are we still confusing desire, byte compatibility, and subset success with genuine rollout readiness?

## Core decision

AnonSync must treat **rollout readiness** as first-class review state whenever any of the following are true:

- the target cohort spans more than one version floor or platform lane
- any subject carries active waivers relevant to the successor
- any activation path requires restart, rebind, or clean install
- some feature claims are subset-safe but not cohort-safe
- one wider ring depends on evidence from a narrower ring

## Review layout

1. **Readiness summary rail**
2. **Gate matrix**
3. **Eligibility partition card**
4. **Promotion verdict card**
5. **Receipts and next actions**

### 1) Readiness summary rail

Show:

- `successor_revision`
- `next_ring`
- `readiness_verdict`
- `gates_passed_count`
- `gates_failed_count`
- `gates_unknown_count`
- `stop_conditions_armed_count`
- `current strongest safe sentence`

Supported summary states:

- `ready-for-promotion`
- `ready-only-for-narrower-ring`
- `blocked-by-version-floor`
- `blocked-by-platform-or-product-lane`
- `blocked-by-waiver-debt`
- `blocked-by-cold-apply`
- `blocked-by-world-fork-risk`
- `unknown`

### 2) Gate matrix

Each gate row must show:

- gate class
- governing subjects
- evidence freshness
- why it matters
- pass/partial/fail/unknown verdict
- what the operator must do next

Required gate families:

- version floor
- platform/product lane
- waiver debt
- restart / cold-apply debt
- storage-world eligibility
- feature-claim safety
- rollback availability

The operator must be able to answer:

> what exact facts are holding back promotion, and are they temporary, structural, or merely unknown?

### 3) Eligibility partition card

This card must partition the target population into explicit buckets:

- `promotable-now`
- `promotable-only-with-restart`
- `promotable-only-with-rebind`
- `holdback-required`
- `waiver-renewal-required`
- `unsupported-for-this-successor`
- `unknown-before-more-evidence`

Each bucket row must show:

- subject count
- representative blockers
- whether movement preserves continuity
- whether movement changes world scope

### 4) Promotion verdict card

Supported verdicts must include:

- `promote-next-ring-now`
- `promote-only-canary`
- `freeze-and-remediate`
- `split-rollout-by-world`
- `renew-waivers-before-moving`
- `stop-this-successor-for-these-subjects`

Each verdict must show:

- why it is safe
- what stronger sentence it blocks
- who moves next
- what evidence must be collected after movement

### 5) Receipts and next actions

Allowed actions:

- `Promote ring`
- `Freeze rollout`
- `Create holdback cohort`
- `Open waiver renewal review`
- `Export readiness receipt`

## Hard rules

- byte compatibility may never satisfy rollout readiness by itself
- an active waiver must be named explicitly if it affects the successor
- restart debt and world-fork risk must never be hidden inside one generic `manual step`
- `ready for some` must never masquerade as `ready for broad`
- unknown evidence must degrade readiness, not disappear
