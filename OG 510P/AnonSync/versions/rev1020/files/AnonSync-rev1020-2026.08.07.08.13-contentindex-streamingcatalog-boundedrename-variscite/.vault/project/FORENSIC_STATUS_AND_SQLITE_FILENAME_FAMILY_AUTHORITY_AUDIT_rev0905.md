# Forensic status and SQLite filename-family authority audit — AnonSync rev0905

## Executive conclusion

The product's `status` command was semantically wrong even when it returned
correct data. It opened the same mutable owners used by operational commands,
which meant an observation could reconcile durability, recover or checkpoint
SQLite state, create or remove sidecars, and synchronize payload files or their
directory. In an evidence-authorized system, that is not a harmless
implementation detail: the observer could create the cutpoint it later claimed
to observe.

Rev0905 introduces a distinct forensic authority. Every SQLite store is opened
through a private descriptor-rooted read-only VFS, exact current-schema
observers execute under deferred read transactions, WAL bytes are copied into a
bounded anonymous file, the WAL index stays in connection-local memory, and
persistent byte-changing callbacks are denied. Payload status uses a shared
lease but performs no identity bootstrap and no durability synchronization.
Adversarial process tests compare exact bytes and namespace metadata before and
after status and exercise hostile sidecars, read-only mutation attempts, WAL
capture, file-control escape, and registration lifetime.

The sanitizer lane then exposed a separate severe defect in the VFS shim. The
wrapper passed `std::string::c_str()` to the delegated Unix VFS. SQLite's public
`sqlite3_filename` type is string-compatible at its visible address, but it may
also carry hidden database/journal/WAL and URI material. The Unix VFS retains
that pointer after `xOpen` and later uses SQLite filename/URI helpers. ASan
reported a heap-buffer-overflow during WAL shared-memory initialization because
the ordinary string lacked the required representation. Rev0905 now constructs
one filename family with `sqlite3_create_filename()`, caches its three official
views, and owns it until all delegated files close and the VFS is unregistered.

## Mission fit

AnonSync's heart is durable, bounded causal convergence in which exact evidence
and explicit capabilities are authority. A status report is a projection. It may
summarize an already-authorized state, but it may not gain write authority merely
because the easiest path to a summary is to reuse a mutable owner. A VFS path is
also not just text: it is a capability-bearing object with a contract defined by
the implementation it is composed with.

The revision follows two rules:

1. **Observation must not repair, publish, checkpoint, or synchronize the state
   it reports.** Unexpected recovery work fails the observation.
2. **A delegated interface must receive the exact object representation and
   lifetime its contract requires.** Similar visible bytes are not a substitute.

## Previous behavior and risk

### Mutable status

The earlier one-shot status surface instantiated operational SQLite owners and a
normal payload store. Those paths intentionally own mutable policy: they may
configure WAL/synchronous behavior, recover schema state, reconcile file and
parent durability, create required markers, or clean sidecars. Reusing them made
status convenient but conflated two different authorities.

Consequences included:

- a status call could update main, WAL, SHM, journal, or directory metadata;
- SQLite close/checkpoint behavior could alter retained WAL state;
- an empty payload root could acquire an identity marker through inspection;
- payload and directory `fsync` calls performed maintenance work during a read;
- failures could be diagnosed only after the observer had already changed the
  evidence surface.

### Invalid delegated filename storage

The descriptor-rooted wrapper mapped logical names to retained
`/proc/self/fd/<dirfd>/<basename>` strings. It correctly kept the string bytes
alive, but lifetime alone was insufficient. The SQLite VFS contract declares
`xOpen`'s second parameter as `sqlite3_filename`, and SQLite documents that this
value may be passed to `sqlite3_filename_database()`,
`sqlite3_filename_journal()`, `sqlite3_filename_wal()`, and the URI-parameter
helpers. `sqlite3_create_filename()` exists to create storage safe for all of
those operations.

The delegated Unix VFS retained the ordinary string pointer. Later WAL setup
called a URI helper on it. Under ASan, the helper inspected memory beyond the
`std::string` allocation and produced a heap-buffer-overflow. The normal registry
passed because the invalid access depended on allocator layout; this is exactly
why the sanitizer lane is a required independent boundary.

Adding one or several NUL bytes would not be a valid repair. That would imitate
an internal layout without proving its prefix, suffix, alignment, ownership, or
future compatibility.

## Forensic SQLite design

### Explicit access mode

