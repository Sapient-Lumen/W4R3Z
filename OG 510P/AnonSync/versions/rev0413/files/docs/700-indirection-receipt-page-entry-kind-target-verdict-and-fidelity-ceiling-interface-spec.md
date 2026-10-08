# Indirection receipt page: entry kind, target verdict, and fidelity ceiling interface spec

## Purpose

This receipt proves what the product concluded about an indirection object and what action was actually taken.

## Receipt questions

The receipt must let a later reader answer:

1. what entry kind was found
2. what platform lane interpreted it
3. what happened to the entry object
4. whether target bytes were in scope
5. whether graph widening occurred
6. what fidelity ceiling remains after the action

## Required fields

- `indirection_receipt_id`
- `subject_ref`
- `seat_ref`
- `entry_path`
- `entry_kind`
- `platform_lane`
- `entry_object_fate`
- `target_scope`
- `target_transitivity_verdict`
- `graph_widening_result`
- `selected_action`
- `conflict_hazard_after_apply`
- `fidelity_ceiling`
- `strongest_safe_sentence`
- `forbidden_overclaim_sentence`
- `issued_at`

## Presentation order

1. summary strip
2. object-fate section
3. target-transitivity section
4. widening result section
5. remaining ceiling section

## Receipt language rules

The receipt must explicitly distinguish:

- `object preserved` from `target included`
- `target out of scope` from `target unresolved`
- `graph widened` from `coupling stayed inside current scope`
- `unsupported here` from `blocked by policy`

## Success criteria

The receipt is successful only when a later operator does not need to reopen support prose to know whether this indirection object stayed as an object, became ordinary bytes, widened the graph, or still carries a fidelity ceiling.
