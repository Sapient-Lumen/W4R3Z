# Local-first Sync Kit — product plan (2026-03-21)

This note sharpens **P-0076 Local-first Sync Kit** into a more implementation-ready `0.1` shape.

The local-first frontier is now broad enough that “CRDT + sync + maybe encryption” is not a sufficient product plan.
Current Rust substrate already shows three materially different truth classes:

- durable document state and incremental sync,
- ephemeral session/presence state,
- and history/branch retention after export, compaction, or shallow snapshots.

A worthwhile `0.1` should therefore avoid pretending that all “collaboration state” has one persistence, delivery, or comparability story.

## Main question

If somebody started building **P-0076** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A worthy local-first crate should not try to be a universal collaboration platform in `0.1`.
It should ship one **reviewable coordination contract** above today’s engines and transports.

The sharpest `0.1` is:

1. one repo/profile manifest,
2. one durable sync-state receipt,
3. one transport-session receipt,
4. one membership/key-epoch ledger,
5. one explicit presence-surface receipt,
6. one explicit history-retention receipt,
7. one conservative divergence triage report,
8. and one redacted `syncbundle@1` export path.

## What changed in the planning stance

Earlier passes already made engine/store/transport/membership layering explicit.
This pass adds two more review objects that should now be treated as first-class:

### 1. `presence-surface.receipt.json`

Local-first stacks increasingly carry session-level collaboration state such as cursors, selections, awareness payloads, typing indicators, or live peer metadata.
That state is often:

- not persisted,
- not guaranteed to arrive,
- scoped to a connection or short-lived session,
- and not strong enough to stand in for durable user or member identity.

A good `0.1` should therefore publish a receipt with at least:

- `delivery_guarantee`: `best_effort` | `reliable_session_scoped` | `manual_review_required`
- `persistence_posture`: `not_persisted` | `session_cache_only` | `persisted` | `manual_review_required`
- `identity_basis`: `peer_runtime_id` | `device_id` | `member_id` | `manual_review_required`
- `user_identity_strength`: `not_user_identity` | `mapped_by_app` | `manual_review_required`
- `export_policy`: `redact_default` | `summary_only` | `manual_review_required`

### 2. `history-retention.receipt.json`

Current engines already make history posture nontrivial.
Some stacks expose rich branch/checkout semantics; others are sync-first and version-vector heavy; some export modes intentionally keep current state while discarding older history.

A good `0.1` should therefore publish a receipt with at least:

- `durable_state_mode`: `full_history` | `shallow_snapshot` | `update_range_only` | `current_state_only` | `manual_review_required`
- `branching_support`: `native_branch_checkout` | `historical_read_only` | `none` | `manual_review_required`
- `comparison_support`: `diff_against_history` | `frontier_only` | `manual_review_required`
- `compaction_effect`: `history_retained` | `history_truncated_before_frontier` | `snapshot_rebased` | `manual_review_required`
- `support_bundle_history_export`: `redacted_summary` | `range_sample_only` | `full_history_opt_in` | `manual_review_required`

## What the crate should provide other people

1. **One honest durable-sync contract** so app teams can compare replica state and sync outcomes without reverse-engineering engine internals.
2. **One explicit presence contract** so cursors/awareness/ephemeral peer metadata stop being mistaken for persisted state or user identity.
3. **One explicit history-retention contract** so branch/time-travel/shallow-snapshot claims stay reviewable after compaction or export.
4. **One transport receipt** that keeps direct/relay/bootstrap truth visible without turning bootstrap handles into durable identity.
5. **One membership ledger** that makes device/member epochs and revocation reviewable when encrypted collaboration is in play.
6. **One divergence triage artifact** that tells another team whether the problem is sync lag, transport failure, membership drift, history truncation, or manual-review-only.
7. **One redacted bundle path** that can move between support, security, and product teams without leaking unnecessary bootstrap or collaboration metadata.

## Recommended `0.1` crate shape

```text
localsync-core/
localsync-automerge/
localsync-store-sqlite/
localsync-transport/
localsync-membership/
localsync-bundle/
localsync-tck/
cargo-localsync/
```

### `localsync-core`
- shared vocabularies for repo identity, replica identity, frontiers, history posture, presence posture, and comparability classes
- schema generation and diff logic

### `localsync-automerge`
- first engine adapter for durable document/import/export/sync facts
- import of old-version / branch-capable evidence where available

### `localsync-store-sqlite`
- snapshot lineage, compaction checkpoints, and store-profile receipts

### `localsync-transport`
- transport-session capture and comparability rules

### `localsync-membership`
- device/member IDs, epoch history, revocation notes, and redaction rules

### `localsync-bundle`
- export/import/diff for `syncbundle@1`
- redaction defaults for presence payloads and bootstrap convenience material

### `localsync-tck`
- tiny proving-ground scenarios for offline fork/reconnect, revoked device, ephemeral presence loss, and shallow-snapshot comparability drift

### `cargo-localsync`
- `init`
- `capture`
- `capture-presence`
- `capture-history`
- `check`
- `doctor`
- `summary`
- `diff <old> <new>`
- `pack`

## Doctor warnings worth shipping first

- `presence_claims_persisted_without_receipt`
- `presence_identity_overclaimed_as_user_identity`
- `history_claims_full_branching_after_shallow_snapshot`
- `history_export_and_sync_comparability_collapsed`
- `bootstrap_material_exported_without_redaction`
- `membership_epoch_missing_for_encrypted_profile`
- `divergence_triage_missing_history_truncation_branch`

## First proving-ground scenarios

1. **offline fork then reconnect** — durable convergence remains the primary happy path.
2. **revoked device after key epoch** — encrypted collaboration rejection remains explicit.
3. **ephemeral presence without durability** — live cursor/peer state disappears or changes without altering durable sync-state truth.
4. **shallow snapshot keeps state but weakens history claims** — current document state survives export, but older-history comparability becomes narrower.

## What to leave for later

- fully generic engine neutrality
- policy-rich authorization semantics beyond membership/device epochs
- whole-app collaborative presence frameworks
- search/indexing across sync bundles
- organization-level fleet dashboards

## Main guardrail

Do not let `0.1` pretend that all collaboration state is equivalent.
The point of this crate is to keep **durable state**, **ephemeral presence**, **history retention**, **transport posture**, and **membership truth** separately reviewable.
