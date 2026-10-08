# Quiet break receipt page — quiet tenure, break origin, and successor boundary interface spec

## Purpose

After review, the operator needs one durable object that records how the previous quiet claim ended or narrowed.
This receipt must be stronger than a vague `resume happened` note and narrower than a fantasy audit log of everything forever.

## Core decision

Every successfully reviewed quiet break emits a **quiet break receipt**.

The receipt answers:

- which prior quiet claim it supersedes or narrows
- how long that claim actually held
- who broke it first
- what authority class best explains the break
- what sentence is actually safe now
- what successor claim would be needed next

## Receipt sections

1. **Superseded quiet basis**
2. **Break finding**
3. **Quiet tenure**
4. **Post-break safe sentence**
5. **Successor boundary**
6. **Reopen conditions**

## 1) Superseded quiet basis

Fields:

- prior quiet receipt id
- subject
- prior achieved stillness class
- prior declared window
- issuing actor
- supersession time

## 2) Break finding

List:

- first break timestamp
- breaking seat
- break event class
- authority verdict
- expectedness verdict
- evidence basis

## 3) Quiet tenure

Show:

- receipt issue time
- first break boundary
- total quiet tenure
- whether the break occurred before declared expiry
- whether the prior claim fully ended or only narrowed

## 4) Post-break safe sentence

Example:

`The prior quiet receipt held for 9m 50s and was invalidated by a scheduler-driven reactivation on laptop-ops before the declared window ended.`

Also show one forbidden stronger sentence, for example:

`Forbidden stronger claim: the maintenance isolation remained intact for the full cohort until 03:30.`

## 5) Successor boundary

List what would be required for a successor quiet claim:

- re-request quiet from resumed seat
- re-review cohort coverage
- issue new receipt with fresh timestamps
- or close as expected expiry with no successor needed

## 6) Reopen conditions

List events that would reopen this break receipt, such as:

- better evidence overturning the authority verdict
- discovery that the breaking seat was outside the prior covered cohort
- a later earlier-timestamped event replacing the first break boundary
- a new quiet claim being issued for the same subject

## Example receipt

```text
Quiet break receipt qbr_01K...

Superseded quiet basis
  prior receipt ......... qcr_01K...
  subject ............... share finance/close-books
  prior class ........... quiet-enough-for-declared-risk
  window ................ 03:00–03:30 UTC

Break finding
  first break ........... 03:12:00 UTC
  seat .................. laptop-ops
  event ................. scheduler-boundary
  authority verdict ..... scheduled
  expectedness .......... unexpected-break

Quiet tenure
  issued at ............. 03:02:10
  held for .............. 9m 50s
  status ................ invalidated before declared expiry

Post-break safe sentence
  Prior quiet claim no longer supports cohort-wide stillness.
  Forbidden stronger claim .. maintenance isolation held for the full declared window.

Successor boundary
  - request fresh quiet from laptop-ops
  - re-run quiet agreement review
  - issue successor receipt if coverage is re-earned
```

## Commands

```text
anonsync quiet-break receipt show <receipt_id>
anonsync quiet-break receipt show latest --subject <subject>
```

## Success condition

A good quiet break receipt lets a future operator answer:

- which quiet claim ended
- how long it really lasted
- whose authority ended it
- what sentence is still safe
- what must happen before strong quiet language can return
