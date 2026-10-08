# Equivalence receipt page: compare plane, proof class, and supported sentence interface spec

## Purpose

This receipt proves what the product concluded about sameness, under which comparison contract, and with what remaining ceiling.

## Receipt questions

The receipt must let a later reader answer:

1. what objects or candidates were judged
2. what compare plane was active
3. what proof class was reached
4. which optional planes were in scope, disabled, or deferred
5. what sentence the product was actually allowed to say
6. what stronger claim remained unsupported

## Required fields

- `equivalence_receipt_id`
- `subject_ref`
- `seat_ref`
- `candidate_refs[]`
- `effective_compare_plane`
- `proof_class`
- `content_parity_verdict`
- `optional_plane_rows[]`
- `later_apply_rows[]`
- `decision_taken`
- `strongest_safe_sentence`
- `forbidden_overclaim_sentence`
- `issued_at`

## Optional plane row

- `plane_name`
- `status` (`native-proven`, `carried-only`, `later-apply`, `disabled`, `not-synchronized`, `unknown`)
- `why`

## Presentation order

1. summary strip
2. compare-plane section
3. proof-class section
4. optional/later-apply section
5. claim-ceiling section

## Receipt language rules

The receipt must explicitly distinguish:

- `same under current compare plane` from `fully identical in every representable property`
- `content proven` from `optional planes deferred`
- `carried for later` from `applied here`
- `quiet now` from `no future difference can emerge`

## Success criteria

The receipt is successful only when a later operator does not need to reopen several reference pages to know what counted as same, how it was proven, what was deferred, and what stronger sentence was deliberately not claimed.
