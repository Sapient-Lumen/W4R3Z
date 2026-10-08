# Blocker scope page: seat, subject, byte, and identity blast-radius interface spec

## Purpose

A warning can be honest and still remain too vague if the operator cannot tell **how wide it is**.
This document defines the interface contract for one first-class **Blocker scope** page.

## Core rule

Whenever a warning, error, or degraded status materially changes availability, freshness, continuity, or safe mutation, the product must publish one explicit scope page that separates:

1. affected seat
2. affected subject or subjects
3. affected files / paths / byte families
4. affected hidden continuity or identity state
5. unaffected neighbors that still behave normally

The product must not let operators infer blast radius from which row happened to be red.

## Public object

### Blocker scope page

Suggested fields:

- `blocker_scope_page_id`
- `warning_ref`
- `seat_scope_rows[]`
- `subject_scope_rows[]`
- `path_or_item_scope_rows[]`
- `hidden_state_scope_rows[]`
- `identity_scope_rows[]`
- `continuing_normal_rows[]`
- `scope_verdict` (`single-item`, `single-subject`, `seat-wide`, `identity-wide`, `mixed`, `unknown`)
- `largest_safe_generalization`
- `generated_at`

### Scope row

Suggested fields:

- `scope_row_id`
- `scope_kind` (`seat`, `subject`, `path`, `item-set`, `hidden-state-family`, `identity-family`, `route-family`, `storage-family`)
- `scope_ref`
- `effect_class` (`blocked`, `suspended`, `degraded`, `uncertain`, `visibility-only`, `normal`)
- `current_consequence`
- `propagation_posture` (`local-only`, `peer-visible`, `identity-visible`, `future-fetch-risk`, `continuity-risk`, `unknown`)
- `strongest_evidence_ref`

## Fixed page order

1. **Blast-radius verdict**
   - one-line scope summary
   - widest affected class
   - strongest unaffected class

2. **Affected now**
   - seat / subject / path / item rows
   - whether the problem is suspend, degrade, or uncertainty

3. **Hidden or continuity-bearing effects**
   - `.sync` or subject-spine effect
   - local DB effect
   - identity / linking effect
   - chronology / clock effect

4. **What continues normally**
   - other subjects
   - other seats
   - unaffected operations inside the same subject

5. **Boundary reminders**
   - what broader actions would be overreach
   - what narrower actions are still safe

## Compact row contract

A dense scope row should preserve these labels in this order:

- `Scope kind`
- `Target`
- `Effect`
- `Propagation`
- `Evidence`

Example:

```text
hidden-state-family   subject spine for Project Atlas   suspended   continuity-risk   service-file loss witness
```

## Anti-goals

- no assumption that one share warning is automatically host-wide
- no assumption that one hidden-state failure is merely cosmetic
- no flattening `degraded` and `suspended` into one color band
- no blast-radius claim that outruns available evidence

## Acceptance test

This page is good enough when a cautious operator can answer:

- exactly what is affected right now
- whether the issue is local, peer-visible, or identity-visible
- what still continues normally
- whether the problem endangers continuity-bearing hidden state
- which broader repairs would be unnecessary overreach
