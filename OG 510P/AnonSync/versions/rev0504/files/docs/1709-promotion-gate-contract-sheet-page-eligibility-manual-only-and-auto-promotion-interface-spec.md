# Promotion-gate contract sheet page — eligibility, manual-only review, and auto-promotion

## Purpose

This page is the canonical declaration of whether a stronger sentence may go live.
It exists so the product can stop pretending that `stable`, `quiet`, `warning-free`, `reviewable`, `manually approvable`, and `safe to auto-promote` are the same truth.

The page must answer:

> given the already-earned lower sentence, what stronger sentence is now under consideration, what prerequisites are satisfied, what lane is authorized, who may decide, may automation act, what override debt would exist, and what event would demote the result again?

## Mandatory promotion rungs

At minimum the page must expose these rungs separately:

- not promotion-eligible
- eligible for review only
- blocked by missing proof
- blocked by missing authority
- blocked by unresolved warning or residue
- manual-review ready
- auto-promotion eligible but not yet armed
- auto-promotion armed
- promoted manually
- promoted automatically
- override-promoted
- override-denied
- demoted after promotion
- re-armed after renewed proof

The implementation may add more rungs, but it may not collapse them into one generic `approved` state.

## Mandatory blocks

### A. Source-bundle block

- case identifier
- source lower-sentence receipt identifier
- source stability proof identifier
- source authority and time-authority receipt identifiers
- exact stronger sentence under consideration
- exact reason a promotion sheet is required instead of immediate speech or automation

### B. Gate-rule block

- exact rule version governing this stronger sentence
- mandatory prerequisites for this sentence
- prerequisites already satisfied
- prerequisites still missing
- whether the sentence is manual-only, auto-eligible, or override-only
- confidence floor for auto-promotion, if any
- strongest blocked sentence above the one currently under review

### C. Decision-authority block

- who may manually promote
- who may deny promotion
- who may request override
- who may grant override
- whether linked identity, owner status, or generic operator role are insufficient without named decision authority
- whether the decision must be unanimous, quorum-based, or single-seat for this row

### D. Override-and-debt block

- whether override is allowed at all
- override reason taxonomy
- maximum duration before re-review
- debt, probation, or residue created by override
- which stronger irreversible acts remain blocked even after override promotion
- exact event that cancels the override

### E. Demotion-and-reopen block

- events that demote the promotion
- events that merely annotate but do not demote
- whether new warnings freeze automation immediately
- whether later policy changes apply retroactively
- what evidence is preserved when the gate re-closes

## Required comparisons

The page must keep these comparisons explicit:

- stable-earned versus promotion-authorized
- review-ready versus manual promotion complete
- auto-eligible versus auto-armed
- ordinary promotion versus override promotion
- promoted versus still blocked from stronger irreversible follow-ons
- demoted versus fully erased from history

## Required microcopy

The page must always show, in plain language:

- the smallest honest sentence already earned
- the next stronger sentence being considered
- whether a human must decide
- whether automation may act
- what still blocks promotion
- what would demote the sentence after promotion

## Forbidden shortcuts

This page must not allow promotion from any single shortcut such as:

- green check alone
- warning absence alone
- stability-earned alone
- notification arrival alone
- manual confidence alone without preserved reason
- one previous similar case auto-promoting successfully

Those are inputs.
They are not the promotion verdict.
