# Rev0625 prepared-effect idempotency

## Problem

Earlier revisions durably rejected duplicate JWT `jti` values and, for AsyncAPI, duplicate CloudEvents `(source,id)` identities. That still left a crash-boundary gap: a caller could present a fresh token for the same HTTP effect or the same normalized operation body, and the ledger had no durable business-effect reservation distinct from the bearer token.

## Change

Rev0625 adds a deterministic `effect_idempotency_key` to each accepted ledger row and marks the row as `effect_state="prepared"`. The key is computed before the decision is emitted and becomes part of the ledger hash material.

For normalized OpenAPI requests the material includes:

- material version: `anonsync-effect-idempotency-v1`
- kind
- tenant
- contract file
- operation id
- contract digest
- HTTP method
- path
- canonical body digest

For normalized AsyncAPI events the material includes:

- material version: `anonsync-effect-idempotency-v1`
- kind
- tenant
- contract file
- operation id
- contract digest
- channel
- action
- CloudEvents source/id
- canonical payload digest

Both local-jsonl and SQLite/WAL reject duplicate prepared-effect keys even when the duplicate has a fresh JWT `jti`.

## SQLite/WAL schema change

SQLite/WAL advances to schema v4:

- `ledger_entries.effect_idempotency_key TEXT NOT NULL UNIQUE CHECK(length(effect_idempotency_key)=64)`
- `ledger_entries.effect_state TEXT NOT NULL CHECK(effect_state='prepared')`
- `backend_profile.schema_version = 4`
- `backend_profile.entry_material_version = anonsync-replay-ledger-entry-v3-effect-prepared`

Read-only snapshot verification now requires those columns, rejects duplicate effect keys, verifies `effect_state='prepared'`, and recomputes the row hash with both fields.

## What this fixes

The ledger now contains a durable local reservation for the effect that an accepted decision is about to authorize. A retry with a fresh token cannot create a second accepted local ledger row for the same normalized effect.

## What this does not fix

The cube still does not dispatch or confirm external side effects. There is no downstream outbox worker, no `APPLIED`/`FAILED`/`COMPENSATED` state machine, no broker transaction, and no distributed dedupe. Rev0625 is the first durable reservation layer on the path to that larger protocol.

## Validation

Rev0625 adds `--selftest-ledger-effect-idempotency`. The test exercises local-jsonl and sqlite-wal backends, checks duplicate rejection while staged, checks invalid key rejection, commits, reloads, and verifies duplicate rejection after reload.
