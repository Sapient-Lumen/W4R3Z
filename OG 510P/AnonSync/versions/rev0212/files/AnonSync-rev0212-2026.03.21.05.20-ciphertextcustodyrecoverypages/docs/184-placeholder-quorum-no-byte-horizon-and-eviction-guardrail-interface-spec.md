# Placeholder quorum, no-byte horizon, and eviction guardrail interface spec

## Purpose

The archive already had fetchability, full-copy witness, and file availability.
What it still lacked was one interface contract for the sharpest destructive-materialization question:

> before a user evicts bytes, disconnects a selectively materialized subtree, or trusts placeholder-visible content, what page proves that *some real bytes still exist somewhere* and that the action is not about to create a names-only horizon?

Current official Resilio docs make this seam sharper than the earlier availability pass.
They still say `.rsls` placeholders are 0-byte representations of shared files, they still warn that if every peer turns a file into a placeholder then only placeholders remain with no actual file, they still say disconnecting a selectively synced folder removes placeholders from the folder, and the power-user docs still note that the `disable_remove_from_all_devices` guardrail is ignored in Linux WebUI.
That is useful candor.
It is not enough for a trustworthy operator surface.

## Core decision

AnonSync should require one explicit **eviction guardrail review** whenever bytes may disappear from the currently reachable mesh or from the active local namespace.

That review must distinguish:

- `evict local bytes but witnesses remain elsewhere`
- `names remain but only weak witnesses remain`
- `this action would create a no-byte horizon`
- `this action also changes namespace visibility`
- `this action is merely disconnecting presentation, not deleting share state`

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- a visible placeholder is not proof that any full copy still exists
- eviction and deletion semantics can still be confused because both start from the same placeholder surface
- disconnecting a selectively synced folder changes local namespace, not just local bytes
- one safety toggle for `remove from all devices` is ignored in one major projection family
- subfolders and placeholder states still carry special handling nuance that is easy to miss

AnonSync should therefore insist on a stronger rule:

> any action that could turn bytes into names-only state must show witness strength, horizon risk, and namespace side effects in one place before apply.

## Fixed review order

Every non-trivial eviction or disconnect case should render the same sections in the same order:

1. **Current bytes and witnesses**
2. **Requested eviction or disconnect effect**
3. **No-byte horizon risk**
4. **Admissible outcomes and receipt promise**

### 1) Current bytes and witnesses

This section should show:

- local materialization state
- known remote full-copy witnesses
- witness freshness and confidence
- whether any witness is policy-limited, stale, or unavailable now

The operator must be able to answer: **where do real bytes still exist?**

### 2) Requested eviction or disconnect effect

This section should show:

- whether the action removes bytes only, placeholders only, or local bind visibility entirely
- whether remote peers are affected
- whether archive/preservation makes any stronger claim here or not

The operator must be able to answer: **what exactly disappears if I continue?**

### 3) No-byte horizon risk

This section should show:

- whether the product can still prove at least one durable full copy after apply
- whether the result becomes guarded because all known witnesses are placeholders or stale
- whether the action is blocked because it would strand the subject at names-only state

The operator must be able to answer: **am I about to keep names but lose bytes?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Evict local bytes safely`
- `Pin one remote witness first`
- `Keep placeholder but do not delete remotely`
- `Disconnect local bind only`
- `Block because no full-copy witness would remain`

The receipt promise must record the witness set and the horizon verdict.

## Public objects

### Eviction guardrail review

Fields:

- `eviction_guardrail_review_id`
- `share_ref`
- `scope_ref`
- `requested_action` (`evict-local-bytes`, `disconnect-local-bind`, `remove-placeholder-view`, `delete-share-visible`, `mixed`)
- `local_materialization_state`
- `witness_summary`
- `horizon_risk` (`none`, `guarded`, `high`, `blocked`)
- `namespace_side_effects[]`
- `admissible_actions[]`
- `generated_at`
- `expires_at` nullable

### Eviction guardrail receipt

Fields:

- `eviction_guardrail_receipt_id`
- `review_ref`
- `applied_action`
- `post_apply_witness_summary`
- `post_apply_horizon_risk`
- `namespace_effect`
- `completed_at`
- `provenance_ref` nullable

## Row and card rules

A truthful compact row should keep these facts in stable order:

1. path or subtree
2. local bytes state
3. witness strength
4. horizon verdict
5. next honest action

Example:

```text
/Projects/Video/raw     local bytes present     2 full-copy witnesses / 1 stale     none     Evict local bytes
/Projects/Video/proxy   placeholder only        0 fresh full-copy witnesses          blocked  Pin a witness first
```

The product should never let a generic trash icon stand in for that distinction.

## CLI implications

A minimum public surface should include:

```text
anonsync evict review --path <path>
anonsync evict apply <eviction_guardrail_review_id>
anonsync evict receipt show <eviction_guardrail_receipt_id>
anonsync witness show --path <path>
```
