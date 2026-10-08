# Rev0826 audit

## Severe defect corrected

Rev0825's reset command rendered canonical receipt bytes and performed a safe
create-new preflight before destructive authority, but that check retained only
a pathname fact. After SQLite committed, the writer reopened the path. A local
reproducer renamed the verified parent directory, created a replacement at the
same pathname, and showed:

```
replacement_received=1
pinned_parent_received=0
```

The receipt could therefore be redirected after authorization but before
publication. No file was overwritten, yet the evidence was delivered to a
namespace object that had never been verified. This was an authority error,
not merely a race inconvenience.

## Refactor

`SyncPreparedImmutableJsonPublication` is a move-only, single-use capability.
Preparation normalizes the destination, owns the exact payload and label,
proves the final name absent, opens the parent component-by-component without
following symlinks, and retains the exact parent descriptor. The reset CLI now
creates this capability before `reset_sqlite_replay_ledger()` and consumes it
after the durable SQLite outcome.

Publication consumes the capability before effects, verifies that the current
parent pathname still resolves to the retained directory, rechecks final-name
absence, and then delegates to the existing private-temp/write/fsync/typed
`renameat2(RENAME_NOREPLACE)`/directory-fsync protocol. A replacement parent is
denied before temp reservation. Payload mutation by the caller is impossible
because bytes are owned by the capability.

The initial fork fence used raw PID equality. The structural audit exposed the
overclaim, so the final source binds the capability to the existing
PID-plus-fork-lineage process-incarnation token. The publication owner depends
only on that primitive, not on SQLite state or storage interpretation.

## Executable proof

- prepared immutable publication: 27/27;
- existing atomic publication corpus: 38/38;
- pure outcome state: 24/24;
- caught/crash/race cutpoints: 149/149;
- descriptor-bound unlink authority: 12/12;
- reset owner: 67/67;
- canonical reset documents: 18/18;
- CLI integration oracle: 380/380;
- structural audits: 206/206;
- focused prepared/receipt repeat: ten consecutive cycles;
- Clang 17 warning-as-error focused graph: 3/3; and
- GCC 14 ASan/UBSan focused graph: 3/3 with leak detection enabled.

The final 110-test inventory passed in three non-overlapping final-source ranges:
22/22, 26/26, and 62/62. Two attempts at one aggregate invocation were
terminated by the cloud command ceiling at test 35 while unrelated temporary
build streams contended for the container. Test 35 then passed alone in 1.2
seconds. A single uninterrupted 110-test execution is deliberately not claimed.

## Package and lineage audit

The exact rev0825 ZIP and extracted source pass their own verifier 25/25 and
21/21. The corrected standalone patch applies cleanly to that parent and
reproduces all 189 active files byte-for-byte. The active
source delta is 9 files, 807 insertions, and 51 deletions.
The first patch draft omitted the new untracked test; exact patch replay caught
that packaging defect and the sealed patch was regenerated with intent-to-add.

Repeated unrelated temporary-root work was quarantined. The release source is
the private absolute root `/tmp/as826-authority-8X6qxyHq/work/AnonSync` and was compared against the sealed parent
immediately before evidence generation. No VFS experiment, generated Python
cache, build product, or alternate branch is in the active change surface.

## Residual risks

This is not a cross-resource atomic transaction. SQLite can commit while receipt
publication later fails, which is why exact recovery remains necessary. A
hostile same-UID writer is not isolated and can race after any observation. NFS
error semantics are not claimed. Windows retains a path-based implementation
and was not executed. Post-fork use is not an async-signal-safe C++ API for a
multithreaded parent. Full-project/bundled-SQLite sanitization, arbitrary power
loss, distributed convergence, confidentiality, anonymity, metadata hiding,
key lifecycle, and secure erasure remain unproved.
