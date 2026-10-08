# Durable byte-bounded payload scrub audit — rev0955

## Heart of the mission

AnonSync exists to replace Resilio Sync in a named real workflow with one
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P are routes
into the same authenticated synchronization semantics. Durable evidence,
cryptographic work, and audit structure matter only when they make the owner's
files safer, recovery more dependable, or the replacement product more usable.

Rev0954 made exact unchanged payload observations reusable across restart. That
removed avoidable cold-start hashing, but it deliberately did not detect
metadata-preserving byte corruption. Rev0955 adds the missing bounded revalidation
owner without changing the complete descriptor-rooted scanner's authority.

## Why restart checkpoints were insufficient

The v1 payload verification checkpoint is acceleration, not authority. It binds
the exact store identity marker and eleven-field POSIX metadata for each
immutable digest-named payload. An unchanged record may nominate byte-hash reuse,
but storage corruption or a cooperating-model violation can preserve or recreate
metadata. Therefore a payload store that never rereads exact observations can
retain latent corruption indefinitely.

A useful integrity owner must eventually cover every retained byte. It cannot be
bounded only by entry count: one payload may be many gigabytes. It also cannot
keep only a process-local cursor: restart would repeatedly reread a stable prefix.
The rev0955 owner is bounded by both bytes and distinct entries per attempt and
persists exact SHA-256 continuation state.

## Acceleration versus authority

The distinction is load-bearing:

1. Complete snapshot scanning still enumerates every root entry, rooted-opens and
   stats every payload, proves privacy and capacity, and hashes every observation
   that lacks exact admissible reuse evidence.
2. The rotating scrub runs only after the complete shared observation lease is
   released. It acquires its own exclusive cooperative mutation lease and
   re-proves the frozen directory and state-file cutpoints.
3. Partial scrub progress is scheduling evidence only. It is excluded from the
   canonical payload snapshot digest and cannot satisfy a payload lookup,
   inventory, transfer, or publication proof.
4. A terminal digest becomes an exact-extent integrity alarm only after extent
   completion, post-read `fstat`, pathname reproof, and lease reproof. It is
   compared with the independently trusted digest basename, but continuation
   across attempts is not a point-in-time byte image.
5. A stored `IntegrityFailure` record is not proof of current corruption. On the
   next complete scan it forces one current full-byte hash of the same exact
   pathname observation. That current hash either reproduces the mismatch or
   disproves and clears the stale alarm.

## Authority sequence

For an ordinary writable snapshot, the production sequence is:

1. prove the retained root authority and exact identity marker;
2. acquire a shared observation lease;
3. completely enumerate, classify, capacity-check, and re-prove the payload root;
4. construct the canonical snapshot and perform the final shared-lease cutpoint;
5. release the shared lease;
6. when enabled and process scheduling permits, try one exclusive scrub attempt;
7. re-prove root, identity marker, frozen directory status, and exact scrub-state
   metadata before reading payload bytes;
8. read no more than the configured byte budget and touch no more than the
   configured distinct-entry budget;
9. re-prove descriptor, pathname, and lease observations;
10. atomically create or expected-replace the fixed-size scrub state, reconciling
    a possible post-rename exception by rereading the exact record;
11. only then perform the independent best-effort verification-checkpoint refresh.

`ReadOnlyInspect` never advances scrub state. It remains the acceleration-cold
forensic surface: each complete inspection bypasses both metadata caches,
hashes every payload byte, and does not mutate the private namespace.

## Byte and entry bounds

`SyncReplicaFilePayloadStoreLimits` now carries
`max_scrub_bytes_per_attempt` and `max_scrub_entries_per_attempt`. Both are zero
when scrub is disabled; asymmetric limits are rejected. The canonical shipping
helper enables 4 MiB and four distinct entries per snapshot attempt. The byte
limit is checked before every `pread(2)` and the returned count is checked against
both the remaining payload extent and remaining attempt budget.

The entry bound limits distinct payload observations, including a resumed active
payload. Zero-length payloads consume an entry but no byte budget. The state file
has a fixed exact size and its atomic writer residue must fit the existing
transient-entry and transient-byte capacity contract before optional work begins.
Capacity refusal leaves the complete payload snapshot authoritative and reports a
noncanonical deferral.

## Resumable SHA-256 continuation

A small provider-independent FIPS 180-4 SHA-256 leaf exposes a stable
`ResumableSha256Checkpoint`: eight hash words, a canonical 64-byte tail, total
byte count, and buffered-byte count. The largest admitted byte-aligned message is
`(2^64-1)/8`, because SHA-256 encodes the terminal bit length in 64 bits.
Malformed, inconsistent, noncanonical, and overflowing checkpoints are rejected.

