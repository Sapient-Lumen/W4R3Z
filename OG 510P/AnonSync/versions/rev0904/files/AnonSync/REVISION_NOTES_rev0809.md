# AnonSync rev0809 revision notes

## Executive finding

AnonSync's heart remains an evidence-authorized convergence kernel: observations
become authority only after the recipient that owns the invariant verifies the
exact evidence required for the transition. Rev0809 applies that rule to the
daemon owner lock.

The prior lock was useful coordination evidence but not a fencing token. Its
epoch was selected by the caller, and downstream checkpoint mutators did not
verify the current owner generation in their own transactions. SQLite ensured
there was only one writer at a time, but writer serialization alone could not
distinguish an authorized successor from a paused stale predecessor.

Rev0809 makes the database mint a monotonic owner generation and makes mutation
recipients validate the exact generation before acting. This is the classic
shape of a fencing protocol: generation is minted at acquisition, propagated
with each operation, and rejected by the recipient after a successor exists.

## Reproduced safety trace

The unsafe trace in the source parent was:

```text
A acquires descriptive owner row using caller-selected epoch
A pauses beyond lease expiry
B replaces the expired row
A resumes
A calls a checkpoint mutator that has no exact current-owner capability
recipient writes because it never compares A with B
```

SQLite's single-writer rule only orders A and B; it does not reject A. The
required invariant is stronger:

> After generation B has been durably minted, no operation carrying generation
> A may mutate guarded checkpoint state or publish a guarded file effect.

The focused SQLite test now runs a concrete A→B transition and proves stale A is
rejected in an immediate recipient transaction without producing the guarded
effect.

## Database-minted generation

Acquisition now occurs under the caller-owned immediate transaction. The focused
runtime boundary:

- loads the exact owner row;
- validates row state, identity geometry, canonical lock ID, times, and signed
  SQLite integer range;
- invokes a pure acquisition policy;
- mints generation `1` when no row exists or exactly `stored + 1` after an
  expired/released generation;
- rejects takeover of a live row, clock regression, malformed state, and
  generation exhaustion;
- inserts or compare-and-replaces on the prior generation;
- reloads the written row and proves every field before returning authority.

The owner generation is no longer derived from `initial_worker_lease_epoch` or
any other caller-selected sequencing value.

## Exact capability

The installed public header introduces:

```cpp
struct SyncSessionCheckpointDaemonOwnerCapability final {
    std::string session_id;
    std::string daemon_id;
    std::string worker_id;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
};
```

Every field participates in authorization. An all-empty capability represents
unowned operation where policy permits it. A partially populated capability is
invalid and fails closed. A live durable owner row requires a complete exact
match.

The lock ID is recomputed from the canonical length-prefixed identity/generation
tuple. This catches row/capability drift and binds the generation to its owner
identities. The digest is binding evidence, not secrecy or process isolation.

## Recipient-side validation

`require_recipient_write_authority_or_throw` first proves the caller is already
inside a SQLite write transaction using `sqlite3_txn_state(db, "main") ==
SQLITE_TXN_WRITE`. It then reads the durable row on that transaction's snapshot,
recomputes canonical evidence, applies the pure recipient policy, and throws
before mutation if authority is absent, partial, stale, expired, malformed, or
for another session/daemon/worker/generation.

The source audit finds 15 guarded mutation contexts spanning:

- peer-response/workorder claim binding;
- chunk advancement and peer-ingress state transitions;
- materialization and cleanup;
- transfer claim/reclaim/abandon;
- owned execution and terminal reset;
- sidecar review, quarantine, and repair/reset;
- stale staging artifact repair; and
- daemon/scheduler/recovery paths that reach those recipients.

The important property is placement: these are not orchestration preflights.
Each check is in the recipient write transaction that contains the state change.

## Filesystem effect reservation

Two paths can publish or remove filesystem artifacts outside SQLite:

- staged-byte/materialization publication; and
- stale sidecar/staging artifact repair.

They now enter an immediate database write transaction, verify the owner on that
write snapshot, perform the filesystem effect while retaining the writer
reservation, and commit after the effect. A compliant takeover using the same
database cannot acquire its generation in the middle of that interval.

This is not crash atomicity. A process can still crash between file operations,
file/directory sync points, and database commit. The change closes takeover
interleaving, not the larger database-plus-filesystem recovery problem.

## Release is also fenced

A release request is a state transition, not harmless bookkeeping. It now
requires the exact live capability in a write transaction and updates exactly
one held generation. Stale A cannot release B. Release time must not predate
acquisition.

The current compatibility policy allows an empty capability after the durable
row is released. That makes explicit a remaining weakness: ownership is not yet
sticky. A checkpoint that has ever entered owned mode can later accept unowned
mutations after release. Future work should make ownership mode durable and
require an explicit administrative transition to disable it.

## Refactor and ownership

New focused owners:

