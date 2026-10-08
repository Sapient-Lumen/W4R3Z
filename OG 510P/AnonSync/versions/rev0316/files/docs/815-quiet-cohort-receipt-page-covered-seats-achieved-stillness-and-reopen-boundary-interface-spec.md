# Quiet cohort receipt page — covered seats, achieved stillness, and reopen boundary interface spec

## Purpose

After review, the operator needs one durable object that records what level of shared quiet was actually achieved.
This receipt must be stronger than a local pause receipt and narrower than a fantasy global freeze.

## Core decision

Every successfully reviewed quiet agreement emits a **quiet cohort receipt**.

The receipt answers:

- which seats were covered
- which seats were intentionally excluded
- which seats remained unresolved
- what sentence is actually earned
- what event would reopen the case

## Receipt sections

1. **Operation summary**
2. **Covered cohort**
3. **Excluded / unresolved seats**
4. **Achieved stillness class**
5. **Safe sentence**
6. **Reopen boundary**

## 1) Operation summary

Fields:

- subject
- operation intent
- requested stillness class
- requested window
- issuing actor
- issued time

## 2) Covered cohort

List each covered seat with:

- achieved proof type
- matched stop class
- proof timestamp

## 3) Excluded / unresolved seats

List them separately.

For each, show:

- why excluded or unresolved
- whether exclusion was low-risk or claim-limiting
- whether future reappearance or acknowledgement would reopen the receipt

## 4) Achieved stillness class

Allowed values:

- `local-only`
- `covered-subset-quiet`
- `quiet-enough-for-declared-risk`
- `full-target-cohort-quiet`

The receipt may never silently upgrade a subset into a full target cohort.

## 5) Safe sentence

Example:

`Quiet agreement achieved for wkstn-02 and nas-01; one writable peer remains outside coverage, so only covered-seat stillness is earned.`

Also show one forbidden stronger sentence, for example:

`Forbidden stronger claim: the subject is fully frozen everywhere.`

## 6) Reopen boundary

List the events that invalidate or reopen the receipt, such as:

- a covered seat resumes
- a previously unresolved relevant seat becomes active
- a new writable seat joins the subject
- the window expires
- proof for a covered seat ages out or is superseded

## Example receipt

```text
Quiet cohort receipt qcr_01K...

Operation summary
  subject ............... share finance/close-books
  intent ................ evidence-capture
  requested stillness ... maintenance isolation
  window ................ 2026-03-22 01:00–01:30 UTC

Covered cohort
  wkstn-02 .............. matched via local quiet receipt qrc_...
  nas-01 ................ matched via quiet-window token qwin_...

Excluded / unresolved
  laptop-ops ............ unresolved writable peer; claim-limiting
  phone-audit ........... excluded observer seat; low-risk

Achieved stillness class
  covered-subset-quiet

Safe sentence
  Quiet agreement achieved across 2 covered seats; full cohort quiet not earned.
  Forbidden stronger claim .. Subject fully frozen everywhere.

Reopen boundary
  - laptop-ops becomes active on this subject
  - either covered seat resumes
  - declared window expires
```

## Commands

```text
anonsync quiet-cohort receipt show <receipt_id>
anonsync quiet-cohort receipt show latest --subject <subject>
```

## Success condition

A good quiet cohort receipt lets a future operator answer:

- what shared quiet was actually achieved
- which seats were and were not covered
- what sentence remains safe
- exactly what event would invalidate that sentence
