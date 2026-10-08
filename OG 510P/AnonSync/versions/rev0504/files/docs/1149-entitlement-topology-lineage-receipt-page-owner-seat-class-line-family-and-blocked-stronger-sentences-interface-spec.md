# Entitlement topology lineage receipt page — owner, seat class, line family, and blocked stronger sentences

## Purpose

Preserve the reviewed truth after license apply, owner transfer, seat approval, reclaim, or line-family migration decisions.

## Receipt questions

- Who owned the entitlement graph at review time?
- Was this seat self-owned, linked-under-owner, borrowed, family-scoped, or line-default?
- What counting basis applied?
- What line-family compatibility or incompatibility mattered?
- What stronger sentence was intentionally blocked?

## Receipt fields

- `receipt_id`
- `seat_ref`
- `owner_identity_ref`
- `seat_class`
- `counting_basis`
- `line_family`
- `topology_verdict`
- `owner_transfer_verdict`
- `borrower_dependency_summary`
- `migration_verdict`
- `survivor_boundary`
- `blocked_stronger_sentences[]`
- `generated_at`

## Required narrative sections

### 1) Basis at time of review

State the exact entitlement topology that was reviewed.

### 2) Mutation considered

State whether the action was apply, transfer, borrow, reclaim, relink-for-license, or upgrade.

### 3) Survivors and losses

Separate:

- bytes on disk
- current capability
- owner controls
- borrower seat validity
- linked-cohort safety
- UI/share configuration continuity

### 4) Blocked stronger sentences

Examples:

- `Upgrade is safe.`
- `This seat is independently licensed.`
- `Applying this key only activates this one seat.`
- `This mixed v2/v3 linked cohort is harmless.`

## Rules

- Receipts must outlive future owner changes.
- Receipts must preserve line-family context.
- Receipts must not flatten borrowed-seat dependency into generic `licensed` language.
- Receipts must preserve the strongest blocked sentence, not just the final verdict.

## Acceptance criteria

A later operator can reopen the receipt and understand the exact topology, dependency edges, migration posture, and survivor boundary without re-reading license folklore.