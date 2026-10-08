# Local-first Sync Kit fixtures

These fixtures exist to make **P-0076 Local-first Sync Kit** look buildable instead of merely aspirational.

The receiver-facing question is:

> what files should another maintainer, support engineer, or security reviewer receive in order to understand why replicas converged, stalled, or diverged?

## Minimal pack for 0.1

- `repo-manifest.schema.json` — repo/profile identity, chosen engine/store/transport lanes, and redaction defaults.
- `sync-state.report.schema.json` — one comparable snapshot of replica heads, snapshot lineage, and compaction state.
- `transport-session.receipt.schema.json` — one sync attempt with direct/relay path, bootstrap method, ordering guarantees, and outcome.
- `membership-ledger.schema.json` — device/member events, epochs, removals, rotations, and visibility notes.
- `presence-surface.receipt.schema.json` — whether collaboration-state is ephemeral, persisted, identity-strong, and exportable.
- `history-retention.receipt.schema.json` — whether current state, history, branches, and comparisons survive compaction/export.
- `divergence-triage.report.schema.json` — conservative diagnosis and recommended next actions.

## Design rules

- Keep **engine**, **store**, **transport**, **membership**, **presence**, and **history-retention** lanes explicit.
- Record **bootstrap material** separately from durable identities.
- Preserve **not comparable** as an honest output when transport or redaction assumptions differ.
- Do not export raw bootstrap tickets by default; support bundles should carry redacted summaries.
- Reuse the shared bundle substrate from **P-0256 Evidence Bundle Core Kit** rather than inventing a new container forever.

## Intended first scenarios

1. `offline_fork_then_reconnect` — same-user multi-device sync over a reliable ordered lane, with an offline fork, later reconnect, and a clean convergence result.
2. `revoked_device_after_key_epoch` — shared-group collaboration where a removed device attempts to sync after a membership epoch change and the session is conservatively rejected.
3. `presence_broadcast_is_not_durable_user_identity` — session-level presence/awareness must not be mistaken for persisted sync state or durable user identity.
4. `shallow_snapshot_keeps_state_but_weakens_history_claims` — current state survives, but older-history comparability and export claims become narrower.
