# Minimum-reader identity migration audit — rev0959

## Heart of the mission

AnonSync exists to replace Resilio Sync with one dependable C++ folder-sync
product. A restart-integrity improvement is not useful if an older installed
binary can silently reinterpret the same durable store and recover authority
from metadata that the newer format deliberately revoked. Rev0959 closes that
mixed-reader hole in the retained payload-store owner. It does not add another
daemon, database, scanner, or user-facing policy language.

## The concrete downgrade hazard

Rev0958 added canonical scrub disposition `Prepared = 4`. A fresh rev0958 owner
that observes `Prepared` or `Progress` for digest D must hash D's current bytes
before returning authority; the durable verification index cannot accelerate
that active digest. Rev0957 and earlier do not understand `Prepared`. They can
classify the scrub record as unusable, ignore it as acceleration evidence, and
then accept a metadata-exact durable verification-index entry for D.

That creates a precise downgrade failure:

1. rev0958 commits `Prepared` for D before scrub reads D;
2. bytes for D contradict the digest basename while all indexed POSIX metadata
   is reproduced;
3. the process exits before optional terminal failure evidence is durable;
4. a rev0957-or-earlier process opens the same v2/v3 identity basename;
5. the old reader rejects or discards the unknown scrub record but trusts the
   stale verification index; and
6. it can return payload authority without re-reading the contradictory bytes.

The scrub state cannot solve its own reader-compatibility problem. A separate
optional sidecar would repeat the same mistake: an old reader that does not know
the sidecar can ignore it. The minimum-reader generation therefore has to be
part of the object that every cooperative reader already needs for both identity
and locking.

## Chosen fence: rename the exact lock inode

Rev0959 keeps the established v2/v3 identity **bytes** and changes only the
identity/lease-anchor basename:

```text
standalone legacy: .anonsync-payload-store-identity-v2
standalone current: .anonsync-payload-store-identity-v2-reader-fence-v1
product legacy:    .anonsync-payload-store-identity-v3
product current:   .anonsync-payload-store-identity-v3-reader-fence-v1
```

A writable new owner accepts one exact legacy marker only through this sequence:

```text
reconcile exact legacy identity
    → acquire fail-fast exclusive flock on that exact inode
    → complete rooted namespace scan with all process/durable byte reuse disabled
    → atomically rename old basename to current basename with RENAME_NOREPLACE
    → fstat the still-open identity descriptor
    → accept only same inode/mode/link/owner/size/mtime; ctime may change
    → re-read exact identity bytes through the retained descriptor
    → fsync identity and root directory
    → prove old name absent and new name names the exact retained inode
    → rebind the live lease to the post-rename observation
    → force replacement of the pre-rename verification checkpoint
```

The cold scan occurs before the old name disappears. Therefore no new-reader
marker is published when current bytes contradict their digest, when a
cooperative old reader holds a shared lease, or when the legacy namespace is
otherwise invalid. The successful cold scan is rebound to the post-rename
identity observation and handed to the immediately following ordinary snapshot,
so migration does not perform a second payload-byte pass.

Linux documents that `rename(2)` leaves existing open file descriptors
unaffected and that `RENAME_NOREPLACE` refuses an existing destination. The
Linux `open(2)` model makes the descriptor refer to an open file description,
and `flock(2)` locks are associated with that open file table entry. Rev0959
uses those Linux semantics but still verifies the exact inode and both pathnames
before accepting the transition. The parent directory is synchronized because a
file `fsync` alone does not make a directory-entry rename durable.

Primary references:

- Linux `rename(2)`: <https://man7.org/linux/man-pages/man2/rename.2.html>
- Linux `open(2)`: <https://man7.org/linux/man-pages/man2/open.2.html>
- Linux `flock(2)`: <https://man7.org/linux/man-pages/man2/flock.2.html>
- Linux `fsync(2)`: <https://man7.org/linux/man-pages/man2/fsync.2.html>

## Namespace state machine

