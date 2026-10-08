# Acknowledgment lineage receipt page — reader capacity, assent grade, and blocked consent sentences

## Purpose

This page is the compact carry-forward receipt for what recipient-action sentence was actually earned for a specific act version.
It exists so later operators can answer `who really read this, who acknowledged it, who assented to it, and what stronger consent claim is still blocked?` without reopening the whole case.

## Mandatory receipt fields

- source act identifier
- source version identifier
- named recipient or audience class covered by this receipt
- highest recipient-action rung earned
- actor capacity that made the rung count
- freshness posture
- highest honest consent sentence earned
- strongest blocked stronger consent sentence
- next event that could strengthen or weaken the receipt

## Required compact verdicts

At minimum the receipt must be able to state verdicts like:

- `notification delivered; open proof absent`
- `opened by linked-device actor; named-person acknowledgment blocked`
- `acknowledged this version; irreversible assent still pending`
- `assented in delegate capacity; principal-specific sentence blocked`
- `remembered trust used for connectivity; fresh assent still required for waiver`
- `binding effect blocked; countersign unresolved`

## Required comparisons

The receipt must keep these comparisons explicit:

- `notified` vs `opened`
- `opened` vs `acknowledged`
- `acknowledged` vs `assented`
- `identity-level action` vs `person-specific action`
- `remembered trust` vs `fresh assent`

## Failure modes the receipt must prevent

- later operators assuming that a bell event means the message was read
- later operators assuming that an any-device approval means the right principal knowingly agreed
- losing the exact capacity in which assent was taken
- losing the reason a stronger person-specific or binding-consent sentence stayed blocked
- losing whether freshness requirements were satisfied or merely bypassed by remembered trust

## Stronger-sentence guard

This receipt may say `opened and acknowledged by named representative; final binding assent blocked because fresh principal-specific assent is still required for this corrected version`.
It may not say `the party knowingly consented` unless that stronger sentence was actually earned.