The ordinary content-digest owner remains OpenSSL EVP. The focused continuation
test uses NIST vectors, the one-million-`a` vector, every critical padding
boundary, many split/restart cutpoints, malformed-state cases, and the independent
OpenSSL-backed digest as an oracle. The continuation state is computation
progress, never an independently trusted digest proof.

References:
https://csrc.nist.gov/pubs/fips/180-4/upd1/final
https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf

## Temporal scope of a resumed digest

One scrub digest may be assembled from ranges read by several processes and
several exclusive-lease intervals. Exact metadata equality and the cooperative
immutability rule make that continuation useful: ordinary writes change mtime
and ctime, and AnonSync writers never replace an existing digest-named payload.
A changed observation discards partial state and restarts from byte zero.

That does not turn the accumulated digest into a simultaneous snapshot of every
byte. Latent media faults, a noncooperating writer, privileged timestamp
manipulation, or storage behavior outside the model can make different ranges
represent different moments while the retained observation appears unchanged.
Therefore a completed mismatch is reported immediately as an integrity alarm,
but the durable witness is never current corruption authority. The next complete
scanner pass bypasses both metadata caches and obtains one current full-file
hash before retaining or clearing the failure.

Linux documents that writes update mtime and ctime and that setting timestamps
also updates ctime; these timestamps are useful change witnesses, not content
cryptography or hostile-writer protection.

References:
https://man7.org/linux/man-pages/man7/inode.7.html
https://man7.org/linux/man-pages/man2/utimes.2.html

## Durable state and crash ordering

`.anonsync-payload-scrub-state-v1` is a private, single-link, fixed-size,
checksum-framed record. It binds the exact store-identity digest and canonical
identity-marker metadata, generation, completed cycle count, lexicographic cursor,
active payload digest and metadata, exact offset, resumable SHA-256 state, and an
optional terminal observed digest.

The three dispositions are `Idle`, `Progress`, and `IntegrityFailure`. Validation
requires one canonical representation for each form. In particular, `Progress`
must be strictly inside the payload extent and cannot contain a terminal digest;
`IntegrityFailure` must be at exact completion, must contain a different lowercase
SHA-256 digest, and that digest must reproduce from the stored completed hash
state.

Publication uses the existing rooted atomic create/expected-replace owners. A
torn, malformed, stale-identity, or otherwise unusable record is disposable and
causes bounded work to restart; it does not invalidate a complete payload
snapshot. An exception after the rename cutpoint is reconciled by rereading and
comparing the exact checksum-framed record under the still-live exclusive lease.

## Cyclic fairness and the one-entry rollover defect

Selection is lexicographic after `cursor_after_content_sha256`. Reaching the end
increments `completed_cycles`, clears the cursor for the newly entered cycle, and
selects the first current entry. Partial progress resumes the exact active digest
and byte offset after restart.

The first implementation exposed a severe one-entry liveness defect during audit.
At wraparound it incremented the cycle but retained the prior cycle's final cursor,
then selected that same digest as active. The state codec correctly rejects
`active == cursor`, so publication failed and every fresh owner reread the same
prefix forever. Rev0955 clears the cursor at cycle entry. A 37-byte payload under
a 10-byte budget now proves durable offsets 10, 20, 30, terminal completion, and
progress into the next completed cycle.

This is cyclic fairness over the payload set observed by each complete snapshot,
not point-in-time namespace isolation. Insertions, removals, or replacements are
ordinary later-snapshot work.

## Failure witness is not proof

When a completed scrub digest differs from the digest basename, the owner tries
to persist `IntegrityFailure` and throws
`SyncReplicaFilePayloadStoreIntegrityError`. The typed error carries expected and
observed digests plus the exact `failure_persisted` result. It never deletes or
silently quarantines the sole retained payload.

A checksum-valid failure record can be written by a same-UID actor and therefore
cannot grant corruption authority. A later matching complete scan bypasses all
metadata reuse, hashes the current bytes, and either:

- observes the same mismatch and throws a current typed integrity error, accurately
  reporting whether the matching witness was already persisted; or
- proves repaired bytes, clears the stale failure, and advances the fair cursor.

The second path reuses the scanner's complete full-byte proof and does not hash
the repaired payload a second time inside the optional scrub attempt.

### Process-local witness closes the publication-loss gap