The writable ensure path now has one explicit state machine:

| Current marker | Legacy marker | Result |
|---|---|---|
| exact | absent | proceed |
| exact | exact or conflicting | fail closed; preserve both for inspection |
| conflicting | any | fail closed |
| absent | exact | exclusive cold migration |
| absent | conflicting | fail closed |
| absent | absent | `ExistingOnly` fails; explicit `CreateIfMissing` performs the established complete bootstrap preflight and creates only the current marker |

Both complete and lightweight payload-root traversals recognize all current and
legacy v2/v3 names. Any known identity name other than the exact selected anchor
is an incompatible generation, not an ignorable internal file. Legacy v1 remains
an explicit offline-migration rejection.

The migration API itself accepts only two directed edges: standalone v2 legacy
to standalone v2 reader-fenced, or product v3 legacy to product v3
reader-fenced. Merely supplying two distinct recognized names is insufficient.
This prevents a later constructor/refactor error from atomically rebinding a
standalone lease inode into the product namespace, or the reverse, before the
expected identity bytes can act as a secondary defense.

`ReadOnlyInspect` deliberately does not run ensure or migration. It observes only
an exact current marker and remains mutation-free. A root that still has only a
legacy marker therefore produces an absence diagnostic rather than silently
changing operator evidence.

## Restart and failure matrix

### Failure before rename

The exact legacy name and inode remain. The next writable owner repeats the
exclusive lease and complete current-byte proof. No current-reader authority was
published.

### Failure after rename but before the operation returns

The operation aborts. After an ordinary process restart, the durable namespace
can expose either the old or current basename depending on what reached stable
storage; the ensure state machine handles either exact singleton. Coexistence or
conflict fails closed. A surviving current marker has the post-rename identity
observation, so a verification checkpoint framed against the pre-rename marker
cannot grant exact restart reuse. A fresh owner falls back to complete hashing
before checkpoint replacement.

Linux also warns that an NFS rename may report failure even when the server
completed the operation. Rev0959 does not claim network-filesystem lock or
power-loss equivalence, but its retry rule intentionally inspects durable
singleton state rather than inferring namespace state from the prior syscall's
return alone.

### Cooperative old process already active

An old reader holding a shared or exclusive flock on the legacy identity inode
blocks the migration's exclusive lease. A process that opened the inode before
the rename but had not yet locked it cannot later prove the old pathname once
the rename has committed. After migration, a newly launched old binary cannot
find its expected marker. Its explicit-existing path fails, while its bootstrap
path encounters the unknown fenced marker during complete namespace preflight
and refuses to mint a second legacy identity.

This is a minimum-reader fence, not a hot rolling-upgrade protocol. Operators
must still stop old services before upgrading. Rev0959 does not revoke an
arbitrary authority object already issued inside an old process, and cooperative
`flock` is not protection against a hostile same-UID process that ignores the
protocol.

## Mechanical regressions

The focused C++ regression builds the exact dangerous durable composition:

- one valid legacy v2 marker;
- one metadata-exact verification-index entry over same-size corrupt payload
  bytes;
- one valid rev0958 `Prepared` record for that digest; and
- scrubbing disabled so migration itself must own the current-byte proof.

It then proves:

1. forensic `ReadOnlyInspect` does not migrate;
2. a child-held shared lock blocks migration and no current name appears;
3. stale verification metadata plus `Prepared` cannot bypass the cold scan;
4. corruption leaves the legacy name and exact inode unchanged;
5. repair permits migration with the same `(st_dev, st_ino)`;
6. the immediate snapshot reuses the migration scan in-process and performs zero
   duplicate payload hashes;
7. the next fresh owner uses a checkpoint rebound to the current marker;
8. product-bound v3 migration preserves its exact inode; and
9. coexisting exact current and legacy markers are rejected without deleting
   either forensic artifact.

The CLI process expectation now names the current product reader-fenced marker.
The structural audit binds the implementation order, runtime vocabulary,
documentation, and package verifier.

