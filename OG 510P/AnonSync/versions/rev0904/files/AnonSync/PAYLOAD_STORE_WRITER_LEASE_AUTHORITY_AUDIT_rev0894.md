# Payload-store writer lease and directory-cursor authority audit — rev0894

## Heart of the mission

AnonSync is an authority-accounting system before it is a file copier. Exact
validated evidence and live owned capabilities decide whether bytes may become
content authority, whether an operation may be attempted, and whether a visible
effect may be acknowledged. A digest, counter, directory listing, process-local
mutex, or successful syscall is not authority by itself.

Rev0893 introduced a deliberately simple durable content-addressed sender store.
Its complete scan and hash was a useful correctness oracle, but its aggregate
entry and byte limits were exact only inside one process invocation. Two
cooperative processes could each scan the same pre-mutation namespace, each see
remaining capacity, and then publish different digest-named payloads. The final
namespace could therefore exceed the configured aggregate budget even though
both local preflights had passed.

Rev0894 gives the immutable folder-identity marker a second, narrowly scoped
role: it is the stable lock anchor for a fail-fast shared/exclusive cooperative
lease. The lease never substitutes for folder identity, root attestation,
content hashing, create-new publication, or final reconciliation. It only makes
one exact full-store capacity decision indivisible with respect to other owners
that use the same protocol on a filesystem whose observed `flock(2)` behavior
provides independent-open exclusion.

That role cannot safely be retrofitted under the rev0893 identity generation:
a rev0893 process would accept the folder while ignoring every lock. Rev0894
therefore advances the immutable marker to generation v2 and includes the exact
lease protocol in its bytes. A legacy v1 marker causes a mutation-free,
explicit offline-migration failure. A legacy process sees the v2 basename as
unknown. This is a durable mixed-version fence, not an automatic migration
protocol.

## Severe defect found during the lease work

### Directory-offset defect

The first rev0894 regression test did not fail on locking. It exposed an older,
more severe scan defect in rev0893.

The store retained a root directory descriptor as part of
`SyncDirectoryAuthority`. To enumerate the namespace, rev0893 duplicated that
descriptor with `F_DUPFD_CLOEXEC` and passed the duplicate to `fdopendir()`.
That looked like independent RAII ownership, but `dup(2)`/`fcntl(F_DUPFD*)`
create another descriptor referring to the same open file description. The file
offset is shared. A directory stream created from the duplicate can therefore
advance the retained root's directory offset while `readdir()` walks entries.

The practical failure was silent and authority-relevant:

1. clean bootstrap scanned an empty root and consumed the retained directory
   cursor;
2. bootstrap then published the exact folder-identity marker;
3. the next scan duplicated the same retained open file description;
4. enumeration began at end-of-directory; and
5. the exact marker was falsely reported absent.

More dangerous variants could omit payload entries from aggregate accounting or
produce a summary of only a suffix of the namespace. The bug was not a
cryptographic failure; it was an ownership-model error caused by treating a
file descriptor number as if it implied an independent open file description.

Rev0894 now reopens the canonical absolute root path into a new
`SyncDirectoryAuthority`, compares path, attestation digest, directory-resolution
capability, and live mount-namespace identity against the retained authority,
and only then duplicates that short-lived independent root into `DIR*` ownership.
`readdir()` may consume the temporary scan cursor, but it cannot alter the
long-lived owner's cursor. Both the temporary scan authority and the retained
authority are re-proved at the final cutpoint.

This is also an audit lesson for the wider cube: descriptor duplication is
ownership duplication, not observation-cursor independence. Any code that hands
a `dup` of a seekable descriptor to an API that changes offsets should be
reviewed for shared-open-description effects.

The audit also found the same privileged descriptor-duplication implementation
copied inside atomic publication and the payload store. Rev0894 moves that bridge
behind `SyncDirectoryAuthority` and returns one move-only
`SyncDirectorySharedOpenDescriptionLease`. Its name and internal contract make
the shared-offset/status-flag property explicit. Descriptor-relative `openat`
and `fstatat` users may consume that result; a directory-stream observer may not
mistake it for an independent cursor and must first reopen and attest the root.
This removes two security-boundary copies without pretending that centralized
lexical shape is itself a semantic proof.

