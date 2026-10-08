# Acknowledgment timeline page — notice, open, acknowledgment, assent, and revocation events

## Purpose

This page is the time-ordered event surface for how a typed act progressed from signal to possible binding assent.
It exists so the archive can distinguish `the system emitted something` from `a named actor knowingly bound themselves in the required capacity`.

## Mandatory event families

- notification created
- notification delivered
- notification mirrored across linked devices
- message opened
- message reopened after supersession
- acknowledgment submitted
- assent submitted
- countersign submitted
- assent revoked or withdrawn
- actor-capacity challenged
- fresh assent required
- fresh assent obtained
- remembered approval used
- stronger consent denied

## Mandatory columns

- event time
- event type
- source act version
- target recipient or audience class
- acting identity or device
- acting capacity class
- recipient-action rung after event
- freshness posture after event
- strongest sentence newly earned or newly blocked
- exact cause of widening, narrowing, dispute, or revocation

## Required comparisons

The timeline must keep these comparisons explicit:

- `notification delivered` vs `message opened`
- `message opened` vs `acknowledgment submitted`
- `acknowledgment submitted` vs `assent submitted`
- `assent submitted` vs `binding effect unlocked`
- `remembered approval used` vs `fresh assent obtained`

## Required badges

- `notified`
- `opened`
- `acknowledged`
- `assented`
- `countersign-pending`
- `fresh-assent-required`
- `fresh-assent-obtained`
- `memory-used`
- `capacity-challenged`
- `binding-effect-blocked`

## Failure modes the timeline must prevent

- collapsing a synchronized notification into proof of reading
- losing which exact version was opened or acknowledged
- losing when remembered approval was used instead of fresh assent
- implying that one owner action permanently settles a later corrected version
- forgetting when a later dispute downgraded an earlier consent sentence

## Stronger-sentence guard

The timeline may say `the notification mirrored across linked devices on day 1, a named principal opened the corrected version on day 2, acknowledgment was recorded on day 3, a second required countersign never arrived, and binding waiver remained blocked throughout`.
It may not say `consent complete on day 1` unless every required rung and capacity row supports that stronger sentence.
