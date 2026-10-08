# Quiescence receipt page — requested stop, effective scope, and residual flow interface spec

## Purpose

After a pause or quiescence action is applied, the operator needs one durable object that records what was asked for, what was actually achieved, and what still remained live.
This is that receipt.

## Core decision

Every applied quiescence-related action emits a **quiescence receipt**.
The receipt is durable, auditable, and linkable from rows, events, and reports.

## Receipt sections

1. **Request summary**
2. **Effective stop class**
3. **Stopped phases**
4. **Residual live phases**
5. **Safe sentence**
6. **Stronger action ladder**

## 1) Request summary

Fields:

- target object
- requested phrase
- operator goal
- requested duration
- actor
- apply time

## 2) Effective stop class

Fields:

- achieved class
- certainty
- mechanism used
- whether resume is local/simple or requires a stronger return flow

## 3) Stopped phases

List only phases actually stopped, for example:

- payload send
- payload receive

Do not imply that omitted phases are also stopped.

## 4) Residual live phases

List the phases still alive and their most important consequence, for example:

- delete propagation — remote deletes may still affect local state
- detect/rescan — local edits may still be noticed and indexed
- participation presence — this seat still appears in subject state

## 5) Safe sentence

Render the strongest sentence the receipt supports, for example:

`Payload transfer is paused on this seat; deletes and detection may still continue.`

Below it, show one forbidden stronger sentence, for example:

`Forbidden stronger claim: This share is frozen.`

## 6) Stronger action ladder

If the operator's goal implied stronger stillness, the receipt should point to the next reviewed action, such as:

- disconnect this seat
- enter maintenance isolation
- capture evidence snapshot

## Example receipt

```text
Quiescence receipt qrc_01K...

Request summary
  target .................... share vault/reports
  requested phrase .......... pause for maintenance
  operator goal ............. evidence-stable maintenance
  requested duration ........ until resumed
  actor ..................... seat wkstn-02
  applied at ................ 2026-03-21T19:44:00-04:00

Effective stop class
  class ..................... partial transfer pause
  resume model .............. one-step local resume

Stopped phases
  payload send .............. stopped
  payload receive ........... stopped

Residual live phases
  delete propagation ........ still live
  detect/rescan ............. still live
  indexing/readiness ........ still live
  participation presence .... still live

Safe sentence
  Payload transfer is paused on this seat; deletes and detection may still continue.
  Forbidden stronger claim .. This share is frozen.
```

## CLI projection

```text
anonsync quiesce receipt show <receipt_id>
anonsync quiesce receipt show latest --object <object>
```

## Success condition

A good quiescence receipt lets a future operator answer exactly what kind of stillness was created, what remained live, and what stronger step would be needed for true maintenance-grade quiet.
