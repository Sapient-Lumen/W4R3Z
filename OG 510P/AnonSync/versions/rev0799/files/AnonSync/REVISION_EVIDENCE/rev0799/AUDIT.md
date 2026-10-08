# Rev0799 architecture audit — finite interpretation and snapshot-consistent reports

## Boundary

Input is an open connection whose database bytes and, for sealed snapshots,
exact byte/page geometry have already been promoted. Output is either verified
replay-ledger state under finite resource authority or one typed, value-free
denial reason. The same capability also spans pending-report verification and
projection.

## Invariants

1. Every policy dimension is nonzero and no greater than its reviewed hard cap.
2. Geometry-derived policy uses saturating arithmetic and can only tighten.
3. The progress callback owner has stable identity and cannot be copied/moved.
4. The callback is installed before any hostile SQL preparation or execution.
5. The first denial is sticky and interrupts SQLite with `SQLITE_INTERRUPT`.
6. SQLite interruption is translated back into the typed budget denial.
7. The callback is detached before the connection is closed.
8. Schema, integrity, foreign-key, profile, metadata, ledger, replay,
   transition, and outbox scans consume one lifetime budget.
9. Retained cross-table state has one ordered owner and no duplicate map key.
10. The integrity verdict is exactly one `ok` row followed by `SQLITE_DONE`.
11. Pending-report verification and projection share one explicit read
    transaction and one budget.
12. Parallel staging tests inspect only directories created by their process.
13. The focused proof links neither the core monolith nor OpenSSL.

## Corrected failure modes

A one-GiB file ceiling did not bound SQLite VM execution or verifier container
retention. Rev0799 adds callback, row, decoded-text, retained-text, and elapsed
ceilings and proves their exact edges.

The pending report previously combined verification from one implicit snapshot
with rows from a later implicit snapshot. A concurrent writer could therefore
separate reported rows from the heads/counts that supposedly authorized them.
Rev0799 holds one read transaction across both phases; the permanent writer-race
proof demonstrates snapshot pinning.

## Refactor assessment

The fused `SnapshotPreparedEffectState` map replaces multiple attacker-sized
hash containers. Exact schema verification plus `integrity_check` owns PRIMARY
KEY/UNIQUE index correctness; `foreign_key_check` separately owns referential
integrity. This removes redundant re-proofs without weakening the durable
contract and avoids attacker-selected hash-table behavior.

Fresh focused build graph:

- six Ninja actions;
- two first-party C++ translation units;
- 709 first-party lines;
- links pinned SQLite;
- does not link `anonsync_core_lib` or OpenSSL.

## Residual risks

- SQLite heap/page-cache and C++ allocator/object overhead are not exactly
  represented by retained-text counters;
- one scalar can allocate up to `SQLITE_LIMIT_LENGTH` before post-extraction
  cumulative accounting rejects it;
- blocked filesystem I/O is not preempted by the progress callback;
- JSON construction after database close has no separate output-byte budget;
- in-process enforcement cannot contain a SQLite/VFS/libc/kernel memory-safety
  defect;
- long read transactions can delay WAL checkpoint progress;
- confidentiality, anonymity, metadata leakage, and key lifecycle remain outside
  this boundary.

## Recommended continuation

Move hostile snapshot interpretation into a disposable worker with OS resource
limits and a narrow typed result protocol. Then pair that worker with a
fault-injecting VFS crash-cut oracle and an executable convergence outcome model.
