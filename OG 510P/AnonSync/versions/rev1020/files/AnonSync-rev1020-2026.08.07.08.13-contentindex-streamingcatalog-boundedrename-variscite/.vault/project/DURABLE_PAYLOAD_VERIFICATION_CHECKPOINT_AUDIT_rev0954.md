# Durable payload verification checkpoint audit — rev0954

## Heart of the mission

AnonSync exists to replace Resilio Sync in a real workflow with a practical C++
folder-synchronization product. Direct TCP, Tor, and I2P are alternate routes
into one authenticated synchronization model. The product has to survive large
retained stores, restart, interrupted transfer, stale metadata, and ordinary
operator mistakes without asking a user to understand internal proofs.

The shipping payload store already used immutable SHA-256 basenames, descriptor-
rooted no-follow opens, exact owner/mode/link/device checks, full-file hashing,
cooperative shared/exclusive leases, and atomic publication. Its important scale
failure was simpler: the first snapshot in every new process re-opened and
re-hashed every retained payload byte. A store near the production 64 GiB
indexed-byte default could therefore do tens of gigabytes of read I/O merely to
restart, even when no payload had changed. The process-local verification cache
introduced earlier removed repeated hashing only until process exit.

Rev0954 adds one durable payload verification checkpoint to remove that restart
penalty while retaining the complete namespace scanner as the authority. The
checkpoint is deliberately a narrow shipping correction, not a second database,
not a garbage collector, not a block-transfer protocol, and not a claim that
metadata can permanently prove content integrity.

## Acceleration, not authority

The checkpoint is named exactly:

`.anonsync-payload-verification-index-v1`

It records the store-identity digest and exact marker metadata, total indexed
bytes, and one sorted entry per digest-named payload. Each payload entry contains
the digest basename and the exact regular-file metadata already used by the
process-local verification cache: device, inode, mode, link count, owner, group,
size, mtime, and ctime, including nanoseconds.

A checkpoint may avoid a payload-byte hash only when all of the following are
true:

1. The store scan holds the ordinary cooperative shared lease on the exact
   identity-marker inode.
2. The checkpoint is one private, same-owner, single-link regular file on the
   retained root device with exact mode 0600.
3. Its fixed-width v1 encoding has the exact expected length, a valid trailing
   SHA-256 checksum, a supported generation, bounded entry count and byte sum,
   sorted unique lowercase digest identities, and valid metadata fields.
4. Its store-identity digest and marker metadata exactly match the marker inode
   carrying the live lease.
5. The scanner independently enumerates the digest-named payload, opens it with
   the existing rooted no-follow capability, and observes metadata exactly equal
   to the checkpoint entry.
6. The scanner re-proves the exact payload pathname, the checkpoint pathname,
   the directory before/after observation, the reopened scan root, the retained
   root, and finally the live identity-marker lease.

Failure of any checkpoint condition does not make its records partially true.
That payload is hashed from bytes, and a malformed, stale, absent, oversized, or
identity-mismatched checkpoint grants no reuse. `ReadOnlyInspect` intentionally
ignores both process-local and durable acceleration and hashes every payload on
every forensic snapshot.

The checksum is a corruption detector and canonical-format seal, not a MAC. A
same-UID process able to rewrite private store files is already outside the
cooperative writer-lease assumption. Even then, a fabricated checkpoint cannot
make a changed ordinary payload reusable without also reproducing the exact
metadata fence observed from that payload. The design does not elevate this into
an adversarial-host security claim.

## Canonical bounded encoding

The new leaf owner is split into:

- `src/sync_replica_file_payload_verification_index.hpp`;
- `src/sync_replica_file_payload_verification_index.cpp`;
- `tests/sync_replica_file_payload_verification_index_test.cpp`.

The store no longer owns binary parsing details inside its already-large source
file. The canonical v1 record uses:

- a fixed generation magic line;
- fixed-width unsigned 64-bit big-endian integers;
- fixed 64-byte lowercase SHA-256 text fields;
- exact metadata geometry for the marker and each payload;
- one count and one aggregate-byte field;
- a final 64-byte lowercase SHA-256 checksum over every preceding byte.

The parser computes the exact expected record size before reserving entries,
rejects arithmetic overflow, rejects any trailing or truncated byte, and applies
caller entry/byte ceilings before materializing the vector. Runtime tests reseal
hostile records after mutation so that checksum failure cannot mask generation,
length, count, digest, mode, duplicate-order, timestamp, or aggregate-byte
parser defects.

The exact production maximum is about 15.2 MiB at 100,000 entries. Ordinary
stores pay only their actual fixed-width entry count. The parser never reserves
the production ceiling unconditionally.

