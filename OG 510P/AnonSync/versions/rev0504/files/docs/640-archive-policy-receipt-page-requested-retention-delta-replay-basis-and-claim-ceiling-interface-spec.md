# Archive-policy receipt page — requested retention delta, replay basis, and claim ceiling interface spec

## Purpose

This receipt exists so later operators do not have to infer meaning from one toggle state, one missing Archive folder, or one sudden re-download.

It answers:

> what Archive-policy change happened here, what retention or replay effect did it actually earn, and what stronger sentence is now forbidden?

## Core decision

Every reviewed Archive-policy mutation must emit one first-class **Archive-policy receipt**.

This receipt is separate from generic preferences history because it preserves the overloaded retention-versus-replay seam.

## Receipt fields

### Required top-level fields

- `archive_policy_receipt_id`
- `subject_ref`
- `acted_on_scope`
- `requested_change`
- `effective_change`
- `retention_delta`
- `replay_basis_before`
- `replay_basis_after`
- `local_access_delta`
- `surviving_witness_refs[]`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `completed_at`
- `acted_by`

### Allowed `effective_change` values

- `no-material-change`
- `retention-shortened`
- `retention-disabled`
- `retention-extended`
- `replay-aid-weakened`
- `access-ceiling-lowered`
- `mixed`
- `blocked-before-apply`

### Allowed `local_access_delta` values

- `unchanged`
- `direct-to-hidden-path-only`
- `direct-to-indirect`
- `direct-to-none`
- `none-to-direct`
- `not-applicable`

## Fixed receipt order

1. **Outcome strip**
2. **Requested versus effective change**
3. **Retention delta**
4. **Replay basis delta**
5. **Local access delta**
6. **Surviving witnesses**
7. **Safe language**

### 1) Outcome strip

Show:

- effective change
- scope touched
- strongest warning that remained true afterward

### 2) Requested versus effective change

Show:

- what the operator asked for
- what actually changed
- what did not change because of platform/path/surface limits

### 3) Retention delta

Show:

- prior horizon
- new horizon
- whether currently retained bytes were removed, merely aging sooner, or unaffected until future events

### 4) Replay basis delta

Show:

- rename/copy replay basis before
- replay basis after
- whether fresh transfer becomes more likely now

### 5) Local access delta

Show:

- whether this seat lost or gained direct recovery access
- which surface remains the honest path for recovery after the change

### 6) Surviving witnesses

Show:

- any other seat still holding stronger or equivalent witness classes
- if none remain, say so plainly

### 7) Safe language

Always show both:

- strongest safe sentence
- stronger rejected sentence

Example:

- `Local Archive retention was disabled on this seat, and rename/copy replay help on this seat is now weaker.`
- `This receipt does not prove that history change was purely cosmetic or that equivalent recovery remains locally available everywhere.`

## Result

A good archive-policy receipt prevents five failures:

- a toggle state becoming the only remembered fact
- retention-only language hiding replay-cost changes
- witness locality being lost from audit history
- support having to rediscover platform/path caveats from scratch
- future operators overclaiming what the policy change actually did
