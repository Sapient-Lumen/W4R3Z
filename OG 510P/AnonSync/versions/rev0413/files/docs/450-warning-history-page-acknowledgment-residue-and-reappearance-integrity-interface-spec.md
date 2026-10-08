# Warning history page: acknowledgment, residue, and reappearance integrity interface spec

## Purpose

A warning that disappears without an accountable history turns back into folklore.
This document defines the interface contract for one first-class **Warning history** page.

## Core rule

Every warning family that can be dismissed, hidden, muted, ignored, or automatically cleared must keep a durable history that answers:

1. when it first appeared
2. when it last appeared
3. whether it was solved, suppressed, accepted, or merely not observed again yet
4. what residue remained at acknowledgment time
5. what fresh evidence would honestly reopen it

The product must not let `Ignore`, `Hide`, `Mute`, or `Disable this warning` erase the semantic trail.

## Public object

### Warning history page

Suggested fields:

- `warning_history_page_id`
- `warning_family_ref`
- `open_instance_refs[]`
- `historical_instance_rows[]`
- `acknowledgment_rows[]`
- `suppression_rows[]`
- `reappearance_rules[]`
- `current_status` (`open`, `acknowledged-open`, `suppressed-open`, `cleared-with-proof`, `historical-only`, `unknown`)
- `generated_at`

### Historical instance row

Suggested fields:

- `instance_id`
- `first_seen_at`
- `last_seen_at`
- `scope_snapshot_ref`
- `strongest_claim`
- `resolution_posture` (`unresolved`, `suppressed`, `accepted-with-residue`, `cleared-with-proof`, `superseded`, `unknown`)
- `verification_ref` nullable

### Acknowledgment row

Suggested fields:

- `acknowledgment_id`
- `actor_ref`
- `action` (`dismiss`, `hide`, `ignore-items`, `suppress-family`, `mute-delivery`, `mark-reviewed`)
- `what_visibility_changed`
- `what_truth_did_not_change`
- `residue_summary`
- `reopen_condition_summary`

## Fixed page order

1. **Current status**
   - open / suppressed / cleared-with-proof / historical-only
   - newest instance summary

2. **Acknowledgment ledger**
   - who hid, ignored, or reviewed what
   - what only changed visibility or delivery

3. **Residual truth**
   - what remained true when the warning was acknowledged
   - which broader risk still existed

4. **Reappearance integrity**
   - what new evidence must reopen the warning
   - whether future sightings branch a new instance or continue the old one

5. **Verification and closure**
   - what proof cleared the warning honestly
   - what proof is still missing when the warning merely went quiet

## Compact row contract

A dense history row should preserve these labels in this order:

- `First seen`
- `Last seen`
- `Action taken`
- `Residue`
- `Current status`

Example:

```text
2026-03-21 07:03   2026-03-21 07:11   ignored item set   missing-source residue remained   suppressed-open
```

## Anti-goals

- no disappearance without history
- no `resolved` language unless verification exists
- no mute/suppress control that silently asserts repair
- no reappearance that loses prior acknowledgment context

## Acceptance test

This page is good enough when a cautious operator can answer:

- whether the warning was actually fixed or merely hidden
- what residue remained at the time of acknowledgment
- what evidence would make it reappear honestly
- who last accepted or suppressed it
- which historical instances still matter to current trust