```text
include/anonsync_sync_checkpoint_owner_fence.hpp
src/sync_checkpoint_owner_fence_policy.hpp/.cpp
src/sync_checkpoint_owner_fence.hpp/.cpp
tests/sync_checkpoint_owner_fence_policy_test.cpp
tests/sync_checkpoint_owner_fence_sqlite_test.cpp
tools/audit_sync_checkpoint_owner_fence.py
```

Dependency direction is one-way:

```text
anonsync_core_lib
  -> anonsync_sync_checkpoint_owner_fence
       -> anonsync_sync_checkpoint_owner_fence_policy
```

The pure policy has no SQLite, filesystem, crypto, clock, or core dependency.
The recipient owner contains row interpretation and focused SQL. The domain
wrapper retains database opening, schema setup, transaction ownership, and
orchestration.

An intermediate implementation placed acquisition/release SQL in
`sync_domain.cpp`, increasing it to 15,632 lines and correctly tripping the
existing 15,400-line scheduler separation budget. The audit was not relaxed.
Those algorithms moved into the focused owner; the final domain unit is 15,308
lines versus 15,329 in rev0807.

## Fail-closed details

The policy rejects:

- zero acquisition or observation time;
- zero lease duration;
- nonportable identities;
- malformed held/released state geometry;
- noncanonical owner-lock IDs;
- acquisition before durable acquisition/release evidence;
- takeover before expiry;
- partial capability population;
- an invented capability when no row exists;
- any capability for a released row;
- absent capability for a live row;
- expired live generation;
- stale or mismatched identity/generation; and
- generation/timestamp values outside SQLite's signed 64-bit integer domain.

The signed-range correction matters because the C++ API uses `uint64_t`, while
SQLite INTEGER storage is signed 64-bit. Treating `UINT64_MAX` as the durable
ceiling would have admitted values the persistence representation cannot
faithfully hold.

## Validation record

- Parent rev0807 package verifier: 25/25.
- GCC 14.2 C++20 Release all-target graph: complete.
- CTest: 86/86 over complete ranges 1–40, 41–70, 71–86.
- Domain model: 592/592.
- Pure owner policy: 28/28.
- SQLite recipient proof: 23/23.
- Owner-fence source audit: 25/25.
- Scheduler source audit: 22/22.
- CLI-advertised versus registered selftests: 38/38.
- GCC 14 and Clang 17 strict changed-unit compile: 8/8 combinations.
- Focused ASan/UBSan: policy 28/28, recipient 23/23.
- Isolated locking diagnostic: 6/6.
- Ledger write-gate: 16 consecutive completed 9/9 runs.

The main graph was built with `-Wall -Wextra -Wpedantic`, not whole-graph
`-Werror`. The four focused changed units were separately compiled with
conversion, sign-conversion, shadow, pedantic, and `-Werror` under both GCC and
Clang.

Leak detection was disabled in the sanitizer lane, bundled SQLite was not
instrumented, and no complete instrumented application is claimed.

## Research interpretation

The design follows the stale-request protection described by Chubby: a lock
sequencer/generation must reach the operation recipient, and the recipient must
reject an old generation. SQLite's transaction documentation supports using an
immediate write transaction to serialize local writers, and `sqlite3_txn_state`
provides a direct check that recipient validation is actually happening inside
a write transaction.

That combination supports a local protocol for cooperating processes sharing
one database/VFS. It does not provide cross-device consensus, trusted time,
Byzantine resistance, or operating-system isolation.

Primary-source references and applied inferences are recorded in
`REVISION_EVIDENCE/rev0809/RESEARCH.md`.

## Remaining severe work

1. **Sticky ownership:** once ownership has been activated, reject empty
   capabilities until a separately authorized mode transition.
2. **Executable state model:** model pause, expiry, acquisition, release,
   mutation, crash, and publication; differentially replay generated traces
   against the pure C++ policy and focused SQLite recipient.
3. **Crash-cut oracle:** enumerate persistence cuts across SQLite, WAL/journal,
   staging, sidecars, receipts, rename, file sync, directory sync, and output.
4. **Convergence algebra:** define operation merge laws, causal dependencies,
   idempotency, retractions, epoch barriers, and conflict semantics.
5. **Hostile database process boundary:** move untrusted SQLite interpretation
   to a disposable, resource-bounded worker.
6. **Privacy and key lifecycle:** distinguish authentication from payload
   confidentiality, metadata leakage, anonymity, forward secrecy, and
   post-compromise recovery.

## Lineage disclosure

The conversation named a rev0808 artifact, but that ZIP was not present or
readable in this cloudtainer when this turn began. Rev0809 is therefore derived
from the complete verifier-clean rev0807 ZIP whose SHA-256 is
`ee63fe28058adfce7a954cfbe200ebd28e728a55cf858f780c6266ea86199991`.
The revision number preserves the conversation sequence; the package does not
claim byte lineage from rev0808.
