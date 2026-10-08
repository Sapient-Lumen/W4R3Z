# Version interlock review page: linked-family mixed-major risk and upgrade boundary interface spec

## Purpose

This page exists for the moment when bytes may still flow but administration truth has already degraded.
It is the focused review for mixed-major cohorts, especially identity-linked families where one optimistic `compatible` label would be dangerously incomplete.

## Core decision

AnonSync must treat **mixed-major interlock** as first-class review state whenever any of the following are true:

- a linked family contains more than one major version
- byte exchange remains possible but license or configuration safety degrades
- one upgrade path is forbidden because a member is Business/NAS constrained
- one feature claim depends on collapsing several members to the same major first

## Review layout

1. **Interlock summary rail**
2. **Member matrix**
3. **Risk translation card**
4. **Upgrade-boundary decision card**
5. **Receipts and next actions**

### 1) Interlock summary rail

Show:

- `mixed_major_present`
- `linked_family_present`
- `byte_exchange_survives`
- `admin_safety_degraded`
- `license_conflict_risk_present`
- `upgrade_boundary_kind`

Supported summary states:

- `safe-same-major`
- `mixed-major-unlinked`
- `mixed-major-linked-risk`
- `migration-blocked-by-lane`
- `migration-blocked-by-platform`
- `unknown`

### 2) Member matrix

Each member row must show:

- member ref
- current major version
- linked-family membership
- product lane (`personal`, `business`, `unknown`)
- platform class
- target-lane eligibility
- governing blocker

The operator must be able to answer:

> which exact member is setting the risk floor?

### 3) Risk translation card

Translate mixed-version facts into operator language:

- `bytes still sync`
- `admin state may conflict`
- `license application may conflict`
- `shares configuration access may be lost`
- `stored data remains intact`
- `migration requires cohort split first`

This card exists because the technical fact and the operator consequence are different truths.

### 4) Upgrade-boundary decision card

Supported verdicts must include:

- `upgrade-together-now`
- `hold-current-until-linked-family-is-split`
- `never-upgrade-this-member-to-target-lane`
- `replace-member-before-upgrade`
- `safe-byte-compatibility-only`

Each verdict must show:

- why it is safe
- what stronger sentence it blocks
- who must move first
- whether reinstall or reconfiguration is required

### 5) Receipts and next actions

Allowed actions:

- `Create migration tranche`
- `Split linked family`
- `Freeze feature rollout`
- `Export interlock receipt`

## Hard rules

- a mixed-major linked family must always escalate to review; it cannot stay a silent badge
- `compatible` must never be shown alone when admin-safety truth is worse
- data-preservation reassurance must never be used to hide UI/configuration risk
- business-held members must be named explicitly, not implied as generic laggards
