# Destructive execution ticket page — one-shot reauth, freshness deadline, and bound-scope commit interface spec

## Purpose

The archive already has a destructive approval barrier.
What it still lacked was the final object that turns reviewed destructive approval into one narrow executable permission without relying on ambient browser/session continuity.

This page exists to answer:

> what exact destructive action is authorized right now, on what endpoint and trust grade, against what reviewed basis, until when, and what invalidates that authority before commit?

## Core decision

AnonSync must compile destructive approval into one first-class **Destructive execution ticket**.
Hard decision:

> **destructive approval never lives as sticky remembered consent.**

It becomes a one-shot, freshness-bound, scope-bound ticket.
If endpoint, trust, acting seat, loss basis, or salvage basis drift materially, the ticket expires and destructive approval must be regenerated.

## Fixed page order

1. **Ticket summary**
2. **Bound review facts**
3. **Freshness deadline and invalidators**
4. **Commit controls and one-shot consumption**
5. **Resulting receipt path**

### 1) Ticket summary

Show:

- `destructive_execution_ticket_page_id`
- destructive action label
- endpoint and acting seat
- current trust grade
- ticket state (`ready`, `reauth-required`, `stale`, `consumed`, `blocked`)
- strongest honest summary

### 2) Bound review facts

Show the exact reviewed facts this ticket binds to:

- destructive review shell ref
- loss matrix ref
- salvage ladder ref
- waiver rows hash or equivalent stable bind
- salvage export receipt refs if any
- approval barrier ref

The operator must be able to answer:

> what reviewed basis does this commit authority actually depend on?

### 3) Freshness deadline and invalidators

Show:

- issued at
- expires at or freshness window
- reauth requirement if any
- invalidators such as:
  - endpoint drift
  - trust-grade change
  - acting-seat change
  - material loss-row change
  - salvage receipt invalidation
  - restart / reconnect that breaks current basis

### 4) Commit controls and one-shot consumption

Controls may include:

- `Re-auth and commit destructive action`
- `Commit now`
- `Return to barrier`
- `Invalidate ticket`

Rules:

- successful commit consumes the ticket
- failed commit may leave the ticket consumed or invalidated, but never silently reusable
- no bulk keyboard shortcut or remembered `approve always` path may bypass ticket consumption

### 5) Resulting receipt path

Show:

- destructive action receipt to be emitted
- linked ledger updates
- whether follow-on recovery or successor review remains open
- strongest safe post-commit sentence expected if commit succeeds

## Public object

### Destructive execution ticket page

Fields:

- `destructive_execution_ticket_page_id`
- `destructive_action_ref`
- `endpoint_ref`
- `acting_seat_ref`
- `transport_trust_grade`
- `ticket_state`
- `bound_review_refs[]`
- `waiver_bind_token`
- `salvage_export_receipt_refs[]`
- `issued_at`
- `expires_at`
- `invalidation_rows[]`
- `reauth_requirement`
- `allowed_controls[]`
- `resulting_receipt_rows[]`
- `generated_at`