## Adjacent correctness correction: damaged intent is not absence

The same restart-path review found a broader fail-open classification. The scrub
state parser correctly labels a checksum-invalid or otherwise noncanonical
fixed-size record unusable, but the complete payload scanner previously treated
that result like no record. It could therefore accept a metadata-exact durable
verification-index entry without reading payload bytes. If the damaged record
was committed `Prepared` or `Progress`, losing its target digest through damage
did not make the write-ahead revocation disappear; it made the required target
unknowable.

Rev0959 treats `present && !usable` as a namespace-wide current-byte requirement.
Neither the process verification generation nor the durable verification index
may accelerate any digest-named payload in that complete scan. Every current
payload is descriptor-opened, metadata-attested, and hashed before snapshot
authority can return. The damaged record is preserved when current-byte proof
fails. When bytes are good, only a later exclusive state-reconciliation owner may
replace it with canonical state and resume bounded rotation. In the ordinary
path that is the scrub owner after the complete snapshot. During minimum-reader
migration, the exact legacy-inode migration lease is already exclusive, so the
owner may rebuild canonical `Idle` state against the post-rename identity before
handing off the cold process generation. This avoids an immediate duplicate
namespace rehash without treating the damaged record as content proof. Until a
record is rebuilt, a fresh complete scan still pays full-byte I/O because no
authenticated active target can be recovered from the damaged bytes.

The focused regression publishes a valid restart index, changes payload bytes to
a same-size contradictory image, rewrites the indexed POSIX observation to match,
and replaces the scrub record with checksum-invalid bytes of the exact canonical
width. The optional scrub budget is only one byte, mechanically too small to
discover the whole-file mismatch. The complete scan nevertheless reports the
exact expected and observed digests. After repair, it hashes the complete payload
before the bounded scrub rebuild starts, proving the damaged record never became
clean-absence acceleration authority.

The audit then followed the same state through a configuration with both
`max_scrub_bytes_per_attempt` and `max_scrub_entries_per_attempt` set to zero.
Previously that early "disabled" branch skipped all scrub-state publication, so
damaged or active intent survived indefinitely and every fresh process repeated
the complete payload-byte proof. Rev0959 now distinguishes optional bounded byte
work from mandatory metadata-only restart-fence settlement. If the complete scan
has already proved the current namespace, a writable owner may re-prove the
unchanged state/root/identity cutpoint and publish canonical `Idle` state without
reading payload bytes. A focused regression proves the first disabled owner hashes
the payload once and rebuilds state with zero scrub bytes, while the next fresh
owner obtains exact durable-index reuse and performs zero payload hashes. Because
no bounded byte attempt occurs, the process-local scrub throttle is not advanced;
lease contention, stale observation, transient-capacity refusal, or publication
failure leaves the restart fence intact and immediately retryable.

## Adjacent correctness correction: complete scan supersedes stale active progress

The reader-generation audit exposed a separate rev0958 composition. A fresh
owner observing `Prepared` or `Progress` correctly hashes the active payload in
its ordinary complete scan. If an operator repaired the payload in place while
preserving/reconstructing the indexed metadata, that scan can prove the current
whole file good. The later optional scrub nevertheless resumed the older partial
SHA-256 checkpoint. Combining an old corrupt prefix checkpoint with the repaired
current suffix could report a false integrity mismatch, and even an unchanged
file paid a redundant bounded reread after the complete scan had already proved
all bytes.

Rev0959 carries one exact `scrub_active_reverified_good` fact from the complete
scan into the existing exclusive scrub transition. It is set only when the scan
actually hashes the active digest, matches the digest basename, and freezes the
same active state observation. Under the exclusive scrub lease, the state file,
root directory, active digest, and canonical payload metadata must still match
the snapshot. The scrub owner then advances the fair cursor, clears active state,
and publishes `Idle` without reading payload bytes again. A distinct report bit,
`reverified_active_completed`, separates this zero-read settlement from
`reverified_failure_cleared`.

