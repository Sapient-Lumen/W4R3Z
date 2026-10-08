# Durable File Payload Store Audit — rev0893

## Heart of the mission

AnonSync is an authority-accounting system before it is a file-transfer
program. Exact authorized history must own identity, causality, policy,
selection, retry, receipt, and visible effect. A digest, cache, index, process
memory snapshot, filesystem pathname, or successful transport call may
accelerate a decision, but none of those summaries may manufacture authority
that the canonical operation and its owned capabilities do not possess.

The rev0892 sender path made a decisive correction: content availability became
part of exact SQLite outbox selection and arbitrary payload callbacks were
removed. Its remaining seam was still operationally incomplete. Every caller
had to construct and retain a bounded `SyncReplicaFilePayloadSnapshot`
containing the complete current working set. That was a useful callback-free
correctness value, but not durable availability. A process restart discarded
it, a large queue multiplied memory pressure, and every integration caller had
to become an informal content-lifecycle owner.

Rev0893 adds one deliberately narrow POSIX content owner:
`SyncReplicaFilePayloadStore`. It publishes immutable bytes under their full
lowercase SHA-256 digest, reconstructs a bounded canonical digest/size index
from a retained private directory, durably binds that directory to one folder
through an exact versioned identity marker, and reopens only the selected
object after a SQLite claim has been minted. The store is availability
authority subordinate to the canonical operation. It is not operation
evidence, membership evidence, a receipt, a file-effect owner, a garbage
collector, or an anonymity mechanism.

## Authority sequence

The intended sender sequence is now:

1. A caller presents payload bytes to the durable store before outbox dispatch.
2. Before any index becomes authoritative, the store exact-reconciles a
   versioned marker binding the private root to the configured folder. A legacy
   clean root may be adopted only after a complete mutation-free namespace
   scan; hostile, malformed, linked, or over-budget entries prevent marker
   creation. A conflicting marker rejects configuration relabeling.
3. The store derives the full SHA-256 digest and observes its retained root.
4. Existing exact bytes reconcile idempotently. Otherwise a create-new
   descriptor-relative publisher writes a private temporary file, synchronizes
   it, performs a no-replace namespace publication, and synchronizes the
   directory.
5. A store snapshot reopens and re-attests the configured root, scans the exact
   namespace, rejects unknown entries, and constructs a bounded canonical
   digest/size index. Payload files are opened without following links, checked
   for regular-file type, exact owner/mode/link/device policy, read through a
   bounded descriptor snapshot, hashed, synchronized, and rechecked in the
   namespace. The exact identity marker is opened and rechecked under the same
   descriptor-relative policy but is not counted as payload or transient
   pressure.
6. The file-delivery service validates the authenticated channel, folder scope,
   and payload-source authority before durable sender mutation.
7. The immutable digest inventory participates in SQLite outbox selection. An
   absent digest cannot consume attempt number, worker, lease, clock, or
   generation authority.
8. After exact selection, the store reopens only the selected digest relative
   to its retained root and rechecks exact size, SHA-256, file identity, and root
   authority.
9. A selected-read failure exact-releases the same SQLite claim onto the
   bounded retry schedule. It cannot silently strand a lease or construct a
   request from stale bytes.
10. The existing dispatch guard re-attests exact claim identity and the live TLS
   channel while the request frame is constructed. The store does not settle
   the outbox and does not imply receiver effect.

This ordering preserves the mission: the content index narrows eligible
canonical operations, while the exact operation still owns attempt identity and
the live channel still owns dispatch authority.

## What changed in C++

### Durable content owner

`src/sync_replica_file_payload_store.hpp/.cpp` adds two move-only types.

`SyncReplicaFilePayloadStore` owns the configured folder scope, an absolute
private root, its retained `SyncDirectoryAuthority`, and explicit limits:

- maximum durable entry count;
- maximum bytes per payload;
- maximum aggregate indexed bytes;
- maximum exact publication-residue count; and
- maximum aggregate publication-residue bytes.

The root contains one exact private
`.anonsync-payload-store-identity-v1` file. Its bytes bind a versioned domain to
the configured folder ID. Existing exact markers reconcile; conflicting marker
bytes reject a wrong-folder restart. Marker bootstrap is deliberately
mutation-free until a complete scan has accepted every pre-existing entry, so
calling `snapshot_or_throw()` on a hostile legacy root cannot bless it by
adding identity evidence. Publication is create-new and exact-reconciled after
ambiguous local failure. The marker is durable local configuration evidence,
not a signature or remotely verifiable provenance statement.

`put_payload_or_throw()` performs an exact full-store preflight, computes the
content digest, enforces all capacity bounds, publishes create-new bytes through
the existing atomic publication owner, and reconciles an ambiguous local
failure against exact final bytes. It never replaces an existing digest name.