`SqliteDescriptorRootedVfsAccess` distinguishes `ReadWriteExisting` from
`ReadOnlyExisting`. Operational callers retain the compatibility overload, while
new observers must choose read-only authority explicitly. Registration still
requires an existing approved main inode, retained parent descriptor, current
process and mount namespace, and exact main/journal/WAL/SHM family names.

The product connection opens with `SQLITE_OPEN_READONLY | SQLITE_OPEN_NOFOLLOW`
and verifies that SQLite reports the main schema as read-only. `query_only`
remains enabled. The observer uses an exact current-schema transaction and does
not invoke mutable schema migration or policy ownership.

### Lock-capable implementation descriptor without write callbacks

SQLite's Unix WAL implementation needs a lock-capable main descriptor to obtain
the exclusive lock used for a connection-local WAL index. An `O_RDONLY`
descriptor cannot provide that lock on the supported Unix path. The wrapper
therefore lets the delegated Unix VFS hold an `O_RDWR` descriptor for the exact
already-existing main inode while preserving the public connection as read-only.

That implementation detail does not grant the wrapper write semantics:

- `xWrite` and `xTruncate` return `SQLITE_READONLY` for persistent files;
- main/journal deletion is denied and persistent SHM deletion is never used;
- persistent `xSync` is a no-op because no deployment bytes can have changed;
- the public method table is version 1, so SQLite cannot call `xShmMap`,
  `xShmLock`, `xShmUnmap`, `xFetch`, or `xUnfetch` through the connection;
- mutating or capability-expanding file controls are rejected;
- direct file-pointer and journal-pointer controls do not reveal the delegated
  Unix `sqlite3_file` object;
- URI filenames, anonymous disk files, delete-on-close, dynamic extension
  loading, lock-proxy paths, and ambient temporary names remain denied.

This is a narrow capability composition, not a claim that hostile code in the
same process cannot use unrelated system calls or descriptors.

### Anonymous WAL snapshot

A read-only WAL database ordinarily needs a usable WAL and WAL-index path. Rather
than granting persistent sidecar mutation, the VFS creates an anonymous Linux
`memfd` and copies the retained WAL into it.

The copy protocol:

1. inspects the `-wal` name relative to the retained parent descriptor without
   following symlinks;
2. requires an absent name or a single-linked regular file;
3. opens the exact name read-only with `O_NOFOLLOW`;
4. binds the opened descriptor to the named identity and enforces a 256 MiB
   ceiling;
5. copies exact bytes with bounded fixed storage;
6. rechecks both opened and named observations after the copy;
7. rejects a WAL that changes, disappears, is replaced, appears during an
   absent capture, or exceeds the bound;
8. verifies that the destination is an anonymous regular file with link count
   zero.

SQLite receives a private I/O object over that descriptor. It may write,
truncate, or logically delete the private copy while parsing/recovering its
view. Those operations never resolve a deployment pathname. Exclusive locking
keeps the WAL index in heap memory, so a persistent `-shm` file is neither opened
nor created.

This is a stable bounded observation of one WAL file, not an atomic snapshot of
all stores. Concurrent mutation is detected where the before/after evidence
changes; ambiguous state fails closed.

### Payload observation

`SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect` uses the existing
identity-bound shared lease and exact payload-name/digest checks. It does not:

- create or adopt a folder identity marker;
- publish payload bytes;
- call `fsync` on marker or payload files;
- call `fsync` on the root directory.

The durability behavior is now explicit in the internal scan/lease helpers
rather than being an incidental consequence of using the snapshot API.

## Filename-family repair

Each VFS registration now owns:

- one `sqlite3_filename descriptor_filename_family` produced by
  `sqlite3_create_filename()` for the descriptor-rooted main, rollback-journal,
  and WAL paths; and
- three cached `sqlite3_filename` views returned by the corresponding official
  database/journal/WAL accessor functions.

Registration verifies that every returned visible path exactly matches the
precomputed descriptor-rooted path. The normal `xOpen` delegate and the pre-open
main-file reader both use these views. The forensic anonymous WAL never delegates
a persistent filename. A shared-memory name is mediated through the live main
file and is not independently placed in the three-entry family.

Destruction order is deliberate:

1. re-prove process and mount-namespace context;
2. require the wrapped-file count to be zero;
3. unregister the private VFS;
4. close the anonymous WAL descriptor, if any;
5. free the filename family with `sqlite3_free_filename()`;
6. clear cached views and close the retained parent descriptor.

