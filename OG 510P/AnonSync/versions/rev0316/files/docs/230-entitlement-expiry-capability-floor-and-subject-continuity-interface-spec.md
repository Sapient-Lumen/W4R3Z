# Entitlement expiry, capability floor, and subject continuity interface spec

## Purpose

The archive already had capability-owner transfer and cohort-compatibility language.
What it still lacked was one explicit contract for the moment a seat or installation crosses an entitlement boundary:

> what exactly stops working, what still exists, what degrades into read-only or inert state, and what subject continuity is preserved when trial or license posture changes?

Current Resilio docs still make this seam concrete.
Their Business trial/license page still says expiry removes access to Pro features for the owner and any shared seats, and local-share docs still say local shares stop working when the trial/license expires or the license is removed.
Selective Sync docs also still preserve a visible feature-availability split between v2 licensed builds and v3.

That means entitlement is still not just a billing fact.
It is an operational boundary with subject fallout.

## Core decision

AnonSync must treat entitlement change as a reviewed **capability-floor transition**, not as a silent feature cliff.

Every entitlement loss, downgrade, expiry, grace-period end, or seat reassignment that affects runtime behavior must produce one review that answers:

- which capabilities are about to narrow or disappear
- which live subjects depend on them
- which bytes and receipts survive intact
- whether continuity degrades, blocks, or requires migration

## Why this matters

Current Resilio behavior still leaves too much meaning scattered across separate pages:

- a shared seat can lose Pro access when the owner's entitlement expires
- a local derivative share can simply cease syncing when entitlement goes away
- some features are described through version/edition availability notes rather than one runtime continuity page

AnonSync should instead hold one stronger rule:

> entitlement affects capability posture, never invisibly rewrites subject history.

## Fixed review order

Every entitlement-cliff event should render the same sections in the same order:

1. **Entitlement change**
2. **Affected capabilities**
3. **Subject continuity impact**
4. **Admissible follow-up actions**
5. **Continuity receipt**

### 1) Entitlement change

Show:

- current entitlement family and expiry/grace posture
- incoming entitlement family or absence of entitlement
- reason (`expiry`, `seat moved`, `trial ended`, `billing failure`, `manual removal`, `downgrade`)
- effective time

### 2) Affected capabilities

Show capability classes, for example:

- local derivatives / local replication
- advanced governance actions
- selective-materialization features
- automation or policy surfaces
- support/export depth

Each capability must be classified as:

- `unchanged`
- `degraded`
- `blocked for new use`
- `blocked for existing subjects`
- `migration required`

### 3) Subject continuity impact

Show:

- active subjects depending on the affected capabilities
- whether current bytes remain usable
- whether replication stops, freezes, or narrows
- whether derived/local-only children are suspended or detached
- whether recovery/export remains possible

The operator must be able to answer:

> what keeps working, what becomes inert, and what I must migrate before the cliff arrives?

### 4) Admissible follow-up actions

Good actions include:

- `Renew / restore entitlement`
- `Migrate dependent subjects`
- `Freeze with evidence`
- `Detach local derivative safely`
- `Accept degraded capability floor`
- `Export continuity receipt`

### 5) Continuity receipt

The receipt must preserve:

- entitlement before/after
- capability classes narrowed
- affected subjects
- bytes preserved vs. live behavior lost
- migrations completed or still pending

## Main surface

The runtime should expose one **Capability floor** page per seat and one **Entitlement event** review whenever the floor changes materially.

A good summary row reads like:

- `Local derivative sync will stop in 3 days unless entitlement is renewed.`
- `Governance/edit surfaces narrow, but subject bytes and receipts remain intact.`
- `This downgrade blocks new high-governance subjects but does not rewrite existing history.`

## Object model implications

### Entitlement event review

Fields:

- `entitlement_event_review_id`
- `seat_ref`
- `entitlement_before`
- `entitlement_after`
- `reason`
- `effective_at`
- `affected_capability_classes[]`
- `affected_subject_refs[]`
- `recommended_actions[]`

### Capability floor state

Fields:

- `capability_floor_state_id`
- `seat_ref`
- `entitlement_ref`
- `capability_classes[]`
- `blocked_new_actions[]`
- `degraded_existing_actions[]`
- `last_computed_at`

### Entitlement continuity receipt

Fields:

- `entitlement_continuity_receipt_id`
- `review_ref`
- `seat_ref`
- `preserved_subject_refs[]`
- `degraded_subject_refs[]`
- `migrated_subject_refs[]`
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- let entitlement expiry silently disable live workflows without an explicit continuity page
- blur `cannot create new` together with `existing subject stopped syncing`
- hide dependent local derivatives behind feature-marketing language
- imply byte loss when the real loss is only active capability

## Relationship to nearby specs

This spec is the entitlement-focused companion to:

- `204-release-cohort-compatibility-control-plane-migration-and-link-gate-interface-spec.md`
- `223-capability-owner-transfer-and-seat-starvation-boundary-interface-spec.md`
- `205-constrained-seat-path-consent-and-removable-storage-capability-interface-spec.md`
- `211-ingress-verb-taxonomy-and-mobile-source-capture-interface-spec.md`

Those documents already cover seat movement and capability family boundaries.
This one fixes the operator-facing continuity contract when entitlement narrows.
