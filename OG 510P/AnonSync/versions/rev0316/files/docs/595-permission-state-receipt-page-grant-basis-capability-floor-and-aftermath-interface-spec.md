# Permission state receipt page — grant basis, capability floor, and aftermath interface spec

## Purpose

Provide one durable receipt after any meaningful platform-permission event.
The receipt exists to answer:

- what permission family changed
- why it was requested
- what capability floor the seat now has
- what stronger sentence remains forbidden
- how to reopen the relevant review later

## Core decision

Every permission grant, denial, defer, revoke, or restore event should emit a first-class **Permission state receipt**.
The receipt is not just audit trivia.
It is the durable proof that the product gave a truthful sentence at the moment platform power changed.

## Fixed receipt structure

### A. Transition summary

Show:

- permission family
- seat / platform family
- transition requested
- transition observed
- generated time

### B. Why it happened

Show:

- prompting action
- trigger origin summary
- whether the operator initiated it directly or it surfaced as a prerequisite

### C. Capability floor now

Show rows for affected capability families with:

- floor now (`enabled`, `degraded`, `blocked`, `deferred`)
- one strongest safe action still available
- one strongest blocked or narrowed action

### D. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

### E. Re-entry and recovery

Show:

- next page to reopen
- whether OS settings handoff is required for change
- whether another seat is better suited for the blocked capability

## Main row contract

A compact receipt row should preserve this order:

1. permission family
2. transition observed
3. capability floor now
4. strongest safe sentence
5. reopen action

## Suggested object model

```text
permission_state_receipt {
  receipt_id,
  seat_ref,
  platform_family,
  permission_family,
  transition_requested,
  transition_observed,
  prompting_action_class,
  capability_floor_rows[],
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  reopen_actions[],
  generated_at
}
```

## Success criteria

A good receipt lets a later operator answer:

1. what permission changed
2. why the product asked for it
3. what the seat can still honestly do now
4. what stronger claim remains forbidden
5. where to return if they want to widen or narrow the permission later
