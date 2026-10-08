# Network eligibility receipt page — policy basis, detection floor, and wake proof interface spec

## Purpose

Provide one durable receipt after any meaningful network-eligibility event.
The receipt exists to answer:

- what network class and policy basis were in force
- why the share was eligible, blocked, or sleeping
- what detection / transfer floor the seat had at that moment
- what stronger sentence remained forbidden
- how to reopen the relevant review later

## Core decision

Every network-eligibility mutation, stoppage review, wake re-entry, or policy delta should emit a first-class **Network eligibility receipt**.
The receipt is not just audit trivia.
It is the durable proof that the product gave a truthful sentence at the moment participation meaning changed.

## Fixed receipt structure

### A. Transition summary

Show:

- share / seat
- current network class
- eligibility verdict observed
- generated time

### B. Why it happened

Show:

- seat-wide network rule
- share-wide network rule
- core activity state
- trigger origin summary

### C. Participation floor now

Show rows for affected capability families with:

- floor now (`eligible`, `detect-only`, `no-detect-no-transfer`, `sleeping`, `unknown`)
- one strongest safe action still available
- one strongest blocked or narrowed action

### D. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

### E. Re-entry and wake proof

Show:

- next page to reopen
- whether automatic wake/resume is expected
- what future observation would strengthen the claim
- whether another seat is better suited right now

## Main row contract

A compact receipt row should preserve this order:

1. network class
2. eligibility verdict observed
3. participation floor now
4. strongest safe sentence
5. reopen action

## Suggested object model

```text
network_eligibility_receipt {
  receipt_id,
  seat_ref,
  share_ref,
  platform_family,
  current_network_class,
  seat_policy_basis,
  share_policy_basis,
  core_activity_state,
  eligibility_verdict,
  participation_floor_rows[],
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  wake_or_reentry_actions[],
  generated_at
}
```

## Success criteria

A good receipt lets a later operator answer:

1. what network class and policy stack were active
2. why the share was eligible or blocked
3. what the share could still honestly do then
4. what stronger claim remained forbidden
5. what event would later justify a stronger sentence
