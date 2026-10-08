# Rev0633 effect outbox boundary

## Priority chosen

Rev0632 identified the most important unfinished product risk as the missing authorization-to-effect boundary. SQLite could persist a `prepared` effect decision and later record a signed terminal transition, but nothing in the durable schema represented a dispatchable item reserved for execution. A crash after authorization but before any external work would be recoverable only through a report that re-derived pending effects from ledger rows. That was useful evidence, but it was not yet a state machine a worker could consume.

Rev0633 therefore avoids another restore registry or manifest ceremony and adds a concrete local reservation primitive: `effect_outbox`.

## New invariant

For every prepared SQLite ledger entry, there must be exactly one outbox row with the same `effect_idempotency_key`, `prepared_sequence`, and `prepared_entry_hash`.

A clean prepared row has:

```text
outbox_state = reserved
dispatch_attempts = 0
last_result_digest_sha256 = ""
updated_at_sequence = prepared_sequence
```

A terminal effect transition must update the same row to one of:

```text
applied
failed
compensated
```

The terminal outbox row must preserve the transition result digest and the effect transition sequence that performed the update.

## Code changes

- SQLite backend profile schema version advances from 8 to 9.
- `create_schema()` creates `effect_outbox` with foreign keys back to `ledger_entries(effect_idempotency_key)` and `(sequence, entry_hash, effect_idempotency_key)`.
- `run_commit()` inserts the prepared ledger row and the `reserved` outbox row in the same transaction.
- `mark_effect_terminal()` appends the signed transition row and updates the matching `reserved` outbox row in the same transaction. The update must affect exactly one row.
- `reload_chain_or_throw()` verifies outbox coverage and terminal consistency during normal ledger open.
- `verify_open_sqlite_ledger_snapshot_readonly()` performs the same checks before pending reports and restore-oriented inspection.
- Pending reports advance to `anonsync-sqlite-effect-pending-report-v4-outbox` and enumerate only rows whose outbox state is `reserved` and that have no terminal transition.
- Runner reports now expose `ledger_effect_outbox_reserved` and `ledger_effect_outbox_terminal` counters.
- Capability manifest format advances to exact v28.

## Audit/refactor performed

`sqlite_replay_ledger.cpp` still needs a real split, but rev0633 removes one cause of drift: scattered schema/material/report literals. The SQLite schema version, ledger material version, commit protocol, effect states, outbox format, and transition material version are now centralized constants near the top of the module and reused by profile verification, schema creation, manifest checks, and report generation.

The line-count problem remains. The largest two files still dominate review effort:

- `reporting_selftests.cpp`
- `sqlite_replay_ledger.cpp`

A future refactor should split production SQLite persistence from report rendering, restore helpers, transition-intent verification, hostile corpus generation, and selftest key material. Rev0633 intentionally limited the refactor to a safe constant consolidation because the session priority was the risky missing boundary.

## Validator additions

`tools/validate_rev0633_effect_outbox_boundary.py` now checks that:

- the packaged binary is rev0633 and stale rev0632 packaged binaries are absent;
- capability format is exact v28 and parent lineage is rev0632;
- schema v9 is present;
- every prepared ledger row has exactly one clean `reserved` outbox row after fixture execution;
- pending reports declare the outbox format, expose reserved/terminal counts, and only list `reserved` rows;
- raw terminal transitions still fail closed;
- signed transitions still require trust-profile digest pins and ledger-instance binding;
- a valid signed transition updates the outbox row to the terminal state/result/sequence;
- deleting an outbox row causes read-only pending-report verification to fail;
- downgraded v27 capabilities are rejected.

## Residual risk

This is still not a production effect worker. Missing pieces include:

1. A narrow production API that accepts already transport-authenticated context and an operator-selected configuration handle.
2. A worker contract for claiming/reserving outbox rows without concurrent double-dispatch.
3. Attempt accounting and backoff policy for `dispatch_attempts`.
4. Reconciliation against authoritative downstream state.
5. Real idempotent downstream adapters.
6. Sender proof-of-possession instead of fixture HMAC proof material.
7. Operator-owned authenticated trust/configuration.
8. Independent log witnesses or signed external checkpoints.

Rev0633 makes the local reserve-before-effect invariant durable. It does not claim delivery, compensation, distributed consensus, or external exactly-once effects.

## Recommended next revision

Rev0634 should either:

- implement a single local worker claim/complete API over `effect_outbox`, including `inflight` or lease semantics and recovery from stale claims; or
- implement the narrow production authorization API that prevents requests from selecting trust roots, clocks, proof secrets, contracts, ledger backend, or restore behavior.

The first option continues the reserve-before-effect path. The second option attacks the still-missing ingress production boundary. Either would be more valuable than another capability registry expansion.
