# AnonSync rev0869 audit summary

## Finding

Rev0869 closes the first durable replica-operation cutpoint. One SQLite owner
now jointly owns exact canonical operation bytes, ordered parent edges, local
counter mapping, deterministic evidence/head/visible projection, persisted
resource policy and counters, and lightweight sender outbox intents for one
folder and one local actor epoch.

The database is not trusted through summaries alone. Every public operation
loads exact bytes, restores the pure replica model, rederives all redundant
rows, checks foreign keys and exact schema SQL, and verifies domain-separated
digests. Every mutation then repeats the complete attestation over the staged
state before COMMIT.

## Severe defects found and corrected during the audit

1. A name-only schema scan missed an unrelated-name trigger attached to a
   replica table. The final exact inventory covers both object name and
   attachment target, with hard count and SQL-byte ceilings.
2. Old-state attestation alone did not detect a connection-local TEMP trigger
   silently mutating staged rows. Every mutating cutpoint now reloads and
   re-attests immediately before COMMIT; mismatch rolls back.
3. Operation/evidence set digests did not bind the exact local
   counter-to-operation map under same-dot substitution. A separate
   `local_operation_digest` is now part of the cutpoint seal.
4. The first crash probe used raw `fork()`. The complete gate rejected it. The
   probe now uses the pinned self-exec boundary and dependent inventories were
   updated to eight fresh-image campaigns rather than weakened.
5. Per-destination operation copies were replaced by one canonical row plus
   lightweight destination intents.

## Invariants defended

- local mint counter, canonical operation, projection, and all destination
  intents commit or roll back together;
- outbox pressure is checked before mint, so rejection cannot burn a counter;
- exact remote duplicate and capacity block are durable no-ops;
- persisted policy survives restart and changes only through explicit fit-
  checked replacement;
- one ACK removes one exact destination/operation intent only;
- all SQL is bound to `main`, and exact schema attachment is attested;
- canonical bytes, operation ID, parent rows, stored charges, evidence states,
  heads, visible rows, local mapping, outbox, metadata, and seals agree;
- a process death after outbox insertion but before commit restores the old
  generation with no partial publication; and
- two writers serialize one contiguous local counter authority.

## Validation result

- GCC Debug all-target build: passed, followed by a no-work rebuild.
- CTest registry: 172/172 across 171 parallel and one isolated serial test.
- Registered audits: 52/52.
- Focused GCC, Clang `-Werror`, and GCC ASan/UBSan: 6/6 executables and
  2,144/2,144 checks in each lane.
- Owner stress: 20/20 final-source iterations, 56 checks each.
- Owner audit: 28/28; raw-fork audit: 11/11; self-exec audit: 36/36;
  allocator-fault audit: 101/101.
- Clang analyzer: three pure production replica translation units under default
  interprocedural analysis with zero diagnostics; owner and owner test under
  bounded shallow analysis with zero diagnostics. The timed-out default owner
  analysis is not claimed.

## Scope and nonclaims

The owner is a correctness scaffold. It performs O(history) restore and full
projection rewrite, is not wired into the integrated product, and has no
point-read sender lease, retry scheduler, authenticated actor/membership
protocol, keyed local seal, payload path, causal stability, compaction, physical
resource accounting, or privacy model. Its unkeyed cutpoint digest is not
protection against an attacker able to rewrite and rehash the local database.

See `SQLITE_REPLICA_CUTPOINT_AUDIT_rev0869.md` for the complete analysis.