## Lease authority sequence

The lock protocol is versioned as
`anonsync:sync-replica-file-payload-store-flock-lease:v1` and is included in the
snapshot digest domain and the v2 identity marker. Changing the protocol
therefore changes both derived evidence and the durable generation seal rather
than silently reinterpreting an old summary or sharing capacity with a
lock-ignorant writer.

### Shared observation lease

A snapshot performs the following sequence:

1. re-prove the retained root and exact folder binding;
2. reopen and attest an independent matching root authority;
3. independently open the exact immutable folder-identity marker;
4. verify private regular-file type, owner, mode, device, link count, exact
   folder-binding bytes, stable descriptor contents, and stable directory name;
5. acquire `LOCK_SH | LOCK_NB` on that marker;
6. independently open the marker a second time and require a nonblocking
   `LOCK_EX` attempt to fail with the platform's lock-conflict result;
7. re-prove the locked marker and root after that capability probe;
8. pass the move-only lease itself into the protected scanner; the raw scanner
   remains reachable only from explicit pre-marker bootstrap;
9. perform the full bounded namespace scan and hash while the shared lease is
   held;
10. re-prove that the directory name still identifies the exact inode carrying
    the lock, rather than an identical replacement marker;
11. construct the immutable public snapshot, content inventory, and canonical
    snapshot digest while the shared lock remains live; and
12. re-prove the exact locked marker and retained root at the final return
    cutpoint before releasing the lease.

Multiple cooperative snapshots may coexist. A cooperative writer cannot pass
its exclusive lease frontier until every shared observation is complete.
Content selected from a returned snapshot is still reopened and rehashed after
outbox claim selection; the lease does not pretend to freeze bytes for the
snapshot's lifetime.

### Exclusive mutation lease

A payload put performs this sequence:

1. validate the candidate byte count and compute its full SHA-256 name;
2. re-prove the retained root and exact folder marker;
3. acquire `LOCK_EX | LOCK_NB` on an independently opened, exactly verified
   marker;
4. independently reopen the marker and require a nonblocking `LOCK_SH` attempt
   to conflict;
5. pass the exact exclusive lease witness into one complete bounded scan and
   hash;
6. re-prove the locked marker inode and retained root after the scan;
7. classify an exact existing digest or check entry, aggregate-byte, transient-
   entry, and transient-byte capacity against that scan;
8. re-prove the exact lock anchor immediately before publication;
9. publish through the existing descriptor-relative create-new, file-sync,
   no-replace rename, and directory-sync owner;
10. re-prove the lock anchor before interpreting an existing object, after a
    successful publication, and before any ambiguous-failure reconciliation;
11. reconcile an ambiguous local failure against the exact intended bytes;
12. re-prove the anchor again at every exact, conflicting, or absent terminal
    classification; and
13. release the lease only when the result is exact or the operation has failed.

The mutation path no longer calls `snapshot_or_throw()` merely to obtain its
private scan results. It consumes the internal `ScannedPayloadIndex` directly.
This removes construction of a public snapshot, a duplicate vector of digest
strings, a content inventory, and a snapshot digest from every put. The full
scan remains; only redundant allocation and hashing of derived metadata were
removed.

## Why the runtime exclusion self-proof exists

A successful `flock()` return is not enough to claim the semantics required by
this owner. Implementations differ across local and network filesystems, and
some locking facilities collapse ownership at process scope. The store needs
locks associated with independently opened file descriptions: an independent
open in the same process must conflict with the already-held opposite-mode
lock.

After acquiring the requested lock, rev0894 opens the marker independently and
tries the opposite lock with `LOCK_NB`. If that attempt succeeds, the store
immediately fails closed and performs no protected scan or publication. If it
fails for an unexpected reason, the store also fails closed. Only the expected
would-block conflict promotes the primary lock to local runtime authority.

