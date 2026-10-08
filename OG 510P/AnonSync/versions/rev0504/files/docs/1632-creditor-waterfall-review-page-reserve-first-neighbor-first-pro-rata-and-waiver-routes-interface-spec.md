# Creditor waterfall review page — reserve-first, neighbor-first, pro-rata, and waiver routes

## Purpose

This page is the operator review for choosing how a limited restoration budget is applied across several creditor tiers after burst debt has already been acknowledged.
It must answer:

> do we clear reserve first, named harmed neighbors first, split relief pro rata inside a tier, convert residue into a narrowed follow-on award, or grant a typed waiver with surviving probation?

## Mandatory review inputs

- source burst-debt object
- current waterfall contract sheet
- available restoration budget now
- creditor tiers and residue per tier
- claimant recurrence profile
- authority class allowed to reorder or waive
- strongest currently blocked sentence

## Required review routes

### Route 1 — full immediate clearance

Allowed only when:

- the full remaining residue across all required tiers can be cleared now
- reserve and named harmed claimants are all explicitly verified
- no probation residue remains except any separate recurrence rule already typed

### Route 2 — default tiered restoration

Default route when:

- restoration budget is limited
- no typed waiver exists
- protected reserve is still below floor or an earlier higher tier remains open

Default order must be:

1. protected reserve
2. explicitly harmed named claimants
3. broader promise-cohort or system-headroom creditors

### Route 3 — pro-rata distribution inside the active tier

Allowed only when:

- the current active tier contains several same-class creditors
- the product has a stable denominator for that tier
- the operator is not silently skipping a higher tier
- the per-creditor slice can be rendered explicitly

### Route 4 — manual severity ordering inside the active tier

Allowed only when:

- several same-tier creditors suffered materially different harm
- severity basis is explicit and reviewable
- the product can name which same-tier creditors remain open afterward

### Route 5 — convert residue into narrowed future entitlement

Allowed only when:

- the product is honestly admitting that some restoration will be delivered by tighter future caps or reserved follow-on relief rather than immediate repayment
- the absorbing creditor tier is explicit
- surviving probation and narrowed-future-burst posture are explicit

### Route 6 — typed waiver with surviving consequence

Allowed only with:

- named waiver authority
- explicit creditor or absorber that accepts the shortfall
- explicit weaker sentence that survives instead of clean restoration
- explicit consequence such as longer probation, manual-only bursts, tighter cap, or no renewal

### Route 7 — deny all new bursts and keep probation active

Required when:

- a higher-priority creditor tier remains open
- restoration slices are being missed
- the claimant requests another exception before the open tier is cleared
- the operator cannot honestly prove that the current waterfall is holding

## Required outputs

- chosen waterfall verdict
- active tier after review
- distribution method inside active tier
- residue still open after this step
- probation posture after this step
- next relief slice due
- strongest sentence still blocked

## Required comparisons

The page must keep these comparisons explicit:

- `reserve restored first` vs `named-neighbor relief first`
- `same-tier pro-rata` vs `silent drift by whoever happened to get throughput`
- `manual severity ordering` vs `unexplained favoritism`
- `carry-forward conversion` vs `debt forgotten`
- `waiver with probation` vs `clean restoration`

## Failure modes the page must prevent

- letting partial reserve repair masquerade as full claimant repair
- paying lower-tier creditors while a higher tier is still open without typed authority
- using available throughput order as implicit moral order
- waiving residue without naming who absorbed the loss
- lifting probation just because live usage is lower this hour

## Stronger-sentence guard

The review may say `default waterfall approved; named harmed claimants remain under tier-2 partial relief`.
It may not say `clean restoration approved` until all required tiers clear or a typed waiver explicitly defines the weaker surviving truth.