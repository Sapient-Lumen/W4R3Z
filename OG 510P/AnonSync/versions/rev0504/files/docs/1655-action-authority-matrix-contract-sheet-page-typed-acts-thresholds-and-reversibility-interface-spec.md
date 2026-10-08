# Action authority matrix contract sheet page — typed acts, thresholds, and reversibility

## Purpose

This page is the canonical declaration of which actions exist in a case and what authority each one requires.
It exists so the product can stop pretending that one coalition verdict or one broad role label answers every stronger act.

The page must answer:

> for each action family in this case, who may do it, how many valid signers are required, how final it is, what residue it touches, and what later rights remain alive?

## Mandatory action families

At minimum the page must type these acts separately:

- acknowledge receipt
- accept provisional settlement
- accept capped settlement
- waive undisputed residue
- waive disputed residue
- lift probation
- restore future-burst eligibility
- delegate narrower authority
- appoint successor authority
- ratify predecessor act
- reopen on new evidence
- freeze execution pending review

The implementation may add more acts, but it may not collapse these into one generic `approve` row.

## Mandatory columns per action family

### A. Identity block

- action family name
- plain-language description
- affected creditor slice or scope
- whether the act is local, cross-creditor, or case-wide

### B. Authority block

- minimum signer class required
- minimum coalition threshold required
- whether a named seat must participate
- whether successor ratification is allowed
- whether delegation is allowed for this act
- whether adjudication may substitute for ordinary signatures

### C. Reversibility block

- reversibility class (`protective`, `revisable`, `irreversible`)
- whether execution is immediate or delayed
- required cooling window if any
- contest window after execution if any
- exact reopen condition after execution

### D. Consequence block

- strongest sentence this act can earn
- stronger sentence this act cannot earn
- whether open residue survives
- whether probation survives
- whether future-burst rights survive
- whether reopen rights survive

### E. Evidence block

- source contract or rule basis
- source coalition rule
- source representative rule if any
- source adjudication or waiver basis if any
- expiry or rereview horizon for this row

## Required comparisons

The page must keep these comparisons explicit:

- `acknowledge receipt` vs `accept settlement`
- `accept settlement` vs `waive residue`
- `lift probation` vs `restore future-burst eligibility`
- `appoint successor` vs `ratify predecessor act`
- `freeze pending review` vs `reopen after execution`
- `protective` vs `irreversible`

## Required badges

- `protective-only`
- `revisable-act`
- `irreversible-act`
- `cooling-window-required`
- `named-seat-required`
- `successor-ratification-allowed`
- `delegation-allowed`
- `delegation-forbidden`
- `adjudication-substitutable`
- `case-wide-consequence`

## Failure modes the page must prevent

- letting one coalition verdict silently apply to every action family
- treating payment receipt as if it automatically waived residue
- treating probation lift as if it automatically restored future-burst eligibility
- treating successor appointment as if it automatically ratified earlier acts
- forgetting that a narrow protective freeze may be valid when a stronger irreversible act is not

## Stronger-sentence guard

The page may say `two-seat coalition may acknowledge funds and freeze collection, but final residue waiver requires unanimity plus a 72-hour cooling window`.
It may not say `these signers can close the case` unless the exact closure action row says so.
