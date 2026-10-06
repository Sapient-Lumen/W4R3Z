# RFC-0174: Confirmable change-sets and auto-revert

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD already models changes as artifacts + receipts (`change-set`, `change-receipt`).

However, “commit confirmed” semantics are currently only described informally:
- the `change-set` schema has a `confirm` block, but behavior isn’t pinned down
- there is no dedicated evidence object for a confirmation action
- rollback behavior can drift into bespoke per-component implementations

## Goals

- Define a single standardized primitive: **apply → pending-confirm → confirm OR auto-revert**.
- Make confirmation itself a **typed, audit-friendly receipt**.
- Ensure the auto-revert mechanism composes with:
  - A/B updates over ZFS boot environments
  - boot try-counters / boot assessment
  - incident bundles

## Non-goals

- Replacing “health-gated updates” with confirmation; they are complementary.
- Designing the full UI/workflow for confirmation (CLI, API, portal) in this RFC.

## Proposal

### 1) Change-set intent (already exists)

`spec/change.set.schema.json` already includes:

- `confirm.required` (boolean)
- `confirm.timeout_sec` (integer)
- `confirm.authority` (optional ref)

This RFC makes the semantics normative:

- If `confirm.required=true`, the apply engine MAY complete with `change-receipt.status="pending-confirm"`.
- If confirmation does not occur within the window, the system MUST revert to the previous known-good generation (unless policy explicitly disables auto-revert for that change type).

### 2) Confirmation is a receipt

Add a new evidence object:

- `change-confirm-receipt` (`spec/change.confirm.receipt.schema.json`)

This receipt ties together:
- the `change_set_digest`
- who/what confirmed (`actor`, optional)
- what authority was used (`authority_ref`, optional)
- the time of confirmation

### 3) Auto-revert via boot assessment

For changes that affect bootability or access, the revert mechanism SHOULD be implemented via:
- staging into a candidate BE
- bounded boot attempts
- fallback on failure or timeout

This is specified in RFC-0173.

## Data contract changes

- Add `spec/change.confirm.receipt.schema.json` and example.
- Update `spec/change.receipt.schema.json` to allow an optional `confirm` section describing:
  - confirmation deadline
  - confirmation receipt digest (if confirmed)
  - auto-revert metadata

## Rollout plan

1) Introduce the new schema + example.
2) Update apply engine:
   - when confirmation required, set status `pending-confirm` and record deadline
   - on confirmation, emit `change-confirm-receipt` and then commit
   - on timeout, auto-revert and emit a rolled-back receipt + incident bundle

## Risks / tradeoffs

- Confirmation can be overused. Policy should reserve it for high-risk transitions.
- Without a reliable time source, a time-based deadline can be gamed; policy can prefer boot-count windows early in bootstrapping.

## Related

- `docs/242-confirmable-change-sets-and-auto-revert.md`
- RFC-0173 (boot try-counters)
- `docs/218-configuration-transactions-and-receipts.md`
- `docs/219-change-sets-and-apply-engine.md`
