# Payload-use lease and snapshot reader fence — rev0977

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Bounded retained history eventually requires reclaiming immutable
payload objects, but a collector must never rename or unlink an object while a
cooperating sender, apply pass, or restore operation is consuming the exact
inode. Rev0977 closes that descriptor-lifetime seam without adding retention
policy, garbage collection, or unlink authority.

## Concrete authority defect

Rev0976 binds the payload store's complete committed and transient namespace,
but its complete snapshot was intentionally move-only metadata rather than a
long-lived store lease. A later call could reopen a committed payload from that
snapshot without reacquiring the current store-wide reader fence. Returned
payload descriptors also carried bytes and frozen metadata but no cooperating
cross-process lifetime witness.

That was acceptable only while the authoritative payload namespace was
append-only. It was not a safe foundation for a collector:

- an already-open file descriptor does not keep its pathname present;
- `rename(2)` leaves open descriptors usable;
- `unlink(2)` removes the name while the inode remains alive until the final
  descriptor closes; and
- therefore an open descriptor by itself cannot tell a namespace mutator to
  defer removal.

A future collector could otherwise take its own namespace observation, remove a
candidate, and let an existing sender continue reading an unlinked inode. The
sender might finish, but restart, accounting, diagnostics, and exact
reobservation would disagree about whether that payload was still retained.

## Two-tier cooperative protocol

Rev0977 introduces the stable protocol identifier:

```text
anonsync:sync-replica-file-payload-use-flock-lease:v1
```

The protocol has one non-negotiable lock order:

```text
reader / selector
    global payload-store identity inode: LOCK_SH | LOCK_NB
    exact committed payload inode:       LOCK_SH | LOCK_NB
    release global lock at selection cutpoint
    retain exact-inode lock with returned descriptor

namespace mutator / future collector
    global payload-store identity inode: LOCK_EX | LOCK_NB
    exact candidate payload inode:       LOCK_EX | LOCK_NB
    rename or unlink only while both remain held
```

The short global lease establishes the current store identity and prevents a
writer from crossing selection. The descriptor-owned exact-inode lease then
survives the global cutpoint, including across `fork(2)` and rename, until the
last descriptor for that open file description closes. A mutator that first
holds the global exclusive lease prevents new selectors, then uses the exact
inode's exclusive lease to discover every already-issued cooperating
descriptor.

No code upgrades a held lock in place, and no reviewed path acquires the inode
before the store identity. That fixed order avoids introducing a lock-order
cycle.

## Complete-snapshot reader fence

A complete snapshot now retains the exact store identity basename, identity
payload, and observation durability needed to re-enter the live reader fence.
Both byte-access paths perform the following current cutpoint:

1. re-prove the rooted directory authority;
2. acquire the current shared store lease for the snapshot's exact identity;
3. open the digest-named regular file beneath the retained root;
4. validate private-file shape, size, and any replacement digest;
5. acquire the shared exact-inode payload-use lease;
6. re-prove the digest pathname;
7. re-prove the store lease and rooted authority; and
8. either return the locked descriptor or copy the requested bounded range.

This applies to
`open_payload_for_operation_or_throw()` and
`copy_payload_range_for_operation_or_throw()`. Whole-payload copying delegates
to the bounded range path. A snapshot issued before an incompatible identity
migration cannot silently reopen through an obsolete marker: its current shared
lease acquisition fails closed.

Targeted one-digest access already retained a short current store lease through
its pathname proof. Rev0977 adds the same exact-inode shared lease before that
lease and the root are finally re-proved, then moves the locked descriptor into
`SyncReplicaFilePayloadStoreOpenedPayload`.

## Bounded descriptor lifetime

`SyncReplicaFilePayloadStoreOpenedPayload` owns only:

- the selected descriptor;
- its frozen metadata and digest identity; and
- the shared exact-inode payload-use lease attached to that descriptor's open
  file description.

It does not retain the global store lease, a cleanup capability, or scheduler
authority. Product consumers keep it only through local byte publication or
restore. Range sending copies bytes while both short leases are held, returns a
bounded byte string, and performs network I/O only after those leases are gone.
The public contract explicitly forbids retaining an opened payload across
network waits, sleeps, or unrelated service work. This avoids turning a slow
Tor or I2P peer into a store-wide writer blockade.

The adjacent folder-owner comments were corrected accordingly. They no longer
say that a complete snapshot depends solely on an append-only store. They name
the current shared-reader reentry, descriptor-owned inode lease, and the exact
future collector order.

## Existing mutators now consume the protocol

The two current payload-name removal operations now exercise the exclusive side
of the protocol:

- exact corrupt-payload quarantine holds the global exclusive store lease,
  opens and validates the authoritative digest inode, acquires its exclusive
  payload-use lease, completely hashes the current corrupt bytes, then performs
  the rooted no-replace rename and final durability/reproof sequence; and
- exact diagnostic-quarantine release holds the same global exclusive lease,
  opens and validates the exact quarantine inode, acquires its exclusive
  payload-use lease, then performs the rooted unlink and final absence proof.

These operations are useful executable collectors for the lock protocol even
though diagnostic quarantine remains semantically separate from user versions
and future retention collection.

## Runtime proof

The focused payload-store regression proves all relevant boundaries:

- a retained complete snapshot cannot reopen a payload or copy a range while an
  exclusive mutation batch owns the current store fence;