The focused regression installs a stale `Progress` checkpoint whose resumable
SHA state was computed from unrelated prefix bytes while the current complete
payload is good. The fresh owner hashes the whole current payload once, performs
zero scrub reads, publishes `Idle`, preserves the fair cursor, and returns valid
payload authority. The rotating one-file regression now proves each fresh
restart settles the active checkpoint from the stronger complete scan before a
later process begins the next fair cycle.

Because this is operator-visible scheduling and integrity evidence, peer-service
status advances to `anonsync.peer-service.status.v6`. Live/configured-service and
native-I2P process oracles require Boolean `state_rebuilt`,
`reverified_active_completed`, and `reverified_failure_cleared` fields plus the
later cooperative-lease and ambiguous-network-outcome evidence, rather than
silently accepting either the older schema or the interim rev0959 v5 shape.

## Adjacent audit and refactor findings

### Identity bytes and reader generation were previously conflated

The v2/v3 identity payload domains remain the durable folder/deployment binding.
The basename is now the reader-generation gate. Separating those responsibilities
avoids rewriting identity bytes merely to raise the minimum reader and allows the
same locked inode to survive migration.

### Lease-capable and reserved identity names are now distinct

The four v2/v3 names that this reader may select or migrate are represented
separately from the five reserved names it recognizes, the latter adding the
unsupported v1 basename. Complete scanners and staged-prefix observers preserve
the explicit v1 offline-migration failure. Exact-name lanes that deliberately do
not enumerate unrelated payload entries nevertheless probe all five reserved
names whenever the selected identity inode is opened or re-proved. This keeps
the optimization from treating a second lock namespace as harmless debris.

The adjacent regression creates a valid current marker and a coexisting v1
marker while a remote file is otherwise ready. Folder convergence fails at the
targeted identity cutpoint before selecting or publishing payload bytes, leaves
the catalog empty, and preserves both identity files for inspection.

### Migration is cold by policy, not by cache accident

`PayloadVerificationReusePolicy::RequireCurrentBytes` mechanically supplies an
empty eligible-verification set. Neither the process generation nor the durable
verification index can accelerate the migration scan, while the successful scan
still populates the current process cache for the immediate ordinary operation.

### Disabled scrub no longer means unresolved intent forever

The prior caller collapsed two different policies into one Boolean: whether
rotating payload-byte scrub work was enabled, and whether a durable write-ahead
record needed to be reconciled after a stronger complete scan. Returning early
for both made an operator's `0/0` scrub budget preserve damaged, active, or
failure state across every restart. The refactor keeps byte work disabled but
allows one exclusive, metadata-only compare-and-replace settlement when the
snapshot has already supplied the required current-byte proof. Clean absence or
canonical `Idle` state still takes the zero-lease fast path.

### Cloudtainer build retention remains a real source of waste

A stale rev0958 Ninja build was still consuming CPU during this work even though
its source tree was no longer the active revision. It was terminated and all
rev0959 claims are tied to fresh or source-verified build directories. Long-lived
orphan builds are operational noise and can also make source/object provenance
ambiguous; release evidence must continue to bind `CMAKE_HOME_DIRECTORY` to the
exact frozen source.

### Deliberate corruption must obey the cooperative lease boundary

The first Clang ASan/UBSan product run found a validation-oracle defect rather
than a payload-store defect. The configured-service regression used
`O_TRUNC`/write/fsync directly on a digest-named payload while the retained
service was free to begin a shared authoritative scan. Slower sanitizer
instrumentation made the overlap observable: pathname reproof correctly rejected
an entry that changed during validation, so the process exited through the
generic namespace-instability path before the stable byte mismatch could enter
the typed degraded-recovery state machine.

