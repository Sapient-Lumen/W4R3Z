
# Remedy-hardening-attestation policy-rollout review page — has this portable rule actually been deployed, enforced, and bounded by explicit exceptions?

## Purpose

This page is the operator-facing review that answers the practical rollout question after a rule has become portable: does the product know enough to treat that rule as actually governing a named estate slice, or is it still only a precedent waiting on deployment or exception cleanup?

## Primary review prompts

The review must answer these prompts in order:

1. **Is the source precedent itself portable enough to justify rollout review?**
2. **Which estate slice is being asked to adopt the rule now?**
3. **Through which concrete control lane is deployment supposed to happen?**
4. **Which populations remain uncovered, manually overridden, waived, or grandfathered?**
5. **What verification evidence proves effective enforcement rather than just intended defaults?**
6. **What is the strongest sentence the product may say right now?**

## Review sections

### 1. Precedent readiness board

Show:

- source precedent class
- unresolved counterexample or sunset risk
- why rollout review is allowed or blocked

### 2. Estate-slice map

Show:

- named populations in scope
- platform and surface families in scope
- explicit out-of-scope populations
- slices deferred to later rollout waves

### 3. Control-lane and drift board

Show:

- deployment mechanism family
- whether the intended control is default-only, enforced, or advisory
- manual override counts
- grandfathered populations
- drift or divergence already detected

### 4. Exception and waiver board

Show:

- active waivers and owners
- expiry dates and review dates
- exception debt versus budget
- whether broader rollout is blocked by current exceptions

### 5. Rollout sentence chooser

The review must output one and only one primary sentence class such as:

- precedent portable, rollout not started
- rollout proposed for named slice only
- deployment active, verification incomplete
- enforced for named slice with bounded waivers
- grandfathered population still outside policy
- exception debt above budget
- review overdue, rollout narrowed or paused
- policy retired or superseded

## Hard rules

The review must never let an operator hide:

- a portable rule behind `already policy`
- a config file behind `effective coverage`
- one platform rollout behind a whole-estate sentence
- a manual detour behind `automatic enforcement`
- waiver debt or grandfathered populations behind `everyone now follows the rule`
