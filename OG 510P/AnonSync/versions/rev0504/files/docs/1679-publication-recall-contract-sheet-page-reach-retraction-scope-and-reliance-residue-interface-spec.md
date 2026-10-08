# Publication-recall contract sheet page — reach, retraction scope, and reliance residue

## Purpose

This page is the canonical declaration of what exactly a later correction, withdrawal, or narrowing is trying to do to an already-published act.
It exists so the product can stop pretending that `access revoked`, `publication retracted`, and `old reliance extinguished` are the same truth.

The page must answer:

> for this already-issued publication, what is being corrected or withdrawn, which audiences must be reached, what residue is allowed to survive, and what stronger clawback sentence remains blocked?

## Mandatory recall classes

At minimum the page must expose these recall classes separately:

- clerical correction
- semantic correction
- narrowing of reliance only
- participant retraction
- external retraction
- public-summary withdrawal
- audit-only preservation
- destructive local delete request
- impossible full clawback

The implementation may add more classes, but it may not collapse them into one generic `recalled` state.

## Mandatory blocks

### A. Source-publication block

- source act identifier
- source publication version identifier
- original audience classes reached
- original reliance classes granted
- current supersession or dispute posture
- exact reason recall is being attempted

### B. Recall-target block

- named or class-based audiences to be reached now
- whether each audience previously received semantic content, metadata only, or encrypted custody only
- whether each audience must receive a correction, a withdrawal, a narrowing notice, or only an audit annotation
- whether any audience is unreachable, unknown, or only probabilistically reachable

### C. Recall-effect block

- future publication state after recall
- future reliance state after recall
- historical trace preservation class
- semantic residue allowed or unavoidable
- whether local copies, exports, screenshots, or prior mirrors may survive
- strongest sentence still blocked after recall

### D. Reach-proof block

- required delivery evidence per audience class
- acknowledgement requirement if any
- timeout or grace period if any
- what counts as partially reached
- what counts as unreached but attempted
- what exact sentence becomes honest at each reach rung

### E. Residue-and-audit block

- surviving audit visibility
- surviving adjudicator visibility
- participant-memory / prior-semantic-residue posture
- encrypted-host custody posture
- archive / history preservation posture
- exact reason the product refuses a stronger erasure claim

## Required comparisons

The page must keep these comparisons explicit:

- `future updates suspended` vs `already seen semantics extinguished`
- `correction issued` vs `correction reached`
- `publication withdrawn` vs `historic trace preserved`
- `viewer lost access` vs `viewer was actually corrected`
- `bytes removed locally` vs `reliance residue eliminated`

## Required badges

- `recall-proposed`
- `correction-issued`
- `reach-partial`
- `reach-complete`
- `future-flow-halted`
- `reliance-narrowed`
- `audit-residue-preserved`
- `semantic-residue-survives`
- `full-clawback-blocked`
- `erasure-claim-blocked`

## Failure modes the page must prevent

- treating access revocation as proof that earlier viewers no longer know the old claim
- treating any delivered correction as if all required audiences were reached
- treating local deletion or archive rollover as proof that semantic residue disappeared everywhere
- losing the distinction between a narrowed reliance instruction and a fully withdrawn claim
- forgetting that some historical trace may need to survive precisely because the recall itself is contested

## Stronger-sentence guard

The page may say `future participant reliance is narrowed and a correction has reached all named participants, while public-summary viewers remain only partially reached and audit trace stays preserved`.
It may not say `the old claim has been fully clawed back everywhere` unless the exact reach and residue rows support that stronger sentence.
