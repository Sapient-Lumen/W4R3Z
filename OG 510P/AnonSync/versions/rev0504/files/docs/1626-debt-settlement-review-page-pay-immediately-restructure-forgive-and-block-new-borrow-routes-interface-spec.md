# Debt settlement review page — pay immediately, restructure, forgive, and block new-borrow routes

## Purpose

This page is the operator review for deciding what to do with unpaid burst debt after an exception has ended, expired, or narrowed.
It must answer:

> do we require immediate restoration, permit staged settlement, convert debt into a narrower future award, grant typed forgiveness with consequence, or keep all new exceptions embargoed until the debt is retired?

## Review inputs

- burst borrow contract sheet
- burst borrow proof
- burst debt contract sheet
- current harmed-claimant condition
- reserve-restoration status
- claimant urgency for any follow-on request
- history of prior burst debt on the same claimant or authority chain
- policy ceiling for forgiveness, restructuring, and repeated exceptions

## Required decision routes

### Route 1 — immediate settlement and restoration

Allowed when:

- reserve and harmed-claimant relief can be completed now
- no further urgent exception is needed
- evidence is strong enough to verify restoration quickly

### Route 2 — staged settlement under active embargo

Allowed only when:

- immediate full restoration is not realistic
- creditor set and remaining balance are explicit
- a due schedule is concrete
- new burst borrow remains blocked or manual-review-only while debt is open

### Route 3 — convert open debt into narrowed future entitlement

Allowed only when:

- the product is honestly admitting that the prior burst exposed a recurring need rather than a one-off emergency
- the narrower successor award is explicit
- harmed claimants are not erased by the conversion
- the old debt object is closed by typed carry-forward rather than forgotten

### Route 4 — typed forgiveness with consequence

Allowed only with:

- named forgiving authority
- explicit reason why creditor restoration will not be completed in full
- explicit weaker follow-on sentence
- explicit consequence such as no-renewal, tighter cap, probation, or manual-only future bursts

### Route 5 — keep debt open and embargo all new burst requests

Required when:

- the claimant seeks another exception before retiring earlier debt
- reserve or harmed-claimant relief is still materially incomplete
- the same authority chain has shown normalization drift
- the operator cannot honestly prove restoration readiness yet

## Required outputs

- chosen settlement verdict
- remaining balance class
- creditor set
- embargo posture
- next review date
- restoration proof required next
- strongest sentence still blocked

## Required comparisons

The page must keep these comparisons explicit:

- `exception ended` vs `good standing restored`
- `staged settlement` vs `silent delay`
- `carry-forward into narrower award` vs `debt forgotten`
- `forgiveness with consequence` vs `clean restoration`
- `manual one-off approval` vs `policy-level reopen`

## Failure modes the page must prevent

- allowing repeated urgent exceptions to stack without a visible debt ladder
- calling a claimant `back to normal` because graphs look calmer
- forgiving debt without naming who absorbed the loss
- converting emergency borrowing into stealth baseline expansion
- letting a manually detached priority state silently reopen the same debt pattern

## Stronger-sentence guard

The review may say `debt settlement plan approved under embargo`.
It may not say `claimant fully restored` until restoration proof clears the gate or a typed forgiveness rule explicitly defines the weaker surviving sentence.