The durable failure record is deliberately best effort. The first implementation
advanced the one-minute process throttle before the scrub attempt and relied on
that record alone to force the next complete hash. If failure publication did
not commit—or if the record disappeared after the typed error crossed the API
boundary—the same live owner still held an exact warm metadata generation. Its
next snapshot could reuse that generation, defer scrub because of the throttle,
and return success even though this owner had just observed contradictory bytes.

Rev0955 retains a second witness in the shared, thread-affine process cache. It
contains only the expected and observed digests and is failure evidence, never
content authority. While live it has five effects:

1. complete leased scans disable both process and durable metadata reuse for the
   exact digest, regardless of metadata drift;
2. mutation preflight scans inherit the same forced current-byte proof;
3. pass-scoped targeted access rejects the exact faulted digest; and
4. verification-checkpoint publication is suppressed; and
5. every future method call on a still-live writable snapshot issued before the
   alarm is rejected.

A successful complete scan clears the witness only after the final lease
cutpoint proves current good bytes or proves the digest name absent. An adjacent
exception-safety audit found that the first witness representation used two
heap-owning strings and advanced the integrity epoch before both allocations were
guaranteed. Allocation failure could therefore leave a changed epoch without the
exact blocking target, or lose publication of the witness entirely. Merely
resetting the scrub throttle was not fail-closed because a later optional attempt
may still defer on lease contention or another bounded-work frontier. The sealed
representation instead owns two fixed inline 64-character digest arrays; its
optional assignment is compile-time `noexcept`, retention is explicitly
nonthrowing, and the epoch advances only alongside an allocation-independent
witness. A deeper pass found that retention was nevertheless still too late:
the scrubber first constructed the heap-owning typed integrity exception, so a
message or digest-string allocation failure could enter the generic catch after
the current bytes had already mismatched. Resumable SHA-256 now provides a
fixed-width terminal form. The scrubber compares that form and retains the
witness at the allocation-free mismatch cutpoint before durable-state string
assignment, failure-record serialization, or typed integrity exception
construction. Once the witness or an exhausted epoch is live, the caller
rethrows every later failure rather than turning it into an optional scrub
deferral. The regression removes a successfully committed durable record after
detection, proves repeated snapshot and mutation failure in the same owner,
repairs the bytes, and proves one complete hash clears the process witness before
warm reuse resumes. A separate allocation-fault regression counts the exact
successful alarm path for the active toolchain, sweeps its allocation-bearing
publication/exception tail, and rejects any returned snapshot after either
durable mismatch publication or process revocation. It also requires at least
one injected `bad_alloc` after the persisted mismatch cutpoint.

The witness deliberately preserves the oldest unresolved digest when a failed
complete scan encounters a different mismatch first. That second path cannot
publish changed metadata, so it remains independently hash-forcing on the next
scan; replacing the original witness would instead permit its unchanged warm
metadata to regain authority after the second path was repaired. A two-payload
ordering regression seeds a later scrub target, removes its durable record,
introduces an earlier changed mismatch, and proves the original target remains
blocked until its own current-byte reproof succeeds.

### Integrity epoch revokes already-issued snapshots

The first process-witness implementation protected future complete scans,
mutation preflights, targeted access, and checkpoint publication, but a snapshot
returned before the alarm retained no link to that witness. Snapshot inventory,
canonical digest, and unchanged-metadata range selection could therefore remain
callable after the same owner had observed contradictory bytes.

The cache now carries a monotonically advancing integrity-fault epoch plus the
most recent diagnostic observation. Every writable snapshot shares the cache and
captures the epoch at issuance. Its single state gate rejects authority whenever
an active fault exists, the epoch differs, or the counter has exhausted. Clearing
the active witness after current good-byte or absence proof never rolls the epoch
back, so repair can issue a new snapshot but cannot resurrect one that was live
at detection. The 64-bit overflow case permanently fails closed rather than
wrapping onto an ancient issuance value.

This revocation is deliberately process-local and method-scoped. It reaches all
future calls that require retained snapshot state, including metadata-only
inventory and digest access. It cannot retract values or references already
returned from the snapshot, revoke a payload descriptor already opened and moved
out before the alarm, or communicate across independent processes. The
regression retains an old snapshot, introduces a guaranteed metadata-changing
digest mismatch, and proves both metadata and rooted
methods fail with exact typed evidence, repairs the bytes, and proves only a new
snapshot becomes usable.