That direct mutation violated the same cooperative owner contract the production
store requires. The regression now opens the exact reader-fenced product
identity basename with `O_NOFOLLOW`, proves the named and opened `(st_dev,
st_ino)` plus single-link regular-file shape, acquires `LOCK_EX|LOCK_NB` with a
bounded retry, re-proves the identity pathname, performs the deliberate in-place
mutation, and proves the lock inode remained exact before unlock. All three
corruption/repair transitions use this helper. A service scan may observe lease
contention, but it cannot observe half of the injected byte image.

The audit also removed a recurring false negative in sanitizer evidence. The
large folder-owner executable intentionally exercises streaming, crash residue,
path races, and many-file convergence; its measured ASan/UBSan runtime crossed
the ordinary sixty-second CTest stall boundary. CMake now retains sixty seconds
for ordinary builds and selects 120 seconds only when
`ANONSYNC_ENABLE_SANITIZERS` is active. This changes test supervision, not product
runtime policy.

### Cooperative lease contention must not destroy the service owner

Linux `flock(2)` is an advisory, cooperative lock. A legitimate writer that
follows AnonSync's store contract can therefore own the exact identity-anchor
`LOCK_EX|LOCK_NB` lease while the peer service reaches a shared scan or an
exclusive scrub transition. The payload-store owner already represented this as
`SyncReplicaFilePayloadStoreLeaseBusyError`, a retryable authority refusal. The
peer-service boundary did not retain that type, so it escaped the run loop and
destroyed the daemon together with its authenticated listener and only operator
status/control endpoint.

Rev0959 maps only that typed refusal to `PayloadStoreLeaseBusyDeferred`. The
step preserves ingress readiness, the listener, the mode-0600 control socket,
network-failure counters, and any active fail-closed integrity alarm. It exposes
`payload_store_lease_conflict_observed`, an exact remaining retry delay, and
separate monotonic counters for real conflicts and clock-only backoff steps. It
does not increment outbound, inbound, or ingress failure backoff.

The first repair retained the process but still relied on the daemon's bounded
250 ms wait and preserved an overdue repair deadline. That allowed the same
local repair to win each scheduler turn and could starve inbound service while a
cooperative writer held the lease. The corrected owner records one steady-clock
`next_payload_store_lease_retry_at`. Initial repair and integrity recovery may
only return clock-only deferrals before it. An established healthy service skips
local repair before it and can enter bounded inbound acceptance. Every real
conflict also sets the next ordinary repair deadline to that exact cutpoint,
which both postpones an overdue repair and advances a distant periodic repair
after an interrupted network session.

A second audit rejected one global state-preserving catch. The failed
nonblocking acquisition consumes no payload-store authority, but an enclosing
network operation may already have crossed an externally visible request or
response cutpoint. Once the lower synchronous stack throws, its partial session
result is unavailable. Rev0959 therefore catches the typed integrity and lease
failures at six explicit service phases. Local repair has a known network
outcome and preserves role. Inbound and outbound phases report
`network_outcome_known=false` rather than inventing exact-peer or handoff
claims. Outbound ambiguity applies the same full-cycle lease used by a successful
handoff and yields to inbound service; inbound ambiguity remains inbound. Both
schedule bounded convergence from fresh durable observation. This is a
conservative duplicate-turn fence, not a claim that the peer definitely observed
the interrupted session.

The authority claim remains deliberately narrow. The failed nonblocking
acquisition itself consumes no payload-store authority. An enclosing
folder-convergence or network turn can have committed independently idempotent
catalog, scan-journal, replica, or peer progress before it later reaches the
contended store. Rev0959 preserves those owners and retries from fresh
observation; it does not claim the whole pass was effect-free, does not invent
cross-owner rollback, and does not assert network-filesystem equivalence.

The configured-service regression supplies a callback that runs while the
corrupting helper still holds the exact product identity inode under exclusive
lease. It repeatedly queries the owner-only status socket and requires the same
PID, healthy readiness in the no-alarm case, advancement of
`payload_store_lease_busy_deferrals`, a positive retry delay, and truthful role
handling: unknown outbound becomes inbound, while unknown inbound remains
inbound. The serialized write then becomes stable current bytes, allowing the
existing typed integrity alarm and same-process recovery regression to exercise
the intended path.