The lease retains the exact root descriptor, locked marker descriptor, marker
inode observation, root attestation, and folder-binding bytes. The ordinary
scanner requires that move-only witness and re-proves it before and after the
directory traversal. Snapshot construction and every mutation terminal path
perform another proof at their final authority cutpoint. This closes a
split-lock frontier in which an identical marker could replace the pathname
while a scan, derived snapshot construction, publication, or reconciliation was
in progress: valid bytes alone are insufficient unless the final result still
connects to the inode carrying the live lock. Only the clean bootstrap path,
which necessarily precedes creation of any stable lock anchor, may invoke the
raw scanner.

This is a capability probe, not a universal filesystem certification. It proves
the specific conflict observation made at that moment on that marker and mount.
It cannot establish behavior across every host, reboot, kernel, network
partition, or server failover.

## What this corrects

For cooperative owners using this implementation on an observed-compatible
filesystem:

- no two puts can independently spend the same aggregate entry or byte budget;
- a snapshot cannot observe the namespace while a cooperative mutation is
  between its capacity preflight and publication reconciliation;
- multiple snapshots can coexist without blocking one another;
- contention is explicit and fail-fast rather than silently blocking an event
  loop or worker indefinitely, and it is reported through a typed busy error so
  retry policy never depends on diagnostic text;
- repeated scans start from an independent directory cursor;
- marker validation has one implementation shared by scanning and locking;
- the v2 marker binds the lease protocol and refuses legacy v1 roots without
  mutation, preventing silent mixed-version capacity races;
- every ordinary scan requires the exact live lease witness and re-proves the
  locked marker name after traversal and again at its public terminal cutpoint;
- every put result and reconciliation classification remains bound to the exact
  live lock inode at its final return or throw frontier;
- lease contention has a typed shared-observation/exclusive-mutation
  classification, so retry scheduling never depends on diagnostic text;
- directory descriptor duplication now has one move-only RAII implementation
  whose type explicitly says that the open-file-description offset and status
  flags remain shared; and
- the mutation path avoids redundant public-snapshot construction.

The full-scan oracle is still O(total indexed bytes), because every digest-named
payload is reopened, bounded, frozen, hashed, namespace-reproved, and included in
aggregate accounting. That cost is intentional until a separately designed
indexed owner can be differentially checked against this oracle.

## What this does not prove

`flock(2)` is advisory. A noncooperating same-UID process, privileged process,
or malicious host can ignore the lock and mutate directory entries or file
contents. Rev0894 therefore does not claim hostile-writer security, mandatory
locking, sandbox isolation, filesystem integrity, or malicious-administrator
resistance.

The protocol also does not claim:

- equivalent semantics on every NFS, SMB/CIFS, FUSE, distributed, or unusual
  filesystem;
- lock survival as durable evidence across process death, reboot, server
  restart, network partition, or lease recovery;
- fairness or starvation freedom among contending processes;
- asynchronous waiting, wake scheduling, or bounded retry backoff for a busy
  store;
- atomicity between the filesystem content store and the SQLite outbox;
- reachability ownership or garbage collection;
- free-space reservation, disk-quota ownership, or protection from unrelated
  filesystem consumers;
- a production-scale indexed catalog;
- at-rest encryption, key lifecycle, anonymity, unlinkability, endpoint hiding,
  or traffic-analysis resistance; or
- Windows parity.

Rolling coexistence with rev0893 or any other payload-store owner that ignores
the lease protocol is durably refused, but rev0894 does not perform the offline
migration itself. Operators must stop every older writer, independently verify
the legacy full-scan state, and deliberately advance the identity generation.
The generation fence prevents silent coexistence; it does not prove that a
human-directed migration was complete or that no hostile writer remains.

The folder marker remains an exact immutable binding, not a signed provenance
statement. Its lock role is local coordination only.

A noncooperating actor can still replace the marker *between* operations and
start a new lock lineage on a new inode. Rev0894 detects replacement while one
of its own protected scans is live; it does not create a signed or
administratively immutable lock anchor across hostile namespace mutation.

## Fork and lifecycle cautions