## Full scanner integration

The payload namespace still has one authoritative full scanner. It independently
opens the retained root, duplicates a separate directory cursor, captures root
metadata, observes the exact checkpoint file, enumerates every entry, and
classifies every digest, staging owner, assembly residue, publication residue,
identity marker, and checkpoint name. Unexpected entries continue to fail
closed.

For each immutable payload, the scanner chooses one of three paths:

- an exact process-local observation reuses the previous verification;
- otherwise an exact durable-checkpoint observation reuses the restart proof;
- otherwise the complete payload is streamed through SHA-256 and compared with
  its digest basename.

Reuse changes only work accounting. The canonical payload snapshot digest still
contains the same limits, identities, counts, byte sums, and digest/size pairs;
no cache or checkpoint field enters synchronization identity.

After sorting, the scanner compares the complete current payload set and exact
metadata against the durable checkpoint. This identifies an already-current
checkpoint without trusting it as namespace completeness. A valid checkpoint
with one stale record may accelerate unchanged peers while the changed payload
is hashed; after the complete scan, the replacement records the new exact set.

## Crash ordering

The publication sequence is intentionally asymmetric:

1. A shared leased scan constructs and re-proves one complete authoritative
   payload snapshot.
2. That shared lease is released. No shared observer writes metadata.
3. Best-effort checkpoint refresh reopens the same root and tries to acquire a
   fail-fast exclusive mutation lease.
4. Under that lease it performs another complete namespace scan. The warm
   process cache avoids repeated payload-byte reads, but the namespace and every
   exact metadata observation are re-proved across the authority gap.
5. The v1 record is atomically create-new published or expected-metadata
   replaced, then the identity-marker lease is re-proved.
6. Failure at allocation, contention, ENOSPC, serialization, stale expected
   metadata, rename, fsync, or final reproof is swallowed only by the
   non-authoritative checkpoint path. The already-returned payload snapshot is
   unchanged.

A mutation batch already holds the exclusive lease and retains a complete exact
index. Its teardown may checkpoint that exact state before promoting the
process-local immutable cache generation. Each individual payload publication
is durable and verified before being added to the checkpoint candidate. If a
publication reports a post-rename error but reconciliation proves that the
payload became exact, the checkpoint is conservatively dirtied so a later scan
cannot omit it.

A receiver completion also already paid for a whole-file digest and a complete
pre-publication scan. It inserts the exact post-rename descriptor observation
into that scan, optionally checkpoints it, and promotes the process-local cache.
The post-rename observation matters because POSIX rename may advance ctime. The
code permits only that ctime transition, re-fstats the still-open descriptor,
and binds the digest pathname to the post-rename metadata before it becomes
restart-reusable.

Crash outcomes are conservative:

- payload committed, checkpoint absent or old: restart hashes only records not
  exactly covered by the old checkpoint;
- checkpoint temp left before rename: the existing publication-residue scanner
  recognizes, bounds, and repairs it under the mutation lease;
- checkpoint rename visible but parent fsync incomplete: either old or new
  acceleration may survive, and both are revalidated from the namespace;
- malformed or partial checkpoint file: it grants no reuse and is replaced only
  after a complete payload proof;
- stale expected destination during replacement: publication fails without
  overwriting an unobserved replacement, and the payload result remains valid.

## Geometric publication and capacity ownership

Writing the whole fixed-width index after every new payload would make initial
sync approximately quadratic in checkpoint bytes. The cache therefore tracks
the durable checkpoint cardinality/bytes and pending additions. Publication is
due geometrically:

- entry threshold: clamp the durable entry count to 256 through 4096;
- byte threshold: clamp the durable byte count to 64 MiB through 1 GiB;
- graceful close: flush any pending or forced repair once.

This bounds restart-cold work after a crash without imposing one metadata rewrite
per received file. It is scheduling, not authority; skipping a checkpoint never
changes payload admission or synchronization results.

Checkpoint publication also yields to the existing transient protocol budget.
Because the format is fixed-width, the exact encoded size is calculated before
constructing or serializing the O(namespace) record. If one atomic-writer residue
cannot fit alongside current staged state, publication is skipped before the
large allocation. Runtime coverage keeps a 128-byte transient budget—too small
for even an empty checkpoint—while proving that payload insertion, restart, and
full cold verification remain correct and that no checkpoint appears. This
corrects a development-time temptation to widen the fixture merely to admit
acceleration.

An oversized private checkpoint is likewise non-authoritative. The scanner
binds its exact metadata but does not allocate or read beyond the configured
encoded-size ceiling. It hashes the payload namespace and conditionally replaces
the oversized file afterward. Wrong type, owner, link count, device, or mode
continues to fail closed because such an object is not a replaceable private
metadata owner.