- a returned descriptor blocks an independently opened exclusive inode lease;
- closing the returned descriptor releases that same-process lease;
- an exact integrity failure is installed after a noncooperating in-place byte
  overwrite;
- quarantine fails with the typed `ExclusiveMutation` busy result while the
  issued descriptor remains live;
- the authoritative and quarantine namespaces remain unchanged on contention;
- the selected descriptor is inherited through an ordinary fork, the parent
  closes its copy, and quarantine still fails while only the child retains the
  shared open-file-description lease; and
- after the child closes the final descriptor, the same quarantine operation
  succeeds and preserves the exact corrupt bytes outside payload authority.

This cross-process oracle matters: Linux `flock(2)` locks are associated with an
open file description, duplicate descriptors and forked children refer to the
same lock, independently opened descriptors conflict, and the lock is released
only after the final descriptor closes.

## Audit/refactor finding: source-byte hygiene

The first edited regression accidentally contained one literal NUL byte inside
a character literal. GCC accepted that source, but a release must not depend on
compiler tolerance for hidden control bytes. The NUL was replaced with the
ordinary textual `\\0` spelling. The structural audit now reads every required
rev0977 source and record as UTF-8 and independently rejects embedded NUL bytes.
This check is release hygiene, not a C++ semantic proof.

## What this proves

For reviewed Linux-local product paths, every newly selected committed payload
byte source now crosses the current shared store identity fence. Any returned
payload descriptor retains a cooperating shared lease on the exact inode. A
namespace mutator following the fixed global-then-inode exclusive order cannot
rename or unlink that inode until every cooperating selected descriptor has
closed, including an inherited descriptor held by another process.

This closes the specific rev0976 `opened sender descriptor` removal race as a
future writer-fence mechanism. It also makes the existing quarantine rename and
release unlink obey the same protocol that a collector must later use.

## What this does not prove

Rev0977 deliberately does **not** claim any of the following:

- complete external transient-root authority;
- that an active pass which has not yet opened a payload is durable or pinned;
- receiver, mutation, publication, range, or scheduler roots beyond the
  reviewed descriptor and existing global-lease boundaries;
- retention count, byte, age, grace, quota, ENOSPC, or restore-loss policy;
- a crash-durable mark or collection intent;
- collection quarantine, restart repair, or final payload unlink;
- protection from noncooperating same-UID or privileged writers;
- mandatory-lock semantics;
- identical `flock(2)` behavior on NFS, SMB, FUSE, overlay, or every other
  filesystem; or
- a complete filesystem support matrix.

The deletion-free retention response therefore continues to report
`opened_sender_transient_roots_bound:false`,
`external_transient_root_model_complete:false`,
`writer_fenced_collection:false`, and `reclaimable_authority:false`. The new
protocol is a necessary collector primitive, not permission to reinterpret the
existing mark as deletion authority.

## Linux semantics researched

Primary references used to check the protocol shape:

- `flock(2)`: locks attach to open file descriptions, are inherited through
  `fork(2)`, conflict across independently opened descriptors, and are released
  at the final close: <https://man7.org/linux/man-pages/man2/flock.2.html>
- `unlink(2)`: removing the last name does not destroy an inode while an open
  descriptor remains: <https://man7.org/linux/man-pages/man2/unlink.2.html>
- `rename(2)`: open file descriptors are unaffected by rename, and
  `RENAME_NOREPLACE` supplies the existing no-replace namespace primitive:
  <https://man7.org/linux/man-pages/man2/rename.2.html>

Those pages also reinforce the nonclaims: `flock` is advisory on ordinary local
Linux filesystems, and remote filesystems can emulate or alter its behavior.
Supported deployment filesystems need live qualification before the product can
make a broad portability promise.

## Next safe edge

The next collection step should not jump directly to deletion. It should:

1. inventory every active pass, receiver, publication, mutation, range, and
   restore lifetime that can name a committed payload before opening it;
2. decide which roots become durable pins and which are excluded by holding the
   global exclusive writer fence across the relevant mark-to-quarantine
   cutpoint;
3. define owner-visible per-share count, byte, age, grace, quota, ENOSPC, and
   restore-loss policy;
4. persist one identity-bound exact mark plus policy record;
5. move candidates through a distinct collection quarantine under global and
   exact-inode exclusive leases;
6. restart, completely reobserve every persistent and transient root, and
   revalidate the exact quarantined inode and bytes; and only then
7. unlink one object proven absent from all roots.

Diagnostic corruption quarantine must remain separate from user history and
collection staging.

## Validation

Exact rev0977 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in a final serial replay (129.22 seconds), and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 613 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 448 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 339/339 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed serially in 144.09 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 613-check payload-store suite in 13.33 seconds at 484,272 KiB peak RSS, the 448-check folder-owner suite in 39.78 seconds at 1,453,628 KiB peak RSS, and the 155-check local-control suite in 1.44 seconds at 105,116 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0976 parent SHA-256 matched 44d90e8b74fffe16239ea0e6b1516a215950d7bc1d558344e7c64b5189a7f566 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,498,367 bytes with SHA-256 d4ad87ef909365a2af2515451da83248a94680bce23f0056dfff0f3c8db0b8b6. Validation excluded overlapping or stale shared-tree launchers, interrupted wrappers, divergent unsealed branches, and every result not bound to the exact final active projection.