This matches the documented Linux cooperative-lock model. It requires the same
PID, healthy readiness, and fresh-observation semantics without claiming
network-filesystem equivalence: `flock(2)` semantics can differ on NFS and other
remote filesystems, which remain outside the qualified product boundary.
Primary references:

- Linux `flock(2)`: https://man7.org/linux/man-pages/man2/flock.2.html
- Linux kernel mandatory-locking documentation (contrasting advisory locks):
  https://www.kernel.org/doc/html/latest/filesystems/mandatory-locking.html
- CTest `TIMEOUT` property used for bounded instrumented supervision:
  https://cmake.org/cmake/help/latest/prop_test/TIMEOUT.html

### One stale complete observation is restartable, not authoritative

The same failure exposed an adjacent production boundary. The identity lease is
a cooperative writer protocol, not kernel immutability. An operator or same-UID
repair process that ignores it can change a payload while a shared complete scan
is in progress. The scanner already rejected read/fstat, namespace-open,
pathname, sidecar, staged-prefix, and root-directory drift, but those exact
staleness cases escaped as generic terminal exceptions.

Rev0959 gives only those observation-drift cutpoints a private typed
classification. `scan_store_under_lease_or_throw` may discard one such attempt,
re-proves the exact live lock inode, and calls the raw scanner again. The second
call owns a new descriptor-rooted directory cursor and reloads all optional
sidecars. Verification-generation allocation/publication, checkpoint scheduling,
integrity-fault release, scrub-observation promotion, and returned snapshot
authority all remain after the retry loop. The first attempt can synchronize
already-open regular files and the directory for observation durability, but it
cannot grant content authority.

The bound is exactly two total attempts. A second drift propagates, preventing a
non-cooperating writer from converting one service pass into an unbounded retry
loop. The Linux regression watches for the first `IN_ACCESS` on a 32 MiB
payload, changes and restores byte zero, and then requires the successful result
to report one current full hash, zero reuse, and exact final bytes. The
configured-service corruption regression still uses the exact exclusive lease:
its purpose is stable digest-mismatch recovery, whereas this regression owns the
separate observation-staleness frontier.

## What this proves

Within the cooperative Linux owner model, rev0959 proves that a rev0957-or-earlier
reader cannot newly open a successfully migrated store through the legacy
identity name, that migration cannot publish the current name before complete
current-byte proof, and that the exact flock/identity inode survives the rename.
It also proves the migration does not duplicate the successful payload-byte scan
inside the new owner, that the bounded exact-name lane cannot proceed under a
current anchor while an unsupported v1 identity name coexists, and that typed
cooperative payload-store lease contention remains a bounded same-process
deferral rather than destroying the listener and status owner. It also proves
that the local retry gate cannot monopolize the scheduler and that an unknown
outbound network outcome is fenced from duplicate dialing by yielding inbound
for the normal handoff horizon. That last proof is deliberately
acquisition-local and does not claim pass-wide rollback.

## What this does not prove

Rev0959 does not claim power-loss correctness on every filesystem, seamless
mixed-version rolling upgrade, downgrade back to an old binary, hostile same-UID
protection, network-filesystem `flock` equivalence, automatic quarantine or
restore, retention/garbage collection, kernel immutability, filesystem checksum
integration, rename/directory user semantics, changed-block transfer, selective
synchronization, many-share device ownership, cross-platform qualification,
live public Tor/I2P privacy qualification, or completion of the first named
Resilio uninstall workflow.

## Product follow-through

The next integrity work should be operator-facing rather than another hidden
format: one explicit status/recheck/repair action, quarantine and restore rules,
and retention/reachability/garbage collection designed together. The first real
Resilio replacement workload still needs to be named and measured so these
storage mechanisms are judged against actual files, churn, outage, restart, and
recovery expectations.
