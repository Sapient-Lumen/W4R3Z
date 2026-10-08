# Action statement receipt page — effective claim, residual scope, and forbidden phrases interface spec

## Purpose

The archive already had receipts for actions and severance.
This document makes one missing receipt concrete.

The page exists to answer one ordinary operator question:

> what exact statement did the product approve after this action, what stronger statements did it refuse, and why?

## Core decision

Every serious action that can change what another human may safely say must emit one first-class **Action statement receipt**.
That receipt is the durable proof object for:

- requested phrase
- executed action class
- approved safe statement
- forbidden stronger statements
- residual scope basis
- next escalation if desired statement was not earned

## Receipt layout

The receipt always renders the same top-level regions in the same order:

1. header strip
2. statement verdict
3. forbidden-phrase block
4. residual-scope summary
5. next-action summary
6. export block
7. expert details drawer

### 1) Header strip

Show:

- object acted on
- acting seat / operator
- executed action class
- receipt timestamp
- strongest next-safe action

### 2) Statement verdict

Show:

- requested phrase
- approved phrase
- claim grade
- audience scope the phrase is safe for

### 3) Forbidden-phrase block

List:

- stronger phrase refused
- blocking reason
- stronger action that would be required before using it

### 4) Residual-scope summary

Summarize the main limiting planes:

- local bytes
- linked cohort
- external retainers
- history / archive
- return / reappearance
- incomplete escalation

### 5) Next-action summary

Show the cleanest next move, for example:

- `Keep current phrase and close`
- `Publish with caveat`
- `Open stronger-action review`
- `Open rotation review`
- `Notify recipients of residual scope`

### 6) Export block

Export formats:

- plain-text copy block
- JSON / structured audit object
- portable receipt bundle reference

The export block must not export forbidden phrases accidentally.

### 7) Expert details drawer

Hide contradiction witnesses, raw graph edges, and policy derivation behind an expert drawer.
They matter, but they are not the semantic center.

## Mandatory fields

- `receipt_id`
- `object_ref`
- `acting_seat_ref`
- `executed_action_class`
- `requested_phrase`
- `approved_phrase`
- `claim_grade`
- `audience_scope`
- `forbidden_phrases[]`
- `forbidden_phrase_reasons[]`
- `residual_scope_summary`
- `strongest_next_action`
- `export_safe_copy`

## Review guarantees

This receipt must let a later reader:

- see what the operator wanted to say
- see what the product actually approved
- see which stronger phrases were refused and why
- see what residual scope prevented the stronger claim
- continue the escalation path without re-deriving the whole case