`SyncReplicaFilePayloadStoreSnapshot` owns a fresh retained root authority and a
sorted vector of digest/size entries. It does not retain the complete working
set. `content_inventory()` supplies the immutable canonical availability value
used by SQLite selection. `copy_payload_for_operation_or_throw()` reopens and
copies exactly one selected payload after claim selection.

### Shared descriptor-relative regular-file resolver

The earlier path resolver only exposed directory-component opens. Rev0893
refactors its internal open policy into one flags-parameterized core and adds
`sync_posix_open_regular_file_component_or_throw()`.

The regular-file path:

- rejects unsafe basenames;
- inspects the terminal component with `fstatat(..., AT_SYMLINK_NOFOLLOW)`;
- rejects symlinks and non-regular objects before an open can block;
- opens with `O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC` and `O_NOCTTY`
  where available;
- uses the already probed `openat2(2)` resolution capability with
  `RESOLVE_BENEATH`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, and
  `RESOLVE_NO_XDEV` when available;
- proves the nonblocking flag and exact pre/post descriptor identity; and
- rechecks mount identity through the existing capability model.

This is a refactor rather than a second resolver. Directory and regular-file
opens share the same actual capability observation, fallback behavior, mount
policy, and error classification. Rev0893 does not infer support from kernel
version; that mistake was already exposed by the time-namespace regression in
rev0874.

### One service and TLS composition path

The file-delivery service now has a private template that accepts either the
rev0892 in-memory snapshot or the rev0893 durable snapshot. This is compile-time
composition, not a callback surface. Both concrete types expose the same narrow
operations: folder proof, preflight, immutable inventory, and exact selected
copy.

The template owns the only claim sequence, exact-release catch, dispatch guard,
and request construction. The TLS convenience paths similarly share one
compile-time forwarding core. This prevents the durable source from acquiring a
parallel, subtly different retry or framing implementation.

## Filesystem cutpoints and research

The implementation follows three external primary references while keeping its
claims narrower than those references.

Linux `openat2(2)` documents that `RESOLVE_NO_SYMLINKS` rejects symbolic-link
resolution and that `RESOLVE_NO_XDEV` rejects traversal across mount points,
including bind mounts. AnonSync uses those flags only when an actual syscall
probe has established the capability and retains explicit weaker capability
states when they are unavailable:
<https://man7.org/linux/man-pages/man2/openat2.2.html>.

Linux `fsync(2)` documents that synchronizing a file does not necessarily make
its directory entry durable and that an explicit `fsync()` on the directory is
needed for that namespace cutpoint. The existing atomic publisher and rev0893
scan/reconciliation path keep file and directory synchronization distinct:
<https://man7.org/linux/man-pages/man2/fsync.2.html>.

RFC 6920 standardizes naming digital objects with hash outputs and explains the
relationship between a hash-derived name and verification of the referenced
object. Rev0893 uses the simpler local convention of a full lowercase SHA-256
basename rather than implementing the RFC's URI formats, but the same important
principle applies: the name is useful only when the observed bytes are checked
against it: <https://www.rfc-editor.org/rfc/rfc6920>.

These references do not prove AnonSync's implementation. They motivate the
cutpoints; compiled adversarial tests and sanitizers exercise the concrete C++
path.

## What this proves

Within the tested POSIX process and filesystem model, rev0893 establishes the
following properties.

### Restart reconstruction

A new store object can reconstruct the same canonical digest/size index from
durable payload files after the original owner has gone away. Before doing so,
it must observe the exact versioned marker for the same folder; a caller cannot
silently relabel one durable root by supplying a different folder ID. A clean
pre-marker root containing only valid digest-named payloads may be adopted, but
the marker is minted only after the full namespace has passed the ordinary
scan. The snapshot digest binds folder scope, root path, root attestation
digest, all configured limits, durable and transient pressure observations,
aggregate bytes, and every sorted digest/size pair.

The snapshot digest is evidence about an already validated observation. It is
not a substitute for the entries, and a later selected read does not trust it
as byte authority.

### Exact immutable publication

The final digest basename is create-new. An exact preexisting object reconciles
idempotently; a conflicting object is rejected. Publication uses the existing
owner's temporary-file, file-sync, no-replace rename, and directory-sync
cutpoints. An exception after publication is reconciled against the exact final
bytes instead of guessed from the exception class.

### Hostile namespace rejection

The runtime matrix rejects unknown filenames, malformed digest contents,
symlinks, digest-shaped FIFOs, multiply linked files, wrong modes, foreign
namespace aliases, invalid publication-shaped residues, and root-path
rebinding. The FIFO case is specifically bounded: pre-open type inspection and
`O_NONBLOCK` prevent an untrusted special file from hanging a scan.

### Bounded pressure

