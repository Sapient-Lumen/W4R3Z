# Acknowledgment contract sheet page — notice, open, acknowledgment, and assent scope

## Purpose

This page is the canonical declaration of what kind of recipient action a typed act actually requires.
It exists so the product can stop pretending that `notification sent`, `notification visible`, `approval clicked`, and `binding assent` are the same truth.

The page must answer:

> for this act version, who must merely be notified, who must open it, who must acknowledge it, who must assent to it, and in what named capacity does each of those steps count?

## Mandatory recipient-action classes

At minimum the page must expose these classes separately:

- notification only
- open required
- acknowledgment required
- assent required
- countersigned assent required
- fresh re-assent required
- remembered-trust allowed
- identity-level substitute allowed
- device-level substitute forbidden
- adjudicator acknowledgment only

The implementation may add more classes, but it may not collapse them into one generic `approved` state.

## Mandatory blocks

### A. Act-and-version block

- source act identifier
- source version identifier
- publication / correction / recall class in force
- exact recipient-action class required for this version
- exact reason this action level is required

### B. Recipient-and-capacity block

- named recipient or audience class
- whether the intended actor is a person, delegated representative, linked identity, device custodian, or adjudicator
- whether owner status is relevant
- whether the exact typed act allows substitution by identity, device, or representative
- strongest blocked stronger sentence if actor identity remains under-proved

### C. Evidence-threshold block

- what counts as notification delivered
- what counts as open proof
- what counts as acknowledgment
- what counts as assent
- what counts as fresh re-assent
- what remembered approval or certificate memory may and may not substitute for

### D. Assent-effect block

- which typed effects unlock at each rung
- what remains blocked after mere delivery
- what remains blocked after opening only
- what remains blocked after acknowledgment only
- what remains blocked until assent or countersign happens
- whether cooling, notice, or recall rules restart after re-assent

### E. Dispute-and-revocation block

- how stale, ambiguous, or device-only action is challenged
- how actor-capacity disputes are opened
- how assent is revoked, superseded, or narrowed later
- what happens if a linked-device action is later denied by the human principal
- exact reason the product refuses a stronger consent sentence

## Required comparisons

The page must keep these comparisons explicit:

- `notification visible` vs `message opened`
- `message opened` vs `acknowledged understanding`
- `acknowledged understanding` vs `binding assent`
- `identity action` vs `named-person assent`
- `remembered approval` vs `fresh assent to this version`

## Required badges

- `notification-pending`
- `notification-delivered`
- `opened`
- `acknowledged`
- `assented`
- `fresh-reassent-required`
- `identity-substitute-used`
- `device-substitute-blocked`
- `capacity-unproven`
- `binding-consent-blocked`

## Failure modes the page must prevent

- treating synchronized notifications as proof that a person read the material
- treating any-device approval as proof that the right human assented in the right capacity
- letting prior certificate memory impersonate assent to a corrected or narrowed version
- hiding when a device acted but personal acknowledgment remained unproved
- forgetting which stronger effect stayed blocked because the recipient only reached a lower rung

## Stronger-sentence guard

The page may say `the participant cohort was notified and two named representatives acknowledged the corrected notice, but binding waiver assent remains blocked until the required countersign occurs`.
It may not say `everyone agreed` until the required actor, capacity, and assent rows actually support that stronger sentence.
