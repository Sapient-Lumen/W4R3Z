# Sync mode receipt page — current posture, future default, path basis, and return-contract interface spec

## Purpose

Provide one durable receipt after any meaningful mode-bearing event.
The receipt exists to answer:

- what current-share posture was reviewed
- what future-arrival default was in force or changed
- what byte posture and path basis were true then
- what return contract now applies after clear, local remove, disconnect, or reconnect
- what stronger sentence remains forbidden

## Core decision

Every mode-bearing apply, clear, local remove, disconnect, reconnect, or default-connect mutation should emit a first-class **Sync mode receipt**.
The receipt is not just audit trivia.
It is the durable proof that the product gave a truthful current-vs-future sentence at the moment local mode meaning changed.

## Fixed receipt structure

### A. Transition summary

Show:

- current mode label
- seat / share scope
- mutation scope
- generated time

### B. Current-share truth then

Show:

- current share posture
- byte posture
- bind/path state
- whether the row was active, placeholder-backed, disconnected, or pathless

### C. Future-default truth then

Show:

- future-arrival default in scope
- whether it changed or remained untouched
- whether the receipt is current-share-only, future-default-only, or both

### D. Path basis and return contract

Show:

- path basis
- reconnect basis
- duplicate-path or default-path risk still remaining
- strongest safe return action still available

### E. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

### F. Re-entry and recovery

Show:

- next page to reopen
- whether path review is still required
- whether fetch, reconnect, or future-default edit is the honest next move

## Main row contract

A compact receipt row should preserve this order:

1. current posture
2. future default
3. path basis / return contract
4. strongest safe sentence
5. reopen action

## Suggested object model

```text
sync_mode_receipt {
  receipt_id,
  seat_ref,
  share_ref nullable,
  current_mode_label,
  mutation_scope,
  current_share_posture,
  future_arrival_default,
  byte_posture,
  path_basis,
  return_contract,
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  reopen_actions[],
  generated_at
}
```

## Success criteria

A good receipt lets a later operator answer:

1. what this mode statement meant for the current share
2. what it separately meant for future arrivals
3. what bytes and path basis were actually true then
4. what reconnect or return contract now applies
5. what stronger claim remained forbidden
