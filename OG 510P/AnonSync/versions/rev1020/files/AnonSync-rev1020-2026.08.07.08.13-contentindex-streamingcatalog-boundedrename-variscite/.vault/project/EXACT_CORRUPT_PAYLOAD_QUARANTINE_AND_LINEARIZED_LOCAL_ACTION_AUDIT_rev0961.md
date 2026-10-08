# Exact corrupt-payload quarantine and linearized local-action audit — rev0961

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Rev0960 let an owner force a complete current-byte proof and kept the
daemon alive when a digest-named payload was corrupt. It still stopped one step
short of an operable recovery path: the owner had to locate and edit AnonSync's
private content store by hand. That is not an acceptable ordinary recovery
contract for a replacement product.

Rev0961 adds one deliberately narrow operation:

```text
anonsync_sync quarantine --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

The operation preserves exactly one byte image already proven inconsistent with
its immutable digest name, moves it out of the authoritative payload namespace,
and lets the existing reconciliation path re-admit correct content. It does not
invent a second synchronization algorithm, automatic deletion policy, restore
browser, version history, or garbage collector.

## Product boundary

The new operation is explicit and exact-pair-scoped. It is useful only while the
same retained service has an active payload-integrity witness for the supplied
`expected` and `observed` digests. Request acceptance is process-local scheduling
evidence, not proof that bytes moved. Completion is visible through status and
is not itself proof that the share recovered; readiness returns only after the
ordinary convergence owner has re-proved authoritative bytes and visible state.

The quarantine namespace is bounded at sixteen entries. Its byte budget is the
lesser of the configured active indexed-byte budget and sixteen times the
configured maximum payload size, with checked arithmetic. That fixed frontier
prevents repeated faults from silently becoming an unbounded or disproportionately
large hidden retention product. The retained images are diagnostic evidence only.
An otherwise valid request that reaches the ordinary entry or byte frontier
completes with a typed non-mutating capacity result instead of terminating the
retained daemon. A namespace already beyond its configured frontier remains a
fail-closed structural error during complete observation.
There is no restore operation, retention age, reachability graph, quota eviction,
or crash-safe garbage collection in this revision.

## Exact active-fault authority

`SyncReplicaFilePayloadStore::quarantine_corrupt_payload_or_throw()` first
requires two distinct canonical lowercase SHA-256 digests. A read-only forensic
store cannot invoke it. Before any namespace work, the retained root and exact
minimum-reader identity marker are re-proved.

The supplied pair must match the process-local allocation-independent integrity
witness exactly. A stale observed digest, a different expected digest, or no
active fault returns `ActiveFaultMismatch` without opening a mutation path. If
the active fault has evolved to another observed digest for the same expected
name, the result reports that current observation so the operator can issue a
fresh exact request.

This process witness is intentionally stronger than a filename supplied by the
operator and weaker than durable cross-process authority. Restart discards the
request and process witness; a fresh owner must detect current corruption again
before quarantine is possible.

## Rooted exclusive mutation path

After exact-pair admission, the store reopens a matching descriptor-rooted
authority and obtains the existing nonblocking exclusive mutation lease on the
reader-fenced identity inode. Cooperative contention is typed and leaves the
service, request, listener, route, status socket, and integrity alarm alive for a
bounded retry.

While that lease remains held, a narrow namespace pass:

- validates the exact identity marker and lease observation;
- accepts only canonical authoritative digest names, known internal files, and
  canonical quarantine names;
- rejects symlinks, non-regular entries, wrong ownership, wrong mode, link-count
  changes, mount crossings, and malformed reserved names;
- counts every retained quarantine and checks aggregate quarantine bytes;
- proves that at most one exact destination name exists; and
- excludes quarantine bytes from authoritative payload inventory.

The pass does not hash unrelated authoritative payloads. Complete payload scans
remain the namespace-health and inventory oracle.

## Current-byte pair reproof

The source digest pathname is opened beneath the retained root without following
symlinks. The exact source inode is streamed through SHA-256 while the exclusive
lease remains held, then its pathname and descriptor observation are re-proved.
The outcomes are typed:

- matching expected bytes means `PayloadAlreadyRepaired` and no move;
- a different wrong digest means `ObservedDigestChanged`, refreshes the active
  process witness, and no move;
- an absent source with no exact retained destination means `PayloadAbsent`;
- an absent source with a byte-valid exact retained destination means
  `ExactQuarantineAlreadyPresent`; and
- only the exact requested corrupt image may reach the rename cutpoint.

If the exact retained destination already exists but the authoritative digest
name has reappeared with the same corrupt bytes, the operation rehashes both
images and removes the duplicate authoritative source under the same exclusive
lease. Without that branch, repeated identical corruption would return an
apparently idempotent result forever while complete recovery remained blocked.

A result reports `quarantine_basename` only when an exact retained destination
actually exists. The audit found and corrected an earlier misleading shape that
pre-filled a target-like basename even for stale or non-mutating outcomes.

## Same-inode no-replace preservation

The canonical destination is:

```text
.anonsync-payload-quarantine-v1-<expected64>-<observed64>
```

For a new destination, the owner uses the existing Linux no-replace rename
helper beneath the already opened root descriptor. It does not copy, truncate,
unlink, or overwrite. Before the rename it synchronizes the exact open corrupt
source, so making the new diagnostic pathname durable cannot leave the observed
in-place bytes merely dirty in cache. After the rename it synchronizes the
directory, requires the original authoritative name to be absent, re-proves the
destination pathname, and requires the open file descriptor to name the same
device and inode with the permitted rename metadata transition. The retained bytes
therefore survive as the same file object while becoming unreachable through
content inventory and targeted payload access.

An already-present exact destination is not trusted because its name looks
right. The file is opened, privately typed, fully SHA-256 hashed, synchronized,
and pathname-reproved before `ExactQuarantineAlreadyPresent` is returned. If the source is
absent, that result is non-mutating. If the same corrupt source has reappeared,
the exact source is also fully hashed and then unlinked, the root is synchronized,
and destination identity is re-proved. This closes both a same-user namespace-
tampering shortcut and an idempotent-but-unrecoverable repeated-corruption loop.

The current product's filesystem authority assumes other code running as the
same effective user does not maliciously race the private store. Descriptor,
metadata, lease, name, and hash reproof narrow accidental and cooperative races;
they are not a hostile same-UID isolation mechanism.

## Authority revocation and re-admission

A successful quarantine mutates the authoritative payload namespace without
constructing a new complete inventory. It therefore clears the process
verification generation, disables checkpoint publication capacity, drops active
scrub continuation, and schedules fresh scrub observation. The exact integrity
fault deliberately remains active. Preserving bytes outside authority is not
recovery.

A later complete scan must prove that the digest name is absent or contains good
bytes. The ordinary peer convergence owner can then obtain the missing expected
payload from an authenticated peer and publish it through the existing durable
payload-store mutation path. Readiness returns only after current bytes and the
ordinary folder/catalog/replica convergence cutpoints agree.

Unlike rev0960's direct current-byte snapshot handoff, quarantine necessarily
changes the payload namespace. Re-admitting the expected digest therefore uses
one ordinary mutation-authority full scan. Rev0961 exposes and tests that cost
instead of falsely describing the operation as duplicate-scan-free.

## One linearized local-action observation

Rev0960 combined drain and recheck into one mutex-owned
`SyncLocalStatusSocketActionSnapshot`. Rev0961 extends that same object with at
most one exact `SyncLocalStatusSocketPayloadQuarantineRequest`; it does not add a
parallel command queue or another synchronization model.

The local worker accepts exactly:

```text
quarantine EXPECTED64 OBSERVED64\n
```

The request parser rejects noncanonical digests, equal digests, trailing bytes,
oversize input, and malformed tokenization. The response uses
`anonsync.local-quarantine.response.v1` and is bound to the connected server PID.
The mode-0600 pathname socket and private parent are re-proved through the same
Linux owner-only control boundary as status, drain, and recheck.

One mutex orders all three actions:

- drain is terminal for later mutation requests;
- repeated requests for the same exact pair advance a generation and coalesce;
- a different pair is rejected while one obligation is pending;
- the owner may complete only an observed nonfuture generation;
- completion through generation N cannot erase a same-pair N+1 request; and
- the owner shutdown seal returns the exact combined final snapshot, so an
  accepted pre-seal quarantine cannot disappear from terminal accounting.

The socket worker still owns no payload-store, folder, SQLite, route, or TLS
capability. It records bounded intent and wakes the service owner. The service
owner alone performs the mutation.

## Service scheduling and recovery

The peer-service owner records requested, started, and completed quarantine
generations and the exact pending pair. Quarantine has priority over operator
recheck and automatic integrity recovery because it is the only action intended
to change the corrupt namespace. It may bypass an old integrity retry cutpoint,
but it respects newly observed lease backoff so repeated requests cannot create
a hot lock loop.

A typed terminal store result completes the request generation. Lease contention
does not. `ObservedDigestChanged` updates the service's exact active evidence and
leaves the owner blocked. `Quarantined` or an exact retained image with the
authoritative source absent allows ordinary convergence to proceed, but does
not clear the alarm by itself.
`EntryCapacityExceeded` and `ByteCapacityExceeded` likewise complete the exact
request without mutation while retaining the active alarm, listener, local
control socket, route state, and process. Capacity is therefore an operator-
visible bounded outcome rather than an accidental lifecycle failure.
The listener and control plane remain in the same PID throughout.

Drain, recheck, and quarantine completion are observed again at shutdown before
action admission is sealed. Terminal JSON therefore cannot omit an owner-
completed request simply because a non-local stop reason raced the next loop.

## Status contract

Status advances to `anonsync.peer-service.status.v8`. Live and terminal output
share canonical renderers for both the quarantine status and the typed store
result. The schema exposes:

- requested, started, and completed generations;
- pending exact expected/observed pair;
- bounded retry delay;
- last terminal disposition, current observed digest, retained basename, and
  size when applicable;
- requests observed and coalesced;
- attempts and completions;
- byte images actually preserved; and
- observed-content transitions discovered at the quarantine cutpoint.

An empty `quarantine_basename` renders as null. This distinguishes an intended
target name from an exact destination whose bytes were actually retained and
reproved.

## Mechanical process oracle

The shipping-process regression exercises the complete operator path:

1. Start two configured linked-peer services and converge a real nested file.
2. Hold the exact reader-fenced identity inode under the exclusive mutation
   lease and queue two current-byte rechecks.
3. Prove same-PID typed lease deferral, request coalescing, retained listener,
   retained owner-only socket, and bounded retry.
4. Corrupt the private digest-named payload, release the lease, and require the
   exact integrity alarm and readiness revocation.
5. Change the corrupt bytes again and require exact observed-content transition
   accounting rather than stale pair-scoped persistence.
6. Invoke the shipping `quarantine` CLI with the current exact pair and require
   the PID-bound response and generation.
7. Require the source digest name to disappear and the canonical quarantine name
   to contain the exact wrong bytes, mode 0600, link count one, and the same
   device/inode as the pre-rename source.
8. Require authenticated ordinary convergence to re-admit correct bytes under
   the expected digest name with a distinct inode.
9. Require the pending forced recheck and ordinary convergence to clear the
   active alarm, restore readiness in the same PID, retain exact recovery
   history, and report the necessary mutation full scan.
10. Drain cleanly and require owner socket removal.

Focused C++ tests separately cover stale pair rejection, changed corruption,
already repaired content, absent source, exact idempotence with a full retained-
byte hash, canonical-name parsing, fresh-bootstrap rejection, bounded namespace
accounting, typed nonfatal entry/byte frontier completion, retained active-fault
authority, forensic-owner rejection, action ordering, generation coalescing,
different-pair exclusion, post-drain rejection, completion races, PID binding,
and malformed responses.

## Audit/refactor findings

The adjacent review corrected seven concrete risks rather than only documenting
the feature:

1. **Manual private-store repair was the product gap.** Quarantine now crosses
   CLI, local control, service owner, rooted store mutation, status, process
   recovery, and release verification without creating another sync engine.
2. **Idempotent filenames were not enough.** Existing retained destinations are
   fully rehashed before success, preventing a forged canonical name from
   becoming evidence.
3. **Split action state would have recreated shutdown races.** Drain, recheck,
   and quarantine remain one mutex-linearized snapshot with one wait predicate
   and one shutdown seal.
4. **Result shape could overclaim a move.** Non-mutating outcomes now leave the
   retained basename empty; status renders null unless the destination exists
   and has been byte-reproved.
5. **A lexical bootstrap check hid a semantic adoption hole.** The first guard
   mentioned `bootstrap.quarantines` but placed it inside the product-bound
   no-adoption branch. A standalone store could therefore publish a fresh
   identity over unexplained quarantine bytes. Quarantine evidence is now
   rejected before the ordinary payload-adoption exception, and a focused test
   proves the failure publishes no identity or other namespace mutation.
6. **Ordinary capacity was misclassified as fatal corruption.** A full valid
   quarantine frontier previously raised `std::length_error` through the
   service owner and could terminate the daemon. Exact entry and byte exhaustion
   now return typed terminal dispositions without mutation or authority loss.
7. **Directory durability did not imply byte durability.** The corrupt source
   is synchronized before rename, and an existing exact destination is
   synchronized after rehash, before either pathname is accepted as retained
   diagnostic evidence.

The audit also rejected a tempting but wasteful claim. Quarantine cannot both
remove an authoritative payload and promise zero subsequent mutation scan; the
ordinary re-admission owner needs fresh namespace authority. The test and status
surface now make that cost explicit.

## Research-informed product comparison

Resilio's Archive and Syncthing's file versioning are user-facing recovery
systems with retention and restore semantics. Rev0961 deliberately implements a
smaller primitive: explicit preservation of one exact corrupt private-store byte
image so good content can be fetched again. Calling it versioning or an archive
would be misleading. A complete replacement product still needs owner-visible
restore, retention classes, reachability pins, quotas, safe collection, and a
measured workflow deciding what should be retained.

Linux `renameat2(..., RENAME_NOREPLACE)` and pathname Unix-socket permissions
provide the current implementation substrate. Those mechanisms do not create a
portable Windows/macOS contract, network-filesystem lock equivalence, or hostile
same-user isolation. Cross-platform recovery remains open.

## What this proves

Subject to the runtime, sanitizer, and package evidence bound into the release,
rev0961 proves that the retained Linux C++ service can accept one exact owner
quarantine obligation, re-prove and preserve the exact active corrupt byte image
outside payload authority without replacing its inode, expose truthful status,
re-fetch correct content through existing authenticated convergence, and recover
readiness in the same process.

It also proves that reaching the declared valid entry or byte frontier is a
typed non-mutating completion rather than a reason for the retained service to
exit, while structurally invalid over-budget namespaces remain fail closed.

It also proves the implementation's declared boundedness: at most sixteen
canonical retained images, aggregate retained bytes no greater than the active
indexed-byte budget, one pending exact local request pair, monotonic process-local
generations, and no automatic quarantine.

## What this does not prove

Rev0961 does not provide automatic quarantine, user-file versioning, restore,
retention age, reachability, garbage collection, encrypted untrusted storage,
filesystem-wide scrub, hostile same-UID protection, power-loss behavior on every
filesystem/storage stack, network-filesystem lock equivalence, portable local
control, rename identity, directories and metadata parity, selective sync,
changed-block transfer, many-share supervision, live public Tor/I2P privacy
qualification, or completion of a named measured Resilio uninstall workflow.

The structural audit is lexical hygiene, not semantic proof. Compiler, complete
registry, focused runtime, real-process, sanitizer, parent, projection, manifest,
ZIP, CRC, and clean-extraction evidence remain load-bearing release gates.


The namespace mutation deliberately exposes one mutation-authority full scan before ordinary re-admission can regain readiness.
