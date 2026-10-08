# AnonSync rev0791 — replay-row truth, referential restart proof, and one semantic owner

Prepared from the supplied and independently verified parent archive
`AnonSync-rev0790-2026.07.15.00.55-exactscalar-nulproof-typefence-rowtruth.zip`. Its SHA-256 is
`089c8a78b24b9d91f71c1707950125598d0858e5f3da92becfb12a537737387f`, and the release-package verifier passes all 25 parent checks.

## Mission

AnonSync's heart is **evidence-authorized convergence**: replicas may converge
only after the boundary that owns an invariant verifies that observations carry
exactly the authority required for a state transition. A table declaration,
successful query, valid-looking digest, or enabled SQLite pragma is not proof
that durable rows still satisfy the protocol after tampering, corruption,
restore, or restart.

## Severe durable-state promotion defect corrected

The integrated `ingress_sender_replay_cache` was schema-checked but its rows
were never semantically scanned during ordinary reload or read-only snapshot
verification. `PRAGMA integrity_check` does not report foreign-key errors, and
enabling `foreign_keys=ON` is not a retrospective validation of rows created or
modified while enforcement was disabled.

The preserved parent reproducer creates a legitimate replay reservation,
disables foreign-key enforcement on a tampering connection, and rebinds it to
nonexistent prepared sequence 999. Rev0790 then promotes the database:

```text
orphaned_replay_row_reload_accepted=true
```

Rev0791 runs `PRAGMA foreign_key_check` and a full replay-row scan on both trust
paths. The same database now fails closed:

```text
orphaned_replay_row_reload_accepted=false
rejection=sqlite-wal replay ledger load foreign_key_check reported a durable reference violation
```

## Refactor: one replay-record semantic owner

`src/persistence/ingress_sender_replay_record.*` is a pure, independently linked
C++ boundary. It owns:

- exact format and lowercase SHA-256 grammar;
- bounded token, principal, and nonce fields;
- C0/DEL rejection for principal evidence;
- replay-window and future-skew policy;
- difference-based signed-time comparisons that cannot overflow;
- prepared sequence/hash/idempotency-key syntax;
- exact comparison with the independently reconstructed prepared tuple; and
- one length-delimited nonce identity shared by staging and restart checks.

The ledger remains responsible for exact SQLite extraction, row traversal,
foreign-key verification, finding the reconstructed prepared entry, and
cross-row uniqueness. It rejects duplicate replay keys, duplicate protocol
nonce identities, and multiple replay reservations for one prepared effect.
Reload now clears the ephemeral staged nonce set before rebuilding durable
authority, fixing a stale in-memory rejection bug when one object is reloaded.

## Verification economics

The focused semantic proof compiles 4 Ninja actions, 2 first-party translation units,
417 lines, and 19,479 bytes. The full core requires
47 actions and 53,632 first-party lines: **128.61×** the focused
line exposure. The integrated restart/restore proof still exposes
53,242 first-party lines, which records rather than conceals the remaining
monolith cost.

## Validation

Required gates passed:

- GCC 14 Debug/`-Werror`, full build and **49/49 CTest**;
- focused replay-record proof, **118 checks × 20/20**;
- integrated restart/restore proof, **20 checks × 20/20**;
- focused GCC ASan/UBSan, **5/5**;
- Clang 17 `-Wconversion -Wsign-conversion -Werror`, **5/5**;
- GCC 14 `-O3 -DNDEBUG` with conversion warnings and `-Werror`, **5/5**; and
- nine deterministic authority audits, all exit zero.

The active implementation projection is `anonsync-active-implementation-projection-v2`:
**101 files / 14,810,992 bytes**, SHA-256
`f44d95cc6ad823d59006626afa7c3a4b19a37e742b4cd9973683f65e805aff53`.

## Explicit proof boundary

This revision proves shape, exact SQLite type/bytes, freshness, uniqueness,
foreign-key validity, and equality to one reconstructed prepared-entry tuple. It
does **not** prove the replay row's original provenance. Replay evidence is not
yet included in the prepared decision's cryptographic hash material. An attacker
who can replace a row with entirely valid-shaped evidence and rebind it to a
different existing prepared tuple may still produce a state that passes these
checks. Likewise, deletion of an old row cannot currently be distinguished from
legitimate replay-window pruning. Correcting those properties requires a
versioned ledger material/schema change, not a stronger ad hoc row parser.

The new 4096-byte principal ceiling is intentionally fail closed. A legacy row
above that limit is rejected rather than truncated or silently migrated.

No integrated/full-core sanitizer completion is claimed. The focused owner
passed, but the integrated sanitizer build remained in the large core archive
and did not produce a runnable test. Total untrusted snapshot file size, row
count, VDBE work, wall time, and SQLite heap also remain incompletely bounded.

## Highest-value next work

1. Bind a canonical replay-evidence digest and pruning policy into a new
   prepared-entry material version, with migration and downgrade tests.
2. Build the fault-injecting VFS plus protocol state oracle for crash-cut
   database/filesystem outcomes.
3. Finish a versioned untrusted-snapshot resource profile using runtime limits,
   progress/interrupt budgets, page/file ceilings, and heap accounting.
4. Continue extracting invariant owners from the replay ledger and 24k-line
   domain unit, and add an executable convergence/adversary model.