## Retained negative-capacity scheduling evidence

The initial capacity fence prevented an inadmissible checkpoint write, but it
still left a repeated-work defect. A restart snapshot first completed the
required shared authoritative namespace scan. Because a missing or stale
checkpoint was due, the best-effort path then acquired the exclusive lease and
performed a second complete namespace scan before discovering that the exact
fixed-width writer residue could not fit the transient budget. Graceful owner
teardown could repeat that scan, and another snapshot could repeat the pair.
The payload result stayed correct, but a deliberately optional accelerator was
multiplying the most expensive namespace operation.

Rev0954 makes the capacity preflight one centralized pure calculation over the
complete scanned index. The process-local checkpoint scheduler retains two
bits—whether a capacity observation is known and whether publication was
available—alongside its existing geometric work state. The ordering is:

1. the complete leased scan establishes authoritative payload truth;
2. after the final lease proof, the exact encoded checkpoint size is compared
   with current transient entry and reserved-byte headroom;
3. that result is retained only as non-authoritative publication scheduling
   evidence;
4. a known-unavailable result suppresses both the ordinary post-snapshot refresh
   and the graceful final refresh;
5. a later complete scan replaces the observation, while any payload addition
   invalidates it because both encoded size and transient state may have changed;
6. the actual writer repeats the same centralized preflight under the exclusive
   lease before constructing or serializing the O(namespace) record.

This does not claim that capacity stays unavailable after the shared scan. A
cooperating second process may remove transient state before this process closes.
Skipping the graceful attempt can then delay only checkpoint acceleration until
the next complete scan; it cannot delay or alter payload convergence. Conversely,
a capacity-available shared observation does not authorize the later write: the
exclusive refresh re-scans and rechecks the capacity fence before publication.

The snapshot diagnostic
`verification_checkpoint_deferred_by_transient_capacity()` reports this exact
scheduling state without changing canonical snapshot identity. The tight-budget
fixture now proves four things together: the cold restart hashes authoritative
bytes, no checkpoint file is created, the snapshot reports deferral, and a
second snapshot reuses process-local verification without performing the known-
doomed exclusive refresh. Destroying the owner also leaves the checkpoint absent.

## Same-process re-verification must refresh restart evidence

The process-local generation and durable checkpoint intentionally have
different read costs. Once a complete scan has loaded a valid checkpoint, later
scans compare live payload observations against the immutable in-memory
generation and avoid rereading the potentially multi-megabyte checkpoint body.
That is the desired warm path, but it created a stale-scheduling corner.

Suppose one payload is rewritten in place with identical bytes. Its inode may
remain the same while ctime and mtime change. The next complete scan correctly
misses the process cache for that entry, hashes the descriptor to prove the
digest, and publishes an exact replacement process generation. Before this
audit, the checkpoint scheduler saw that checkpoint contents had not been
requested and retained its old “current” state. It therefore skipped
publication. A fresh process then rejected the stale durable metadata and paid
for the same whole-payload hash a second time.

The corrected observation rule is conservative and bounded:

1. any process-cache-backed complete scan that hashes at least one payload
   marks the durable checkpoint due;
2. exact entry-count or indexed-byte drift from the last durable baseline also
   marks it due, covering namespace insertion, removal, and size changes even
   when other observations were reusable;
3. the already-returned snapshot remains authoritative regardless of whether
   the optional refresh succeeds;
4. refresh still acquires the exclusive cooperative lease, completes a new
   namespace scan, repeats the exact capacity calculation, atomically publishes
   or expected-replaces the checkpoint, and finally records the new baseline.

This deliberately does not publish from the shared scan's index. Another owner
may mutate the namespace after the shared lease is released, so the exclusive
refresh must establish its own current cutpoint. The additional scan is paid
only after actual re-verification work or exact aggregate drift, while ordinary
fully warm snapshots remain byte-cold and checkpoint-body-cold.

The focused regression creates a durable checkpoint, starts a fresh owner that
uses it, rewrites the payload in place with byte-identical content, and proves
that owner hashes exactly once. A second fresh owner must then report durable
reuse and zero hashed entries. The test binds the restart-cost property without
promoting metadata equality to permanent content integrity.

## Source-fresh composition and sealed-parent overlay audit

The durable-checkpoint work survived in more than one unsealed branch. Two
problems were hidden until the change was reconstructed over the exact sealed
rev0953 bytes.

