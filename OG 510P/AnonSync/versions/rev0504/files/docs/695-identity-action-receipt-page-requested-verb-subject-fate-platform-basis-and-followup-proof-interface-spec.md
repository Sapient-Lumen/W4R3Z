# Identity-action receipt page: requested verb, subject fate, platform basis, and follow-up proof interface spec

## Purpose

Identity work needs a durable receipt because later operators otherwise inherit folklore.
The receipt must answer:

> what identity verb was requested here, what actually happened to each local subject class, what platform rule shaped the byte result, and what follow-up work is still owed?

## Core decision

AnonSync should publish a first-class **identity-action receipt** after every identity-changing action that had non-trivial subject fallout.

## Required receipt fields

- `identity_action_receipt_id`
- `requested_verb`
- `effective_action_verdict`
- `seat_ref`
- `platform_class`
- `subject_fate_rows[]`
- `local_byte_survival_summary`
- `platform_basis_summary`
- `preserve_first_sequence_used`
- `followup_required[]`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `evidence_timestamp`

## Receipt layout

### Header

Show:

- requested verb
- effective verdict
- seat
- platform class
- timestamp

### Subject-fate summary

Show one compact matrix or list with:

- subject class
- governance result
- byte result
- recovery path

### Platform basis block

Explain why the local-byte result was what it was on this platform.
This block must be plain language, not only a raw enum.

### Follow-up block

List remaining work, for example:

- relink required
- manual reimport required
- cleanup residue later
- recovery must be performed on another seat
- no follow-up owed

## Compact row contract

A trustworthy compact row should preserve the following order:

1. requested verb
2. effective action verdict
3. strongest subject-fate summary
4. byte-survival summary
5. strongest next action

Example:

```text
Rename identity on Phone-A · fresh identity created · Advanced subjects left app governance · local synced bytes deleted on this platform by architecture rule · Recover on Desktop-B before relink
```

## Rules

### Rule 1 — requested verb and effective result must stay separate

The receipt must preserve whether the operator asked for `rename`, `unlink`, `relink`, or `uninstall`, even if the effective local consequence was larger.

### Rule 2 — platform basis must be preserved, not inferred later

If bytes were deleted or preserved because of platform architecture, the receipt must say so directly.

### Rule 3 — subject-fate rows must outlive the transient review UI

Later operators should not have to reopen the original review to know what happened.

## Acceptance criteria

A later operator can:

- prove which identity verb was requested
- prove what happened to each local subject class
- prove why byte survival differed on this platform
- know what follow-up work is still required
- quote one safe post-action sentence without folklore