Durable entry count, individual payload bytes, aggregate durable bytes,
publication-residue count, and aggregate publication-residue bytes are all
finite and included in snapshot identity. Unknown namespace entries are errors,
not invisible disk consumption.

### Exact post-claim failure handling

A store snapshot can validly index an object and then encounter deletion or
replacement before selected lookup. The service catches that failure after the
claim, exact-releases the same claim, preserves the configured retry delay, and
later resumes with the next exact attempt number after the bytes are repaired.
It does not turn a local content failure into transport ambiguity or a terminal
receipt.

### No complete working-set retention by the dispatch caller

The durable snapshot retains digest/size metadata and one root capability. It
loads at most one bounded payload at a time during a full scan and one selected
payload for dispatch. The caller no longer needs to preserve every payload byte
in process memory across retries or restarts.

## What this does not prove

### No same-UID or privileged-writer defense

The scan is not an adversarial filesystem transaction. A same-UID process or a
privileged actor that can mutate the root concurrently remains outside this
proof. Before/after directory observations, descriptor identity, file
modification snapshots, and final namespace rechecks make ordinary races fail
closed, but they do not create a kernel-enforced immutable directory or a
separate security principal.

The store also does not claim malicious same-process defense. Memory corruption,
a forged internal object, or code executing with the same capabilities can
invalidate C++-level assumptions.

The identity marker narrows accidental configuration relabeling and
cooperative restart ambiguity; it does not upgrade the directory into signed
membership, rollback-proof provenance, or a separate-principal trust root. A
same-UID or privileged writer can still replace local evidence outside the
tested observation windows.

### No cross-process capacity serialization

Two cooperative processes can independently scan below a limit and publish
different payloads concurrently, temporarily crossing aggregate count or byte
budgets. A later full scan will reject the over-budget state, but rev0893 does
not provide a directory lock, lease database, or single-writer daemon. This is
one reason the class is an availability seam rather than a complete storage
service.

### No garbage collection or reachability authority

There is no reference count from canonical operations, outbox intents, staged
receiver effects, receipts, checkpoints, or peer acknowledgements. There is no
tombstone, minimum retention interval, lease, pin, dead-letter owner, or safe
unlink cutpoint. Consequently rev0893 deliberately never deletes payload files
or publication residue.

Adding opportunistic deletion here would be severe: a summary of current
outbox rows cannot prove that no restart, delayed retry, historical receipt,
repair operation, or offline replica still requires the bytes. Garbage
collection must be derived from an explicit durable reachability protocol.

### No peer/folder fairness or disk reservation

The limits apply to one store observation. They are not per-peer quotas,
per-folder scheduler fairness, filesystem free-space reservation, project-wide
pressure accounting, or protection against unrelated files outside the
private root. An attacker capable of causing authorized content insertion could
still fill the configured budget with many unique hashes.

### No atomic transaction between SQLite and the filesystem

Payload publication and outbox mutation are separate resources. A payload may
exist without an operation, and an operation may exist while its payload is
missing. The latter is intentionally nonterminal: availability-aware selection
skips it without consuming attempt authority. There is no distributed commit
claim between the SQLite owner and the content directory.

### No hash agility or collision recovery

The namespace is fixed to SHA-256. A digest collision is treated as one name and
exact conflicting bytes are rejected, but there is no algorithm identifier in
the filename, migration mechanism, dual-hash epoch, or collision adjudication
record. RFC 6920's algorithm-qualified naming is a useful direction for a later
versioned namespace.

### No streaming or chunk tree

The selected payload is still copied into one `std::string`, then incorporated
into the current canonical request and TLS framing path. Memory is now
O(selected payload), not O(total working set), but large-object streaming,
chunk verification, resumable ranges, sparse files, deduplicated chunk trees,
and end-to-end flow control are absent. The current hard payload bound keeps
that omission explicit.

### No anonymity claim

Digest-named local files can reveal equality, payload sizes, access patterns,
and retention duration to a local observer. The store does not encrypt content
at rest, hide traffic metadata, provide unlinkability, or alter the project's
still-unimplemented anonymity model.

## Audit and refactor findings

### Corrected waste: whole-working-set copies

The most direct waste was architectural. The callback-free rev0892 API pushed
complete working-set ownership into every caller. That made tests precise but
made a production retry loop either rebuild all payload strings repeatedly or
retain them indefinitely. Rev0893 centralizes durable availability and keeps the
existing in-memory snapshot as a small test, migration, and differential seam.

### Corrected leak frontier: `fdopendir()` failure ownership

The first scan draft released its duplicated root descriptor in the argument to
`fdopendir()`. POSIX transfers descriptor ownership only on success; a failed
`fdopendir()` would therefore have escaped with no RAII owner. Rev0893 now keeps
the descriptor in `OwnedFd` through the call and releases it only after a
non-null directory stream has accepted ownership. This is a small line-level
correction with cumulative operational importance because repeated low-memory
or libc failures must not exhaust process descriptor authority.

