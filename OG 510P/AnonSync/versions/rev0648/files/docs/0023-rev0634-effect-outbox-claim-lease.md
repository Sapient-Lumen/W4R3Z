# Rev0634 — effect outbox claim leases

## Mission fit

Rev0634 turns the rev0633 outbox from a passive reservation table into a local relay handoff primitive. A prepared authorization decision now becomes:

1. a durable prepared ledger row;
2. an atomically inserted `reserved` outbox row;
3. a bounded `inflight` worker claim with a unique claim id and attempt count;
4. a signed terminal transition that closes the same outbox row as `applied`, `failed`, or `compensated`.

This is still not a production worker, but it removes the main local excuse for unsafe worker behavior: a relay no longer needs to mutate `effect_outbox` by hand to decide which row it owns.

## Code changes

- SQLite schema version is now 10.
- `effect_outbox` keeps dispatch/lease evidence: `dispatch_attempts`, `worker_claim_id`, `worker_id`, `claimed_at_epoch`, `lease_expires_at_epoch`, `last_result_digest_sha256`, and `updated_at_sequence`.
- `run_sqlite_effect_outbox_claim_command()` opens the ledger, verifies current metadata, starts `BEGIN IMMEDIATE`, selects one claimable row, writes the inflight lease, and emits a claim report.
- Claim reports use `anonsync-sqlite-effect-outbox-claim-v1`.
- Claim ids are derived from length-prefixed claim material, not newline-concatenated strings.
- Stale inflight rows are reclaimable after `lease_expires_at_epoch <= now_epoch`; non-expired inflight rows are skipped.
- Signed terminal transitions update outbox rows from either `reserved` or `inflight`, preserving claim metadata if a worker had claimed the row first.
- Pending reports use `anonsync-sqlite-effect-pending-report-v5-outbox-claim` and include both reserved and inflight work.
- The read-only verifier rejects malformed inflight metadata, invalid claim ids, partial worker metadata, and terminal rows inconsistent with effect-transition evidence.

## Audit/refactor performed

The focused refactor was deliberately narrow. Instead of creating a new registry layer, rev0634 tightened one high-risk source file around the actual state machine:

- effect outbox states are centralized as constants;
- claim material has one domain constant;
- report format/version strings were advanced once and asserted in selftests;
- schema exact-column checks now include claim metadata;
- in-memory counters now distinguish reserved, inflight, and terminal outbox rows.

The broader structural problem remains: `sqlite_replay_ledger.cpp` and `reporting_selftests.cpp` are still too large and mixed-purpose. Splitting them should follow the next adapter/reconciliation work rather than precede it.

## Validation added

- `--selftest-ledger-sqlite-effect-outbox-claim` seeds two prepared effects, claims them under separate workers, verifies no fresh inflight double-claim, reclaims a stale lease, rejects a control-character worker id, closes an inflight row with a signed terminal transition, and verifies terminal preservation of worker claim evidence.
- `tools/validate_rev0634_effect_outbox_claim.py` checks the packaged binary, v29 capability manifest, schema v10 columns, initial reserved coverage, claim reports, stale reclaim behavior, malformed worker rejection, tampered inflight metadata rejection, and v28 downgrade rejection.
- CTest now includes 23 tests.

## Residual risk

The dangerous gap has moved forward, not disappeared. The cube can reserve and claim work locally; it still cannot perform, observe, or reconcile a real downstream effect. The next revision should add a tiny adapter harness/state machine that consumes a claimed row, invokes an idempotent simulated downstream operation, writes a signed terminal transition, and reconciles on restart from both local outbox state and downstream status.

Worker leases are not distributed locks. They are local SQLite evidence. A process can crash after dispatch and before terminal evidence. Downstream consumers must remain idempotent, and later production design must bind effect ids to actual operation keys at the target service.
