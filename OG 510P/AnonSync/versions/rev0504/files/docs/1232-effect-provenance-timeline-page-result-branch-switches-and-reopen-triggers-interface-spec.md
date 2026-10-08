# Effect-provenance timeline page — result, branch switches, and reopen triggers

## Purpose

Show how origin explanations changed over time.
A current state may move from `detection induction`, to `manual replay`, to `shared publish observed`, or from `direct seat posture` to `derived cascade`.
The timeline must keep those shifts visible.

## Operator question

> Did the explanation for this state stay the same, or did it switch branches as new evidence arrived or posture changed?

## Fixed page order

1. **Current branch at top**
2. **Earlier branch states**
3. **Branch-switch triggers**
4. **Receipts and supersession map**

## 1) Current branch at top

Show:

- current result class
- current origin class
- confidence now
- time first adopted
- latest reopen reason if any

## 2) Earlier branch states

For each earlier state show:

- result class then
- origin class then
- why it was the strongest safe branch at the time
- what later weakened or superseded it

## 3) Branch-switch triggers

Show typed triggers such as:

- overwrite-heal posture enabled / disabled
- seat narrowed or widened by source or owner
- encrypted-seat role entered / exited
- Archive extraction performed
- touch / rescan induction performed
- runtime witness later contradicted earlier branch
- parent-source derivation changed

The operator must be able to answer: **what changed the explanation, not just the file state?**

## 4) Receipts and supersession map

The page must show:

- which provenance receipt is current
- which earlier receipts are superseded
- which earlier receipt still matters for historical honesty

## What this page must never imply

It must never imply that:

- the latest branch erases earlier uncertainty
- a later manual replay proves the earlier surprising state was manual all along
- a touch-induced notice should overwrite an earlier chronology receipt without explicit supersession
- inherited posture shifts can rewrite earlier direct-actor evidence retroactively
