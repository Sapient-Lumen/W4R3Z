# Entitlement basis page — owner, seat provenance, and usage claim interface spec

## Purpose

The archive already had install-target and entitlement-expiry review language.
What it still lacked was one ordinary page for the simpler question:

> why does this seat believe it currently has these capabilities at all, and what ownership chain, shared-seat path, or usage claim makes that belief true?

Current official Resilio docs make this seam concrete.
They still distinguish Home, Family, Business, linked-owner inheritance, shared seats, personal non-commercial v3 use, and owner-stealing behavior when a Business key is re-applied elsewhere.
That is useful truth.
It should not remain support-lore.

## Core decision

AnonSync must expose one first-class **Entitlement basis** page for every seat whose capability posture depends on subscription, license, grant, household scope, owner inheritance, or usage claim.

The page exists to answer five things in one place:

1. what the current entitlement verdict is
2. which provenance path makes it true
3. who or what may revoke or narrow it
4. which usage claim and seat scope it assumes
5. what follow-up action is safest if the basis looks unstable

## Fixed page order

1. **Current entitlement verdict**
2. **Provenance chain**
3. **Usage and scope claims**
4. **Instability and override risks**
5. **Safe next actions**

### 1) Current entitlement verdict

Show:

- `entitlement_basis_page_id`
- seat in scope
- current `entitlement_verdict` (`self-owned`, `owner-inherited`, `shared-seat`, `family-scope`, `line-default`, `expired`, `revoked`, `conflicted`, `unknown`)
- strongest honest summary
- effective time or last refresh time

The operator must be able to answer:

> what exact entitlement posture do I currently have?

### 2) Provenance chain

Show the chain as reviewed facts, for example:

- direct license or subscription on this seat
- inheritance from linked owner seat
- externally shared seat from another identity
- family / household allowance
- line-default capability not dependent on separate Pro activation
- manual override or restored key application

The page must distinguish `current capability` from `why that capability is currently allowed`.

### 3) Usage and scope claims

Show:

- declared usage class
- allowed seat population
- identity scope
- host-role constraints
- whether the basis is personal-only, family-shared, or business-owner controlled

The operator must be able to answer:

> what real-world claim is this entitlement resting on?

### 4) Instability and override risks

Show the strongest current risks:

- owner can reclaim or overwrite seat allocation
- owner expiry propagates to shared seats
- key re-application elsewhere can replace owner status
- host-role mismatch narrows real capability despite visible key application
- mixed-version or mixed-family cohorts can destabilize effective control continuity

This section must answer:

> what could make this entitlement stop being true next?

### 5) Safe next actions

Actions may include:

- `Re-verify owner`
- `Re-apply local key`
- `Request seat re-share`
- `Correct usage claim`
- `Open capability availability`
- `Open Pro-function loss`

Each action must preview whether it changes entitlement basis or only re-describes it.

## Public object

### Entitlement basis page

Fields:

- `entitlement_basis_page_id`
- `seat_ref`
- `entitlement_verdict`
- `provenance_chain[]`
- `usage_claim`
- `scope_claim`
- `instability_risks[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. seat
2. entitlement verdict
3. provenance phrase
4. strongest instability risk
5. next safest action

Example:

```text
workstation-07     shared-seat     inherited from business owner seat     owner expiry will remove Pro functions     Re-verify owner
```

## Non-goals

This page does **not** replace install eligibility or full downgrade-event review.
It proves only **why the seat currently believes its capability floor is what it is**.