On Linux, `flock` locks are associated with an open file description and are
released when all descriptors referring to that description are closed.
Descriptors duplicated before or inherited through `fork()` can therefore
extend a lock's lifetime. This owner does not expose its marker descriptor and
marks it close-on-exec, but a caller that forks while an operation is active can
still inherit process state. The broader project already treats active authority
crossing a process boundary as a serious ownership event; this store should not
be used across `fork()` without an exec or an explicit higher-level process
policy.

The implementation deliberately relies on final close rather than a separate
unlock call. The move-only RAII lease owns one independently opened marker file
description, and every exception path destroys it.

## Audit and refactor findings for the wider cube

The directory-offset failure suggests a targeted repository audit:

- search every `dup`, `F_DUPFD`, and `fdopendir` composition;
- distinguish descriptor lifetime ownership from open-file-description state;
- review shared offsets for regular files, directories, event streams, and any
  callback/API that may seek;
- require independent reopen where an observation must begin at a known
  cutpoint; and
- add repeated-observation tests, because one first scan can pass while poisoning
  all later scans.

The rev0894 inventory found exactly one production `fdopendir()` owner in the
active source tree: this payload-store scanner. The source audit now makes that
inventory explicit so a future directory-stream owner cannot enter production
without a fresh open-file-description review. Test-only `/proc/self/fd`
enumeration remains outside this production ownership claim.

The audit also found two copied private implementations of directory-authority
descriptor duplication: one in atomic publication and one in the payload
store. Besides being wasteful, both returned a generically named “verified
descriptor lease,” which made it easy to mistake duplicated lifetime ownership
for an independent observation cursor. Rev0894 defines the move-only internal
`SyncDirectorySharedOpenDescriptionLease` interface in
`sync_directory_authority_internal.hpp` and implements its single bridge in the
directory-authority library. Its API and comments state the shared-offset and
shared-status-flag semantics, retain capability and mount evidence, own failure
cleanup through RAII, and leave independent observations responsible for an
independently opened and re-attested root. Atomic publication and the payload
store now consume the same implementation; neither retains a copied friend
shim.

Repeated stress also exposed an unrelated but release-relevant waste source in
`sync_atomic_file_publication_test.cpp`: the parent created the cross-process
start-gate pathname before writing its complete payload, so a child could
truthfully observe an in-progress file and report a false product failure. The
gate now uses a private staging name, file synchronization, single-consumption
close, and `renameat2(RENAME_NOREPLACE)` before visibility. The source audit
requires that ordering, turning the stress discovery into a durable harness
invariant rather than dismissing it as flakiness.

The payload store remains a deliberately conservative reference owner. The next
performance correction should not weaken it. A separate SQLite or append-only
catalog can record digest, size, and reachability under the same exclusive
mutation lease, but every generated scenario should periodically compare that
catalog against the full-scan oracle and quarantine disagreement.

A second high-value direction is production composition: make one bounded
sender/listener executable use the causal SQLite, durable payload, TLS, receiver
effect, and terminal-receipt owners as its sole authority. More isolated proof
machinery without a shipped caller risks optimizing an assurance island rather
than the product.

## Primary sources consulted

- Linux `flock(2)`: advisory shared/exclusive locks, nonblocking conflict,
  open-file-description ownership, close and fork behavior, and network-
  filesystem notes: https://man7.org/linux/man-pages/man2/flock.2.html
- Linux `dup(2)`: duplicated descriptors refer to the same open file description
  and share file offset/status flags: https://man7.org/linux/man-pages/man2/dup.2.html
- Linux `open(2)`: each successful open normally creates a new open file
  description, while duplicated descriptors refer to the existing one:
  https://man7.org/linux/man-pages/man2/open.2.html
- POSIX `fdopendir()`: the directory stream assumes ownership of the supplied
  descriptor: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fdopendir.html
- FreeBSD `flock(2)`: advisory lock semantics on another supported POSIX family:
  https://man.freebsd.org/cgi/man.cgi?query=flock&sektion=2

The conclusion that `fdopendir()`/`readdir()` on a duplicated directory
file descriptor can consume the retained cursor follows from the POSIX stream
ownership rule plus Linux's documented shared open-file-description offset.
