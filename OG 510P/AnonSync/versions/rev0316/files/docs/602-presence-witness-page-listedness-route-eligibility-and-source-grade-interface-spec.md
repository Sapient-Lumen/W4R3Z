# Presence witness page — listedness, route grade, eligibility, and source-grade interface spec

## Purpose

Give the operator one reviewed answer to:

- what kind of presence proof exists right now
- whether the peer is only historically listed, currently connected, or actually eligible
- whether the subject has a current byte source or only announcement residue
- what sentence is still true right now
- what next observation would strengthen or weaken that sentence

This page is the presence-truth companion to membership, network-eligibility, pause, and subject-delivery pages.
It should appear whenever a peer row, share row, or file row could otherwise overstate what is actually present.

## Inputs

- seat identifier
- peer identifier
- optional subject identifier
- listing grade (`hidden`, `historical-listed`, `currently-listed`, `unknown`)
- route grade (`connected-now`, `disconnected`, `sleep-offline`, `paused`, `unknown`)
- eligibility grade (`eligible`, `share-policy-blocked`, `seat-policy-blocked`, `sleep-blocked`, `paused-limited`, `unknown`)
- source grade for subject (`full-byte-source-present`, `placeholder-only-present`, `ghost-announced-no-source`, `source-may-exist-offline`, `not-applicable`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- next strengthening observation
- freshness of each observation plane

## Primary questions this page must answer

1. Is this peer only listed, or actually connected now?
2. If connected, is it actually eligible to participate for this share?
3. If a subject is in view, does any currently present peer still have full bytes for it?
4. What exact sentence is still honest right now?
5. What future observation would justify a stronger sentence?

## Layout

### A. Presence verdict strip

Fields:

- peer label
- optional subject label
- current presence witness grade
- strongest safe sentence

Example verdicts:

- `Peer is historically listed but not connected now`
- `Peer is connected now, but this share is forbidden on the current network`
- `Peer is visible and eligible, but no current byte source is proven for this subject`
- `Peer is connected and eligible; full bytes for this subject are present on this peer`

### B. Listedness card

Show:

- whether the peer is merely in historical total
- whether it is hidden from view rather than revoked
- whether it aged out of ordinary connection view
- freshness of the listing observation

This card exists so the operator can stop treating roster presence as live participation proof.

### C. Route / connection card

Show:

- online/offline witness
- whether the witness comes from live connection, stale roster memory, or inferred absence
- whether pause or sleep affects what the online dot means
- current sync/posture mode if relevant

### D. Eligibility card

Show:

- whether this share may currently connect / detect / transfer on this seat
- whether the blocker is share policy, seat policy, sleep policy, or pause semantics
- strongest capability still allowed
- strongest capability currently blocked

### E. Source-grade card

If a subject is in scope, show:

- whether a current full-byte source is proven
- whether only placeholders are known
- whether the subject is merely announced without any current byte source
- whether an offline peer may still carry the latest bytes
- current fetchability implication

### F. Claim ceiling card

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker or missing witness
- next observation that would strengthen the claim

## Compact row contract

A compact row should preserve this order:

1. listing grade
2. route grade
3. eligibility grade
4. source grade
5. strongest safe sentence

Example:

```text
Historically listed     Disconnected     Unknown eligibility     No current byte source proven     Peer remains known but cannot currently serve this subject
```

## Behavior rules

- This page must appear whenever a visible row could be misread as stronger presence than the product can prove.
- The product must not treat `online dot`, `roster listed`, and `current source` as interchangeable.
- If source grade is weaker than peer grade, the weaker grade must win the visible sentence.
- If a hidden-offline device may return, the page must say so rather than implying removal.

## Success criteria

The page is successful only when an operator can answer:

1. what kind of presence proof exists
2. what stronger proof is still missing
3. whether this share is actually eligible now
4. whether current full bytes exist anywhere presently reachable
5. what statement the product may honestly make now