The family cannot be freed while the Unix VFS may retain one of its views.
Ordinary strings remain useful for exact comparisons and diagnostics but are no
longer passed as delegated SQLite filename objects.

## Audit/refactor changes

- The database-open source audit advanced to v18 and requires family creation,
  all three official views, delegated use in both open paths, exact registration
  lifetime, and header documentation. It rejects plain `mapped.c_str()`
  delegation.
- Read-only status paths are factored as explicit owner observers instead of
  boolean flags leaking through mutable constructors.
- Payload scans carry a named observation-durability policy, removing hidden
  `fsync` work from read-only snapshots while preserving reconciliation for
  operational calls.
- The Python process harness now closes SQLite readers before removing temporary
  namespaces, so a passing mutation check cannot be contaminated by leaked
  handles.
- The private VFS exposes only reviewed file-control operations and validates
  non-null arguments before the delegated Unix implementation can dereference
  malformed input.
- Persistent mmap is removed from the forensic surface by method-table shape,
  not just by setting an mmap-size pragma.

## Validation

The final release evidence records exact toolchain and log hashes. At the point
of this audit:

- clean GCC 14 and Clang 17 Debug registries: **226/226** each;
- focused strict GCC 14 ASan/UBSan lane: **4/4**, including the product CLI and
  direct descriptor-rooted process-authority test that traversed the former
  overflow path;
- direct descriptor-rooted SQLite process authority: **103/103**;
- database-open policy source audit v18: **37/37**;
- all bundled-profile and package-policy adversaries are registered in both
  complete CTest registries.

Manifest, extracted-directory, and ZIP results are bound under
`REVISION_EVIDENCE/rev0905/` before publication.

## Explicit nonclaims and residual risk

- The status result is not an atomic cross-store snapshot. Stores are observed
  independently and may represent nearby but different moments.
- Cooperative SQLite and payload locks can delay or be delayed by writers.
  Non-mutating does not mean zero concurrency influence.
- The lock-capable main descriptor is safe only because every reviewed
  byte-changing wrapper path is denied. This is not sandboxing against hostile
  in-process code, injected libraries, ptrace, root, or raw block access.
- Linux procfs, `statx` mount identity, and `memfd_create` remain platform
  requirements for this implementation.
- The 256 MiB WAL bound is a deliberate operational ceiling; larger state is
  refused rather than silently truncated.
- A privileged actor racing every namespace observation is outside the claimed
  transaction model; the implementation detects reviewed substitutions but is
  not hostile-root proof.
- Read-only forensic mode does not make invalid or torn SQLite state valid. It
  fails rather than repairing persistent evidence.
- No anonymity, unlinkability, endpoint-hiding, or traffic-analysis claim follows
  from local storage correctness.

## What should change next

1. Add one bounded supervisor that turns the current one-shot authorities into a
   restartable scan/exchange/transfer/effect/repair loop with explicit
   quarantine and operator-visible cutpoints.
2. Define a multi-store observation envelope so status can report per-store
   sequence/time evidence and distinguish exact agreement from merely adjacent
   observations.
3. Keep the SQLite 3.53.4 update isolated, verify official source identities,
   inspect upstream VFS/WAL changes, and rerun every process, crash, corruption,
   sanitizer, and package lane.
4. Add externally signed builder provenance and reproducible-build comparison;
   in-archive hashes establish self-consistency, not builder authorization.
5. Design cross-store durable intents or consolidate operations that actually
   require one atomic commit; separate WAL databases do not become a transaction
   merely because status can inspect them together.
6. Specify the anonymity and metadata threat model before naming or transport
   behavior is treated as a privacy property.

## Primary-source research checked 2026-07-26

- SQLite filename construction and lifetime API:
  https://www.sqlite.org/c3ref/create_filename.html
- SQLite `sqlite3_filename` contract and filename/URI helpers:
  https://www.sqlite.org/c3ref/filename.html
- SQLite VFS interface:
  https://www.sqlite.org/vfs.html
- SQLite WAL and read-only WAL requirements:
  https://www.sqlite.org/wal.html#readonly
- SQLite file-control opcodes:
  https://www.sqlite.org/c3ref/c_fcntl_begin_atomic_write.html
- Linux anonymous file descriptors:
  https://man7.org/linux/man-pages/man2/memfd_create.2.html
- Linux process-associated record-lock lifetime:
  https://man7.org/linux/man-pages/man2/fcntl_locking.2.html
- SQLite warning about closing a separate descriptor for a locked inode:
  https://www.sqlite.org/howtocorrupt.html#posix_close
