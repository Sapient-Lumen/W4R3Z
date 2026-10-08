# Presence witness receipt page — listedness, route grade, and source-proof interface spec

## Purpose

Provide one durable receipt after any meaningful presence-grade event.
The receipt exists to answer:

- what kind of peer or subject presence was actually proven
- whether the proof was roster-only, connection-level, eligibility-level, or byte-source-level
- what strongest safe sentence the product emitted
- what stronger sentence remained forbidden
- how to reopen the relevant review later

## Core decision

Every peer-presence review, subject-source review, hidden-device event, source-loss warning, or presence-strengthening observation should emit a first-class **Presence witness receipt**.
The receipt is not just audit trivia.
It is the durable proof that the product gave a truthful sentence at the moment presence meaning changed.

## Fixed receipt structure

### A. Transition summary

Show:

- peer / seat / optional subject
- presence witness grade observed
- generated time

### B. Why it was graded that way

Show:

- listing grade
- route / connection grade
- eligibility grade
- source grade if subject is in scope
- trigger origin summary

### C. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

### D. Strengthening and weakening basis

Show:

- next observation that would strengthen the claim
- next observation that would weaken the claim
- best page to reopen
- whether another seat or surface is better suited for stronger proof

## Main row contract

A compact receipt row should preserve this order:

1. presence witness grade
2. strongest safe sentence
3. stronger forbidden sentence
4. next strengthening basis
5. reopen action

## Suggested object model

```text
presence_witness_receipt {
  receipt_id,
  seat_ref,
  peer_ref,
  subject_ref?,
  listing_grade,
  route_grade,
  eligibility_grade,
  source_grade,
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  strengthen_on[],
  weaken_on[],
  generated_at
}
```

## Success criteria

A good receipt lets a later operator answer:

1. what kind of presence was actually proven
2. what stronger proof was still missing
3. what sentence the product was allowed to say then
4. what stronger sentence remained forbidden
5. what future observation would justify changing the sentence