### Corrected drift: publication-residue naming

The durable store initially duplicated the atomic publisher's private temporary
basename grammar. That would have made a future publisher-version change look
like hostile namespace corruption after restart. Rev0893 exports one exact,
non-authorizing classifier from the publisher itself. The store may count and
diagnose names accepted by that classifier, while the API explicitly grants no
unlink, byte, or ownership authority.

### Corrected drift: two path-resolution implementations

A tempting implementation would have added bespoke `openat()` logic inside the
store. That would duplicate the mount, symlink, close-on-exec, and capability
rules already hardened in the directory resolver. Rev0893 instead extracts a
single internal flags-aware component opener and adds a regular-file typed
wrapper. The file-specific policy remains visible while capability handling is
shared.

### Corrected drift: two dispatch implementations

The durable source could also have acquired a copied claim-and-release path.
The service and TLS layer now use compile-time shared helpers, so the in-memory
and durable sources cannot independently reorder claim mutation, selected byte
copy, exact release, dispatch guard, or frame construction.

### Remaining severe waste: O(total indexed bytes) full scans

Every `snapshot_or_throw()` reads and hashes every payload, and every
`put_payload_or_throw()` performs that full scan before publication. This is the
correctness oracle and is appropriate for the current bounded scale, migration,
repair, and adversarial validation. It will become the dominant cost as the
store grows. The flat directory also makes lookup and scan cost dependent on
filesystem behavior at larger cardinalities.

Do not “fix” this by trusting an unverified cache. The next production owner
should use an indexed SQLite catalog only as an accelerator:

1. Keep digest-named files as byte authority.
2. Record publication intent, exact size, stable file identity observations,
   algorithm epoch, and verification generation in a durable catalog.
3. Use create-new file publication and catalog mutation as a recoverable
   two-resource protocol with explicit intermediate states.
4. On restart, reconcile catalog rows against the directory and directory
   entries against catalog rows.
5. Retain the current full scan as a full-scan oracle for migration, repair,
   periodic audit, and generated differential tests.
6. Permit an indexed fast path only when the root identity, catalog generation,
   namespace change witness, and selected file all re-attest.
7. Measure and bound verification debt; never let an “eventually scanned” entry
   become dispatch authority before exact verification.

A directory watcher alone is not authority. Events can overflow, be coalesced,
or be lost across restart. It may schedule reconciliation but must not replace
the full-scan oracle or selected-file reproof.

### Remaining build waste

The new store is a narrow library, but the cube still contains many link targets
and several giant legacy translation units. A focused durable-store edit should
not require rebuilding the historical executable monolith. The medium-term
refactor remains semantic decomposition by authority boundary, generated CMake
target declarations, and an affected-authority validation gate backed by a
periodic complete legacy gate.

### Lexical audits remain hygiene only

Rev0893 updates stale lexical audits that expected one concrete payload snapshot
spelling. The new source audit explicitly disclaims semantic proof. It can catch
missing files, CMake drift, removed negative-test vocabulary, and obvious
ordering changes. It cannot establish syscall behavior, race safety,
durability, or exact SQLite rollback. Runtime, sanitizer, stress, and package
verification remain load-bearing.

## Recommended next sequence

1. Compose the durable payload store into a bounded production listener/sender
   executable that already uses the anchored membership, TLS, SQLite outbox,
   receiver effect, and terminal receipt owners.
2. Add an indexed catalog as an accelerator and differentially test every fast
   result against this full-scan oracle under generated crash frontiers.
3. Define canonical content reachability and retention records before adding
   garbage collection.
4. Add process ownership or a documented single-writer service boundary before
   treating aggregate limits as hard concurrent quotas.
5. Version the content namespace with an algorithm identifier and migration
   epoch.
6. Replace whole-payload request buffering with a bounded authenticated chunk
   protocol while preserving operation identity and terminal effect semantics.
7. Add per-folder and per-peer pressure policy, retry/dead-letter ownership, and
   operator-visible diagnostics.
8. Keep anonymity and metadata-leakage claims separate until concrete at-rest,
   discovery, relay, endpoint, and traffic-analysis mechanisms exist.

## Bottom line

Rev0893 closes a real production-shaped hole without promoting a cache to
canonical authority. Sender payload bytes can survive process restart, exact
content availability participates in claim selection, and a selected-file race
releases rather than corrupts attempt authority. The change also removes two
likely drift points by sharing the path-resolution and dispatch state-machine
cores.

The next danger is performance pressure inducing an unsafe shortcut. The full
scan is intentionally expensive because it is the correctness oracle. Future
indexing should be introduced as subordinate, reconstructible acceleration,
with the current implementation retained as the differential standard against
which faster owners must converge.
