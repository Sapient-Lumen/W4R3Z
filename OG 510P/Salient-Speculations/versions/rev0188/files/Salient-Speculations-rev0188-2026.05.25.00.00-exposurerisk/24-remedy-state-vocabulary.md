# Remedy state vocabulary

This file normalizes state terms for appeals, complaints, disputes, corrections, stays, and grievance systems.

## Filing and standing

- `notice-given`: the affected party has received a decision or state sufficient to begin contesting.
- `appeal-window-open`: the filing window exists.
- `appeal-filed`: an appeal, complaint, dispute, or challenge was received.
- `standing-pending`: the system is determining whether the filer may bring or view the matter.
- `standing-accepted`: the filer has sufficient relation to proceed.
- `standing-denied`: the filer lacks accepted subject, reliance, representative, or public-interest basis.
- `cure-requested`: the filing lacks information but may be completed.
- `wrong-forum`: the filing belongs elsewhere, ideally with routing information.

## Interim reliance

- `no-stay`: the challenge is pending but does not pause reliance.
- `disputed-only`: downstream systems may continue but must show disputed status.
- `manual-review-only`: automation must pause; human handling may continue.
- `score-excluded`: the challenged item is removed from scoring while pending.
- `processing-restricted`: storage may continue but ordinary use is limited.
- `eligibility-suspended`: access, award, listing, or market participation pauses.
- `holdback-reserved`: money can close but is reserved.
- `emergency-use-only`: use continues only under emergency or override rule.
- `non-reliance-pending`: parties are warned not to rely for specified purposes.

## Evidence and review

- `evidence-requested`: another actor must provide evidence by a clock.
- `source-witness-pending`: a source vendor, registry, or native-system witness has not responded.
- `source-witness-nonresponse`: the witness failed to respond by deadline.
- `sealed-review`: evidence exists but is visible only to a neutral, auditor, regulator, or court.
- `human-review-active`: a qualified reviewer is evaluating the matter.
- `escalated`: the case moved to external dispute body, regulator, court, or senior reviewer.

## Outcome

- `sustained`: the challenge succeeded.
- `denied`: the challenge failed.
- `partly-sustained`: some claims succeeded.
- `corrected-immaterial`: correction occurred without downstream materiality.
- `corrected-material`: correction triggers notice, restatement, or reliance change.
- `unverifiable`: the state could not be confirmed.
- `withdrawn`: filer withdrew or abandoned.
- `moot`: state changed independently.
- `closed-no-remedy`: closed without change.
- `closed-with-remedy`: closed with correction, reversal, restoration, compensation, or notice.

## Abuse and restriction

- `duplicate`: same matter already pending or decided.
- `late-filed`: filing outside the clock.
- `manifestly-unfounded`: no plausible basis after minimal review.
- `bad-faith`: evidence of harassment, evasion, delay, or abuse.
- `abusive-volume`: filing pattern exceeds rate limits after warning.
- `restricted-stay-effect`: appeal may proceed but automatic stay is unavailable.
- `abuse-label-appealable`: the abuse classification itself can be challenged.

## Closure and afterlife

- `recipient-notice-routed`: downstream recipients were notified.
- `non-reliance-final`: prior version is not reliable for specified purposes.
- `archive-only`: retained for history but not current reliance.
- `reopen-triggered`: new evidence or repeated fault reopens review.
- `telemetry-classified`: the case contributes to pattern metrics.

## Usage rule

Use these states when writing or indexing future dossiers. A new state term should be added only if it changes who may rely, who may file, who may see evidence, what clock controls, or what remedy follows.
