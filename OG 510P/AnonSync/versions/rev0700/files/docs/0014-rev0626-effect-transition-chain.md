# Rev0626 SQLite effect transition chain

## Problem

Rev0625 made accepted decisions safer by reserving a deterministic `effect_idempotency_key` and storing `effect_state="prepared"`. That closed a local duplicate-effect admission gap, but the state never advanced. Operators could see that an effect had been prepared, not whether a downstream worker later applied, failed, or compensated it.

Mutating the original decision row would be the wrong fix because the decision row is already part of the ledger hash chain. Changing it would either break the chain or require rewriting history.

## Change

Rev0626 keeps decision rows immutable and adds a SQLite/WAL append-only effect transition chain:

- `effect_transition_metadata(id, line_count, head_hash)` tracks the transition chain head.
- `effect_transitions(sequence, previous_hash, transition_hash, effect_idempotency_key, terminal_state, result_digest_sha256, transition_reason)` stores terminal effect evidence.
- `terminal_state` is restricted to `applied`, `failed`, or `compensated`.
- `effect_idempotency_key` must reference a previously prepared decision row.
- `result_digest_sha256` must be a lowercase SHA-256 digest.
- each prepared effect can have at most one terminal transition.
- transition hashes are computed from material version `anonsync-effect-transition-v1`, sequence, previous transition hash, effect key, terminal state, result digest, and reason.

This makes the local state model:

```text
prepared decision row  ->  one append-only terminal transition
                         -> applied | failed | compensated
```

The prepared decision row remains immutable.

## CLI surface

A terminal transition can be recorded with:

```bash
anonsync_core \
  --ledger path/to/ledger.sqlite \
  --ledger-effect-idempotency-key <64-hex-key> \
  --ledger-effect-terminal-state applied \
  --ledger-effect-result-sha256 <64-hex-digest> \
  --ledger-effect-transition-reason "downstream worker confirmed application"
```

The command fails closed for unknown prepared keys, duplicate terminal transitions, unsupported states, and invalid result digests.

## SQLite/WAL schema change

SQLite/WAL advances to schema v5:

- `backend_profile.schema_version = 5`
- `backend_profile.entry_material_version = anonsync-replay-ledger-entry-v4-effect-transition-chain`
- `effect_transition_metadata` is required.
- `effect_transitions` is required.
- `effect_transitions_key_unique` is required.

Read-only snapshot verification now requires and verifies the transition tables. It rejects unexpected schema objects, malformed transition metadata, duplicate transitions, unknown prepared effect references, unsupported terminal states, invalid result digests, and transition hash-chain mismatches.

## What this fixes

Rev0626 creates durable local evidence that a prepared effect reached a terminal downstream state without rewriting decision history. It also makes snapshot/restore verification cover terminal effect evidence because the existing read-only verifier is now responsible for transition-chain integrity.

## What this does not fix

This is not yet a full outbox worker. The cube still does not apply external effects itself, retry delivery, poll downstream truth, compensate automatically, coordinate broker transactions, or provide distributed exactly-once semantics. Rev0626 gives the local ledger a truthful terminal-state recording surface that those later pieces can use.

## Validation

Rev0626 adds `--selftest-ledger-sqlite-effect-transition`. The test seeds a prepared effect, records an `applied` transition, reloads the ledger, inspects persisted transition rows, rejects duplicate/unknown/invalid transitions, verifies snapshots with the transition chain present, and rejects a tampered transition hash.
