# Rev0623 — durable AsyncAPI event identity replay rejection

Rev0623 closes a replay gap left after rev0622 proof binding. A valid redelivered AsyncAPI event with a fresh JWT `jti` could still be accepted because the durable replay check only keyed on token identity. That is insufficient for event systems where CloudEvents `source` + `id` is the semantic event identity.

## Runtime changes

- `IReplayLedgerBackend` now exposes `contains_event_identity(source, id)`.
- The local JSONL ledger tracks committed AsyncAPI CloudEvents identities, persists them in the existing entry material, and rejects duplicate identities during reload.
- The SQLite/WAL ledger tracks committed and staged event identities, creates a partial unique index over async `cloud_event_source` + `cloud_event_id`, and rejects duplicate identities during reload.
- Ledger stage now fails closed for AsyncAPI rows missing CloudEvents `source` or `id`.
- Capability metadata advances to exact v18 with explicit event-identity replay requirements.

## Regression coverage

`--selftest-ledger-event-identity-replay` stages one AsyncAPI event, verifies that its event identity is visible before commit, rejects a second staged event with the same `source` + `id` and a fresh `jti`, commits, reloads, and rejects the duplicate again. It runs against both `local-jsonl` and `sqlite-wal`.

`tools/validate_rev0623_event_identity_replay.py` adds an end-to-end fixture mutation: it takes two valid positive AsyncAPI cases with distinct tokens, changes the second event to reuse the first event's CloudEvents identity, recomputes the rev0622 proof binding so proof verification still passes, and verifies that the ledger rejects the duplicate event identity.

## Refactor/audit note

This revision deliberately avoided expanding registry surface beyond the required capability version bump. The main refactor is an explicit replay-identity interface across ledger backends plus centralized event-identity key construction in each backend.

## Remaining ceiling

This is local replay rejection only. It is not distributed exactly-once delivery, broker-side dedupe, a durable side-effect reservation/outbox protocol, or a retention/collision policy for event identities across clusters or time windows.