First, timestamp-retained Ninja objects made focused binaries appear healthy even
though a clean compilation failed: `SyncReplicaFilePayloadStoreMutationBatch::State`
had gained four process-versus-durable reuse-origin constructor parameters, but
the only production construction site still supplied the older argument list.
The final implementation initializes those counters from the first scan,
aggregates them across publication-residue cleanup rescans and failure recovery,
passes all four values into the state owner, and exposes a runtime partition that
would fail if the provenance were lost. Fresh build directories are mandatory
release evidence; an incrementally linked binary is not accepted as source
proof.

Second, one unsealed checkpoint branch was based on an earlier rev0953 candidate
and had removed the final sealed correction from
`sync_replica_sync_once_final_pass_settles_cutpoint`: equality between the pass's
published remote fairness cursor and the final durable cutpoint. Catalog and
visible-state digests can remain unchanged while a second scheduler moves that
cursor, so omitting the comparison could report a different scheduling head as
the same settled observation. Rev0954 is overlaid on the exact sealed rev0953
project and restores the cursor predicate, public contract comment, lexical
audit token, and compiled `scheduling-only remote cursor movement settled`
regression before any release validation is accepted.

This reconstruction work is part of the payload audit because acceleration code
must not weaken unrelated convergence settlement merely through branch age or
stale build artifacts.

## Sanitizer graph closure is feature ownership

The checkpoint parser was introduced as a narrow static library with a focused
product-labelled executable. AnonSync's inherited sanitizer graph intentionally
keeps separate explicit inventories for compilation instrumentation and final
executable link flags. This avoids injecting sanitizer runtimes into every
ordinary consumer, but it means a new executable is incomplete until it is
listed in both places.

The first fresh Clang product build exposed that omission. The shared SHA-256
library was instrumented, while the new verification-index test had no
`-fsanitize=address,undefined` final-link option. The linker correctly rejected
unresolved ASan/UBSan runtime references. Incremental GCC testing could not
detect this because non-sanitized static objects need no such runtime.

Rev0954 now adds the verification-index library and driver to the sanitizer
compile inventory and the driver to the explicit final-link inventory. The
payload structural audit extracts those two CMake bodies and requires the exact
targets in their correct roles. A loose target-name count is insufficient: a
test may exist, be registered, and even be a product dependency while still
failing only at the sanitizer link frontier.

## Owner-local cache ordering audit

The process-local verification generation and checkpoint scheduler deliberately
contain no mutex. Their authority comes from the surrounding store or mutation
batch being bound to the process/thread incarnation captured by
`SyncDirectoryAuthority`. The intended invariant is stronger than “ordinary
operations happen to be thread-affine”: no code may even read the mutable
scheduler or generation pointer until that owner relationship has been proved.

Review found three best-effort exceptions. The checkpoint-refresh helper tested
whether publication was due before its rooted source preflight; graceful store
teardown repeated the same scheduler test; and detached mutation-batch teardown
read both `shared_ptr::use_count()` and scheduler state before its first lease
proof. On a correct originating thread these were harmless fast paths. Under
concurrent foreign-thread misuse, however, the first cache access could race
with the legitimate owner before the directory authority later rejected or
fail-stopped the misuse. Thread affinity is not synchronization unless the proof
precedes the memory access.

The correction adds one narrow internal
`SyncDirectoryAuthorityAccess::require_current_owner_or_throw` bridge. It checks
only process/thread incarnation, so a clean no-op close does not pay for pathname,
mount, descriptor, or identity-marker reproof. Refresh and both teardown owners
call this gate before any scheduler, generation, or cache-owner-count read. The
existing complete rooted and lease proofs still occur before every checkpoint or
generation publication. A new lexical audit check fixes all three orderings and
prohibits moving the graceful-close scheduler predicate back ahead of the gate.

This does not make store or batch objects cross-thread safe, nor does it weaken
the authority object's fail-stop destruction rule. It only restores the claimed
memory-order boundary: foreign-thread misuse cannot touch the deliberately
unsynchronized acceleration state first.

## Staged-prefix integration failure found by the wider lane

The first implementation updated the complete scanner but missed the receiver's
lightweight staged-prefix namespace observer. That observer validates the full
lexical payload-root namespace while avoiding hashes of unrelated immutable
payloads between bounded ranges. Once the new internal file existed, ranged
reconciliation failed with “unexpected payload-root entry.”

This was a real integration defect, not a test inconvenience. The staged-prefix
observer now:

- observes the exact checkpoint before directory enumeration without reading its
  contents;
- recognizes exactly one matching internal basename during enumeration;
- rejects appearance, disappearance, duplication, incompatible private state,
  or observation drift;