That descriptor nonclaim follows the operating-system capability boundary, not
an implementation convenience: Linux `open(2)` specifies that a descriptor's
reference to its open file description is unaffected if the pathname is later
removed or changed to name another file. Closing or replacing AnonSync's
wrapper object therefore cannot retroactively invalidate an integer descriptor
already borrowed by another component; ordinary
C++ values and references already handed to a caller likewise have no recall
mechanism.

Reference: https://man7.org/linux/man-pages/man2/open.2.html

The epoch lives in the same intentionally mutex-free owner cache as warm
verification metadata. An adjacent affinity review found that adding the epoch
read to metadata-only snapshot methods had created a new race frontier: those
methods previously needed no filesystem or cache access and therefore had not
proved their documented exact-thread ownership. The single snapshot state gate
now performs the directory authority's cheap process/thread-owner proof before
reading the epoch, and pass-scoped targeted access applies the same ordering
before consulting the active fault. This is an affinity fence, not a mutex;
cross-thread object use remains rejected, while ordinary metadata access does
not pay for a pathname or filesystem reproof. A regression invokes a retained
snapshot's canonical-digest method from a foreign thread and proves rejection
occurs before the mutex-free revocation state is touched.

## Scheduling and availability

One store owner attempts scrub at most once per steady-clock minute. The deadline
is advanced before lease acquisition or I/O so contention and ordinary failure
cannot make a hot snapshot loop retry without bound. A fresh process intentionally
receives one immediate attempt, which allows restart continuation and failure
reproof without a durable wall-clock dependency.

Lease contention, stale snapshot cutpoints, transient-capacity pressure, state
publication failure, and other optional-attempt failures are distinct scrub report
dispositions. None changes canonical payload truth. A completed exact-extent
mismatch is the sole optional result promoted to an exception; durable evidence
then forces the complete scanner's current full-byte reproof.

## Audit/refactor boundary

Rev0955 moves three brittle concerns out of the already large payload-store owner:

- `resumable_sha256.{hpp,cpp}` owns stable SHA-256 continuation and its message
  ceiling;
- `sync_replica_file_payload_scrub_state.{hpp,cpp}` owns the fixed-width state
  grammar, exact checksum framing, identity binding, and canonical disposition
  validation; and
- `sync_posix_regular_file_snapshot_codec.{hpp,cpp}` owns the shared fixed
  88-byte big-endian projection and private mode-0600 single-link validation used
  by both the rev0954 verification index and rev0955 scrub state.

The shared codec preserves both existing v1 byte layouts while removing two
copies of the same eleven-field serializer, parser, and validator. The new leaf
is independently compiled and directly exercised by the verification-index
matrix; all three leaves are included in the product lane and explicit sanitizer
compile inventory, while executable tests retain sanitizer final-link closure. The payload
store composes them through the existing rooted directory authority and atomic
publication owners rather than introducing a second filesystem boundary.

The structural audit also inventories both production `fdopendir` paths. The
complete scanner and staged-prefix observer recognize and finally re-prove the
scrub-state basename; pre-bootstrap product adoption rejects a preexisting scrub
record rather than binding attacker-selected scheduling evidence to a new store.

An adjacent documentation audit found a different kind of accumulated waste: a
rev0881 section still called itself the unqualified ‘largest product gap’ even
though later revisions had composed the service it said was missing. The section
is now explicitly historical and superseded. This preserves useful provenance
without allowing stale mission language to become current planning authority.

## Filesystem research and future qualification

Linux fs-verity can make a file read-only after building a Merkle tree, verify
reads in the kernel, and expose a measurement. It may eventually provide a
qualified on-read integrity accelerator, but it is filesystem-specific, changes
publication and copy semantics, and does not replace AnonSync's portable SHA-256
content identity or rooted namespace proof.

Reference: https://docs.kernel.org/filesystems/fsverity.html

Btrfs scrub validates filesystem data and metadata checksums across a device and
can repair from redundant copies. Btrfs also verifies checksums during ordinary
reads. That is valuable storage-layer defense, but it is not an application-level
proof that a digest-named payload contains the digest in its basename, and it is
not portable across supported filesystems.

References:
https://btrfs.readthedocs.io/en/latest/Scrub.html
https://btrfs.readthedocs.io/en/latest/Checksumming.html

## Adjacent process-harness audit: two readiness frontiers

The retained service owner can expose its authenticated public listener before
the configured owner-only status socket has completed construction. One
provisioning process proof waited only for the listener, observed very fast tree
convergence, and then issued `stop --socket` during that narrow startup window.
The missing socket was a harness readiness race, not evidence that convergence
or the service owner had failed. The first correction proved the status socket
at startup, but loaded registry validation exposed a second temporal gap: a
bounded 24-second convergence wait ran inside a 30-second service lifetime, so
orderly runtime shutdown could remove the endpoint before drain.

