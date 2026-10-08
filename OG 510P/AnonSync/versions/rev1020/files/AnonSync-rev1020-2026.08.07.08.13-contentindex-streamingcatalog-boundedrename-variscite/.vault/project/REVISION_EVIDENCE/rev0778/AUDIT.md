# Rev0778 deep audit — SQLite retained-mutex authority and repository hygiene

## Scope followed

The review traced every direct production `sqlite3_mutex_enter()` and
`sqlite3_mutex_leave()`, every path that retains the database mutex beyond one
stack frame, copied transaction authority, explicit COMMIT/ROLLBACK, destructor
rollback, lease move operations, `sqlite3_close()`/`sqlite3_close_v2()` behavior,
SQLite client-data ownership, and package contents.

## Finding 1: thread affinity was a convention, not a capability

Rev0774 retained the recursive connection mutex from typed BEGIN through exact
finalization. That closed same-handle transaction replacement but created an
unexpressed lower-level invariant: only the entering thread may leave the
mutex. Before rev0778:

- a live connection-authority lease could be moved or destroyed elsewhere;
- a live typed transaction could reach rollback/release elsewhere; and
- copied authority could block behind an entry held recursively by its owner.

SQLite explicitly defines foreign-thread `sqlite3_mutex_leave()` as undefined.
Serialized connection mode orders API calls; it does not transfer ownership of
an already-entered mutex.

### Correction

A monotonic `uint64_t` incarnation is allocated once per exact C++ thread
lifetime. `std::thread::id` is not used because its value can be reused. Every
retaining owner captures the incarnation. Foreign observation returns false
before any SQLite-owned state is read. Foreign explicit finalization throws.
Noexcept move or destruction on a foreign thread terminates before cleanup.

## Finding 2: same-thread close could manufacture a dangling mutex pointer

The prior guard retained a raw `sqlite3_mutex*` without independently fencing
the lifetime of its `sqlite3*` owner. The connection mutex is recursive, so the
owner thread could call `sqlite3_close_v2()` while an outer entry remained live.

In bundled SQLite 3.53.3:

- `sqlite3Close()` recursively enters `db->mutex` at line 188637;
- it invokes all connection client-data destructors at lines 188671–188677;
- it marks the connection zombie and calls
  `sqlite3LeaveMutexAndCloseZombie()` at lines 188679–188682; and
- the terminal path leaves and frees `db->mutex` at lines 188840–188842.

Without a close fence, the outer AnonSync owner could later leave freed storage.
Normal builds may appear to survive this undefined behavior, making it more
dangerous than an immediate crash.

### Correction

`sync_sqlite_mutex_capability.cpp` installs the versioned client-data sentinel
`anonsync.sqlite.retained-mutex-capabilities.v1`. Acquisition increments its
count while the connection mutex is held; release decrements the count before
leaving the retained entry. Client-data destruction or replacement with a
nonzero count fails stopped.

The count is **not exact authorization**. Multiple nested owners share it, so it
proves only close-order lifetime. Exact authority remains in the noncopyable
owner, thread incarnation, connection incarnation, authorizer generation, and
transaction generation. Copied transaction authority is also gated by an
atomic active bit before it may inspect the shared sentinel.

## Ordering proof

The corrected release order is:

```text
validate lease/proof shape
  -> compare immutable thread incarnation
  -> inspect SQLite-owned lifetime sentinel
  -> decrement and consume this owner's sentinel pointer
  -> sqlite3_mutex_leave(exact retained entry)
```

Foreign-facing observation checks the thread before dereferencing the sentinel
or asking SQLite for its database mutex. This matters after a lifetime violation:
the thread incarnation lives in the C++ owner, while the sentinel is owned by
the potentially closing SQLite connection.

## Refactor result

The 171-line `sync_sqlite_mutex_capability.cpp` module now owns thread lifetime
and connection-close lifetime only. Policy, authorizer callback generations,
transaction permits, and SQL remain in their existing invariant owner. A single
lease-shape validator replaced duplicated constructor, destructor, and move
checks and proves that an empty lease has all three fields empty.

All nine direct production SQLite mutex calls remain in
`src/sync_sqlite_connection_authority.cpp`. The only direct production
connection-client-data owners are that file and the new capability module.

## Executable and static evidence

- connection authority: 98/98 checks;
- 100 consecutive authority runs: 9,800/9,800 checks;
- live lease, fenced and unfenced transaction, sentinel replacement, and zombie-close fail-stop death tests;
- foreign close blocks and then succeeds after normal release;
- full Debug CTest: 40/40, repeated three times;
- GCC Release, GCC ASan/UBSan, and Clang focused tests: 2/2 each;
- mutex capability audit: 63/63;
- transaction-stack audit: 45/45;
- payload transaction audit: 38/38;
- authorizer ownership audit: pass.

## Finding 3: tracked build output had become repository state

Two tracked directories contained 488 generated artifacts totaling 286,095,753
bytes. They included binaries, static archives, object files, compiler probes,
CMake caches, Ninja databases, and stale CTest output. This is a severe source
integrity problem, not merely storage waste:

- search and inventory tools see stale generated copies;
- reviewers can execute binaries that do not match current source;
- compiler paths and host details leak into handoffs;
- checksums and package review are dominated by irreproducible products; and
- every revision pays the transfer and extraction cost again.

Rev0778 deletes both tracked build roots and adds `.gitignore`. The complete
removed inventory is in `audit/REMOVED_TRACKED_BUILD_ARTIFACTS.tsv`; a JSON
summary records count, bytes, roots, and largest items.

## Remaining debt

The transaction-stack audit still reports 95 legacy raw transaction controls
outside peer-ingress production. They are inventory, not authority proof.
`src/sync_domain.cpp` is 24,523 lines, `reporting_selftests.cpp` is 4,498,
`sqlite_replay_ledger.cpp` is 4,340, and peer-ingress lifecycle is 3,794. The
correct decomposition boundary is durable aggregate and transition ownership,
not a mechanical line-count split.

The runtime still accepts raw `sqlite3*` at public support boundaries. A
connection actor/strand should structurally own open, task dispatch,
transaction generation, and close. Fork/process incarnation and power-loss VFS
behavior remain separate unproved boundaries.
