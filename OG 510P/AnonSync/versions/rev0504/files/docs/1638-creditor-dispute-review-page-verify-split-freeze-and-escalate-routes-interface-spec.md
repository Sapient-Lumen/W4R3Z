# Creditor dispute review page — verify, split, freeze, and escalate routes

## Purpose

This page is the operator review for deciding what to do when a creditor claim feeding restoration is challenged, under-evidenced, or reopened.
It must answer:

> do we verify the claim, split undisputed core from contested residue, freeze release, allow only provisional relief, escalate for ruling, or reopen a case that was closed too early?

## Mandatory review inputs

- source creditor claim contract sheet
- source restoration waterfall and current active tier if present
- evidence packages and expiry horizons
- counterevidence or competing claimant assertions
- current probation and future-burst posture
- authority class allowed to rule, waive, absorb, or reopen

## Required review routes

### Route 1 — verify creditor fully

Allowed only when:

- attribution basis is strong enough for the creditor class
- no material counterevidence remains unresolved
- evidence freshness remains inside policy horizon
- resulting stronger sentence is explicitly renderable

### Route 2 — split verified core from contested residue

Default route when:

- part of the claim is clearly verified
- another part lacks sufficient actor attribution, amount certainty, or freshness
- the product can render separate consequences for the core and residue

This route must preserve:

- verified core that may enter ordinary restoration flow
- disputed residue that still blocks the stronger cleaner sentence
- the exact review needed to resolve the residue

### Route 3 — freeze clean release and keep probation active

Required when:

- any material named-harmed-creditor claim remains contested
- evidence aged out before adjudication completed
- counterevidence materially undermines an earlier verification
- a reopen request alleges that prior closure omitted a creditor

### Route 4 — allow provisional reserve-only or undisputed-core relief

Allowed only when:

- some creditor classes are verified now
- disputed residue is rendered explicitly
- the operator is not laundering contested claimant harm into full restoration
- future-burst posture remains appropriately tightened

### Route 5 — explicit absorber or typed waiver

Allowed only with:

- named authority
- named absorber of unresolved residue
- explicit weaker sentence that survives
- explicit consequence such as longer probation, permanent narrowed cap, or manual-only future bursts

### Route 6 — deny creditor claim as unverifiable

Allowed only when:

- evidence basis is materially insufficient
- no policy formula or structural proxy can support a narrower verified core
- the denial explains whether residue disappears, is carried by another absorber, or remains unresolved under policy

### Route 7 — reopen previously closed case

Required when:

- new material evidence appears
- prior evidence was misread or truncated
- an omitted creditor emerges before release finality is immutable
- previously provisional closure is no longer defensible

Reopen must be able to:

- re-freeze clean release
- re-open probation
- re-tighten future-burst posture
- reinsert creditor residue into the active waterfall tiering

## Required outputs

- chosen dispute verdict
- verified creditor set after review
- contested residue after review
- release freeze posture after review
- future-burst posture after review
- next evidence or ruling required
- strongest sentence still blocked

## Required comparisons

The page must keep these comparisons explicit:

- `creditor verified` vs `creditor plausible but contested`
- `undisputed core paid` vs `all harm repaired`
- `evidence expired` vs `claim disproved`
- `waived residue` vs `resolved residue`
- `administrative closure` vs `truthful release`

## Failure modes the page must prevent

- clearing a claimant just because the operator is tired of the dispute
- converting missing attribution into silent creditor deletion
- allowing a lower-friction verified reserve slice to erase named-neighbor contest
- reopening the case without preserving what changed and why
- treating waiver as evidence

## Stronger-sentence guard

The review may say `undisputed reserve core verified; named-neighbor residue remains contested under release freeze`.
It may not say `claimant cleanly restored` until contested residue is ruled, absorbed, or waived with an explicit weaker surviving sentence.