Rev0955 centralizes `wait_for_service_status_socket`: it keeps checking process
liveness, rejects symbolic and non-socket paths, and requires exact mode 0600.
The provisioning proof now establishes both startup control endpoints, uses a
bounded 60-second service horizon, and invokes the same helper again for the
source immediately after convergence and before `stop --socket`. This is
intentionally separate from `wait_for_service_listener`. Public data-plane
readiness is not local control-plane readiness, neither witness substitutes for
the other, and an observation made before intervening work is not authority at
a later cutpoint.

## Adjacent validation audit: measured stress timeout

The complete generated network-model corpus passes under Clang ASan/UBSan in
about 21 seconds in this cloudtainer, but it inherited a generic 20-second
CTest timeout. That produced a false sanitizer failure while the generated
operations were still making bounded progress. Rev0955 retains the exact
corpus and gives it the same 60-second qualified frontier already used by the
heavy graph oracle. The structural audit now binds both stress targets to
that explicit frontier so future releases do not hide a timeout by deleting
coverage or depending on ad hoc direct execution.

## Adjacent I2P ingress oracle audit: require the connector attempt

The retained native-I2P process proof includes a negative control: while the
I2P ingress bridge is absent, an independent direct pull must fail without
reaching the service's TLS dispatcher. The original negative control allowed
only three seconds for a complete local repair pass plus connector scheduling.
Under concurrent compiler load it could terminate at
`command_deadline_before_pull`; that result proved neither a direct-route attempt
nor the intended no-handshake boundary.

Rev0955 changes only the test horizon: eight seconds for the bounded command and
15 seconds for the outer process guard. The oracle still rejects a zero exit
status, still requires a structured reconciliation object, and still rejects a
completed handshake. Five consecutive focused runs passed before the final
registry. This is test reliability, not a relaxation of route semantics.

## What this proves

The implementation and compiled matrix establish, within the cooperative
same-process/thread and advisory-lease model, that:

- every enabled attempt has strict byte and distinct-entry bounds;
- partial SHA-256 work resumes from exact durable state across owner restart;
- lexicographic cycles advance without stable-prefix starvation, including a
  one-entry store;
- damaged or identity-mismatched state is disposable rather than authoritative;
- a completed exact-extent mismatch raises an integrity alarm and can retain an
  exact diagnostic witness;
- a matching witness forces current byte reproof and repaired bytes clear it;
- a newly observed mismatch permanently revokes older live writable snapshots,
  while repair may authorize only a replacement snapshot;
- optional work cannot change canonical snapshot identity;
- forensic inspection remains nonmutating and acceleration-cold while still
  hashing every payload byte; and
- the new leaves are retained through ordinary, product, and sanitizer build
  graphs.

Runtime evidence, sanitizers, and release-package verification remain
load-bearing. The lexical audit is only a source-shape regression tripwire.

## What this does not prove

This is not hostile-writer security. `flock(2)` is advisory; the state checksum is
not a MAC; a privileged or same-UID noncooperating actor can cause denial of
service, replace bytes between unproved cutpoints, or manufacture scheduling
records. Rooted no-follow and no-mount-crossing resolution reduce pathname risk
but do not turn the local account into a hostile multi-tenant boundary.

Process-local snapshot revocation cannot claw back a descriptor already moved
out of a snapshot, and another process has its own independent cache and epoch.
Cross-process revocation would require a durable authority protocol rather than
promoting the best-effort scrub record into corruption truth.

This is not a point-in-time snapshot across restart-separated ranges, and it is
not instant corruption detection. Production defaults cover at most 4 MiB and
four entries per eligible snapshot attempt, with a one-minute
same-owner throttle. Time to complete one cycle depends on retained bytes,
snapshot cadence, contention, restarts, and failures. There is not yet an
operator deadline, coverage-age alert, or service-level objective for scrub lag.

The complete snapshot remains O(total indexed namespace) in metadata work.
Rev0955 does not add a durable change-sequence index, eliminate prefix traversal,
or make remote projection incremental. It also does not provide garbage collection, quarantine copies, restore/version retention, reachability pins,
block reuse for changed files, rename identity, empty directories, selective
sync, many-share supervision, polished conflict UX, cross-platform
qualification, or the first measured Resilio uninstall workload.
