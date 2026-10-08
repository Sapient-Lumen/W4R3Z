# Subject source witness page — announced, online, and byte-source grade interface spec

## Purpose

Provide one review surface for the operator question:

- is this subject merely announced in the tree
- is some peer currently online but only carrying placeholders
- is there a current full-byte source
- is the best-known source offline and therefore only a weaker hypothesis
- what safe sentence follows from those facts

## Core decision

Every meaningful `no source peers`, `ghost file`, `placeholder-only`, or ambiguous fetchability event should render one first-class **Subject source witness** page.
The receipt is not just troubleshooting detail.
It is the durable proof of what kind of source existence the product had actually established.

## Fixed page structure

### A. Source verdict strip

Show:

- subject label
- source witness grade (`full-byte-source-present`, `online-placeholder-only`, `ghost-announced-no-source`, `offline-source-likely`, `unknown`)
- strongest safe sentence
- generated time

### B. Announcement versus source card

Show together:

- tree announcement present?
- peer roster presence for candidate peers
- current full-byte source proven?
- placeholder-only presence proven?
- whether the subject may exist only on an offline peer

This card exists so the operator can stop treating name visibility as byte visibility.

### C. Candidate-source table

For each candidate peer show:

- peer presence grade
- eligibility grade for this share
- byte role (`full bytes`, `placeholder only`, `unknown`, `offline candidate`)
- latest freshness of that observation
- whether the peer could satisfy a fetch now

### D. Safe action card

Show the narrowest honest next moves, such as:

- `wait for offline candidate peer to return`
- `touch or move local up-to-date version if operator is certain`
- `ignore ghost warning`
- `open peer presence review`
- `move to broader repair only if continuity evidence weakens further`

### E. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

Examples:

- safe: `This subject is still announced, but no current byte source is proven`
- forbidden: `This file is available from another peer`
- safe: `An offline peer may still carry the latest bytes`
- forbidden: `The latest bytes are safely recoverable`

## Main row contract

A compact source row should preserve this order:

1. announcement state
2. current best source grade
3. strongest safe sentence
4. narrowest next move
5. stronger forbidden sentence or blocker hint

## Suggested object model

```text
subject_source_witness {
  witness_id,
  subject_ref,
  announcement_present,
  source_grade,
  candidate_peers[],
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  next_moves[],
  generated_at
}
```

## Success criteria

A good page lets a later operator answer:

1. whether the subject is only announced or actually source-backed
2. whether any present peer can currently serve bytes
3. whether placeholders are the only currently known form
4. what safe next move exists without overclaiming
5. what stronger sentence remains forbidden