- re-proves the exact checkpoint pathname at the final traversal cutpoint;
- retains the existing full-scan requirements before reserving a new prefix and
  before final payload publication.

A focused `staged-prefix` regression seeds the checkpoint, transfers a payload in
bounded ranges, proves namespace accounting remains unchanged, restarts the
owner, and proves both payloads reuse exact post-rename checkpoint metadata.
Both production `fdopendir` payload-root observers were reviewed; there is no
third partial namespace loop silently retaining the old vocabulary.

## What the checkpoint does not prove

Exact inode metadata is a strong ordinary-write invalidation fence on supported
POSIX filesystems: payload writes normally advance mtime and ctime, and setting
file timestamps also advances ctime. It is not a permanent content truth oracle.
Possible gaps include silent corruption in storage that preserves inode metadata,
hardware or filesystem defects below the observed metadata layer, privileged
metadata restoration, snapshot rollback to an indistinguishable observation,
and a hostile same-UID process outside the cooperative lease model.

Therefore rev0954 explicitly makes **no permanent corruption detection claim**.
A checksum-sealed metadata checkpoint can reduce restart I/O; it cannot replace
periodic content verification.

The next integrity owner should be a bounded rotating scrub persisted by digest
or ordinal. Each service interval should hash a bounded amount of retained
payload data, advance a durable cursor only after exact descriptor/path reproof,
and eventually cover the complete store. Startup, mutation, and delivery paths
would continue to hash changed/new bytes immediately. Scrub failure should
quarantine or fail closed without silently deleting the only retained copy.

On Linux filesystems that support it, `fs-verity` is a promising optional
acceleration/integrity backend for immutable payloads: the kernel builds a
Merkle tree, makes the file read-only, verifies reads, and can return a constant-
time verity digest. It is not portable, requires filesystem/kernel support,
changes file lifecycle, and its digest is not AnonSync's ordinary SHA-256 file
digest. Adoption would therefore require an explicit capability probe, a
mapping/proof between content identity and verity state, recovery behavior for
unsupported copies/restores, and tests across ext4, f2fs, and btrfs. It should
not be silently assumed from the current cloudtainer.

## Rejected entry-count-only scrub experiment

A late unsealed branch tried to add a rotating scrub by hashing one payload per
complete scan and retaining only a process-local ordinal. That looked bounded in
entry count, but it did not bound bytes, wall-clock time, or device I/O. One
large retained payload could therefore make every otherwise-idle service pass
read many gigabytes, while a restart would forget the cursor and repeatedly
select the same prefix. It also had no durable epoch, no byte budget, and no
quarantine or recovery state.

Rev0954 deliberately excludes that experiment. A production scrub must be
**byte-bounded as well as entry-bounded**, persist its exact continuation only
after successful content and pathname reproof, eventually cover the complete
namespace despite restart, and expose failure without deleting the sole copy.
Until that owner exists, the product reports the checkpoint strictly as restart
acceleration and keeps forensic `ReadOnlyInspect` byte-cold.

## Online research and inference

Sources consulted on 2026-07-30:

- https://docs.kernel.org/filesystems/fsverity.html
- https://man7.org/linux/man-pages/man7/inode.7.html
- https://man7.org/linux/man-pages/man2/utimensat.2.html
- https://docs.syncthing.net/users/syncing.html
- https://docs.syncthing.net/users/config.html

The Linux kernel documentation states that fs-verity makes supported regular
files read-only, verifies reads against a Merkle tree, and is currently supported
by ext4, f2fs, and btrfs. The Linux manual pages document ordinary mtime/ctime
updates and the ctime effect of timestamp changes. Syncthing's current
synchronization/configuration documentation describes a persistent metadata and
block-hash index plus filesystem rescanning. The inference for AnonSync is
limited: persistent metadata is a practical way to avoid repeated work, while a
separate repair/scrub mechanism must retain content completeness. No equivalence
or performance parity is claimed.

## Remaining payload-store work

The checkpoint corrects restart hashing, but the store remains append-only and
history-heavy. The next product-facing sequence should be:

1. persist and qualify a bounded rotating scrub;
2. define version retention, restore, reachability pins, quarantine, and safe
   garbage collection as one crash-consistent policy;
3. add block manifests and local block reuse so a one-byte edit does not require
   a new whole-file transfer;
4. measure the first Resilio-uninstall workload for payload count, retained
   bytes, restart latency, churn, and range-resume behavior;
5. then consider a broader metadata/subtree index for the synchronized folder
   scanner, keeping the current descriptor-rooted scanner as rebuild authority.

This order keeps the heart of the mission visible: remove real restart waste
without manufacturing a second source of truth or overstating metadata as
cryptographic content permanence.
