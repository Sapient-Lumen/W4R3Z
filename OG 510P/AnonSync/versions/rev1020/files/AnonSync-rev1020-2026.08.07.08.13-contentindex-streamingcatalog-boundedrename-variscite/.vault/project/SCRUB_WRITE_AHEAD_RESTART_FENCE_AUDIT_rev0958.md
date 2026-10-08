# Scrub write-ahead restart fence audit — rev0958

## Heart of the mission

AnonSync exists to replace Resilio Sync with one dependable C++ folder-sync
product. Integrity machinery is valuable only when it protects ordinary folder
convergence without creating unbounded work, unexplained outages, or a second
storage engine. Rev0958 closes a restart authority gap in the retained payload
store and refactors the scrub transition boundary so the ordering is explicit,
reviewable, and mechanically exercised.

## The concrete restart gap

Rev0954 made an exact unchanged POSIX observation reusable through a durable
verification checkpoint. Rev0955 added bounded rotating byte scrubbing so latent
content damage can eventually be found even when inode, size, mode, ownership,
link count, mtime, and ctime appear unchanged. Rev0955 also installed an
allocation-free process witness at the exact mismatch cutpoint, and rev0956 made
the service remain alive but fail closed while recovery re-proves current bytes.

One composition remained unsafe across process loss:

1. a durable verification-index entry says digest-named payload D is valid for
   exact metadata M;
2. an optional scrub begins reading D and finds bytes whose digest is not D;
3. the process-local integrity witness is installed;
4. publication of the best-effort terminal `IntegrityFailure` record fails, or
   the process dies after detection but before that record is durable;
5. the process-local witness disappears with the process;
6. a fresh owner observes the same metadata M and can reuse the stale durable
   verification-index entry; and
7. its immediate optional scrub can be deferred because another cooperative
   process holds the shared payload-store lease.

The fresh owner could therefore return an authoritative complete snapshot before
re-reading the contradictory bytes. The bug required three individually valid
features—restart acceleration, best-effort scrub evidence, and cooperative
bounded-work deferral—to compose in the wrong order. Retrying scrub sooner is not
a proof: lease contention, scheduling limits, publication failure, or another
bounded frontier can defer optional work again.

## Required invariants

Rev0958 makes these ordering rules explicit:

1. **Intent before read.** Before the first byte of a newly selected payload is
   opened or read for scrub, a checksum-framed durable `Prepared` record for that
   exact digest, exact metadata, generation, and initial SHA-256 checkpoint must
   be committed and re-observed under the live exclusive store lease.
2. **No proof from intent.** `Prepared` and `Progress` are crash witnesses and
   scheduling state, never content authority.
3. **Fresh-process reproof.** A fresh process observing `Prepared` or `Progress`
   for digest D may not use the durable verification index for D. Its ordinary
   complete scan must hash current bytes before returning authority, even when
   the optional scrub attempt is later deferred.
4. **Narrow same-process acceleration.** An owner that either committed and
   re-observed the active record, or completed a current-byte scan while that
   exact record was frozen, may reuse only its process-local verified entry for
   that digest. Durable-index reuse remains forbidden while the record is
   active.
5. **Exact replacement fence.** Same-process acceleration is valid only while
   the active state value and the state file's complete eleven-field POSIX
   observation both equal the committed observation. Replacement by another
   process cannot borrow the witness.
6. **Mismatch first revokes.** A completed mismatch installs the fixed-width
   process integrity fault and clears the active same-process acceleration before
   allocating terminal strings, serializing failure evidence, or constructing
   the typed exception.
7. **No read after uncertain intent publication.** If exact publication or
   re-observation of `Prepared` cannot be proved, the optional attempt returns a
   publication deferral without opening or reading the selected payload.

These rules do not make the scrub state a write-ahead log for payload mutation.
Payloads remain immutable digest-named objects under the existing rooted writer
lease. The record is a small integrity-read intent whose sole authority effect is
conservative: it disables stale metadata acceleration for one active payload
after restart.

## Canonical `Prepared` state

`SyncReplicaFilePayloadScrubStateDisposition` now has four values while retaining
the established encodings for the first three:

- `Idle = 1`;
- `Progress = 2`;
- `IntegrityFailure = 3`; and
- `Prepared = 4`.

A canonical `Prepared` record must contain:

- the exact store identity digest and identity-marker metadata;
- a valid nonzero generation;
- the selected lowercase SHA-256 payload basename;
- the selected payload's exact private regular-file metadata;
- offset zero;
- the initial resumable SHA-256 checkpoint with zero total bytes; and
- no observed terminal digest.

A zero-byte payload is valid in `Prepared`: there is still a real interval
between publishing intent and finishing the digest comparison. `Progress`
continues to require a strict interior offset, and `IntegrityFailure` continues
to require exact completion and a different reproducible terminal digest. The
fixed-size v1 record width remains unchanged because the disposition already had
an encoded byte and all active fields already existed.

This source does **not** claim downgrade compatibility. An older binary does not
understand disposition 4 and cannot be relied on to preserve this new restart
fence. Downgrade therefore requires an operator-controlled cold verification
procedure rather than reuse of rev0958 acceleration records. A future on-disk
format negotiation policy should make that lifecycle explicit before general
upgrade/downgrade support is advertised.

## Exact publication and re-observation refactor

The former publication helper returned a Boolean describing whether the desired
record appeared to commit. That was enough for best-effort terminal evidence but
not for a pre-read authority fence. Rev0958 changes
`publish_payload_scrub_state_with_reconciliation()` to return the exact committed
regular-file metadata when—and only when—the checksum-framed desired state was
published and then re-opened, parsed, identity-checked, and byte-compared under
the still-live exclusive lease.

The helper follows one rule for normal success and exception reconciliation:
read back the exact record and accept only exact desired bytes bound to the
current store identity. A rename-cutpoint exception may therefore reconcile to a
successful commit, while a missing, replaced, malformed, or different record is
not mistaken for the requested transition.

`advance_payload_scrub_from_snapshot_or_throw()` centralizes every state
transition through one `publish_working` closure. It increments the generation,
requires exact publication/re-observation, records the exact state-file metadata
in the process witness, and only then updates the expected observation for the
next transition. Newly selected work publishes `Prepared` before
`open_store_file_or_throw()` or any `pread()`. Partial work advances to
`Progress`; completion advances to `Idle`; mismatch tries to replace the active
record with `IntegrityFailure` after process revocation is already installed.
If terminal publication is lost, the committed `Prepared` or `Progress` record
remains the restart fence.

This refactor removes several ad hoc Boolean branches and makes the safety order
a local property of one function. It also prevents a subtle future regression in
which code could treat “rename may have happened” as permission to read without
proving the exact committed state.

## Reuse matrix

The complete scanner now applies this matrix to the active digest:

| Durable scrub state | Exact same-process state-file witness | Process cache | Durable verification index |
|---|---:|---:|---:|
| `Idle` / no usable record | not applicable | exact metadata may reuse | exact metadata may reuse |
| `Prepared` or `Progress` | yes | exact metadata may reuse | forbidden |
| `Prepared` or `Progress` | no | forbidden | forbidden |
| matching `IntegrityFailure` | not applicable | forbidden | forbidden |
| process integrity fault | not applicable | forbidden | forbidden |

The same-process exception is deliberately narrow. This owner has already
completed a current hash for the exact payload observation and has either
committed/re-observed the active scrub record or kept that exact record frozen
through the complete scan. Reusing the process generation avoids turning
a one-minute scrub throttle into a whole-file rehash on every service pass. A
fresh process has neither fact and must hash.

After a successful complete scan, the owner refreshes the active witness only if
the exact parsed active state and exact state-file observation still match. Any
absence, malformed state, replacement, terminal state, or mismatch clears it.
The witness is fixed-width and trivially copyable, so maintaining it does not add
an allocation-bearing escape hatch near the integrity boundary.

## Mechanical restart regression

The focused payload-store test constructs the dangerous composition directly:

1. create a digest-named payload and a valid durable verification-index entry;
2. alter the payload bytes while restoring the entire canonical POSIX metadata
   projection so the index appears reusable;
3. publish a valid `Prepared` record for that exact digest and metadata;
4. fork a child that holds a shared `flock` on the store identity marker;
5. open a fresh payload-store owner; and
6. request an ordinary complete snapshot.

The shared lock is important. It permits the complete scanner's shared lease but
mechanically prevents the later optional scrub from acquiring its fail-fast
exclusive lease. Thus a passing test cannot be explained by the scrub simply
running again. The fresh complete scan must reject the stale durable index,
rehash the active payload, and throw the exact typed integrity error with
`failure_persisted == false`; the original `Prepared` record remains in place.

The existing rotating-scrub test was sharpened at the adjacent performance
boundary. A same-owner throttled pass must report zero newly hashed entries, one
process-cache reuse, and zero durable-index reuse. Each owner restart while
`Progress` is active must hash the payload once in the ordinary scan; after the
scrub returns to `Idle`, the next cycle may again use the durable index. This
proves the fence is restart-conservative without making a live service reread the
whole payload on every bounded attempt.

The state-codec test independently proves canonical `Prepared` round trips for
nonempty and zero-byte payloads and rejects consumed bytes or a terminal digest
in that disposition.

## Adjacent audit findings

### Best-effort terminal evidence was doing two jobs

The terminal `IntegrityFailure` record was intentionally described as
best-effort operator/scheduling evidence, but restart safety also implicitly
depended on it. Those responsibilities conflict: best-effort publication cannot
be the sole durable authority revocation. `Prepared` separates them. The small
pre-read fence is mandatory for starting new byte work; the richer terminal
record can remain best effort because a lost terminal transition leaves the
mandatory active fence behind.

### A process throttle is not an integrity boundary

The optional scrub's schedule and lease are performance controls. Neither may be
used to decide whether stale metadata is authoritative. The complete scanner now
consumes the durable active state independently of whether scrub is enabled,
due, or able to acquire its exclusive lease.

### Research-informed comparison: persistent progress needs a conservative restart interpretation

Btrfs records scrub status and can resume an interrupted scrub from saved
progress. OpenZFS periodically checkpoints scan progress so long-running scans
can survive reboot. Those systems have different data structures and checksum
authorities, but they reinforce the useful engineering pattern: progress state
must be persistent, bounded, and interpreted conservatively after interruption.

References:

- https://btrfs.readthedocs.io/en/latest/btrfs-scrub.html
- https://openzfs.github.io/openzfs-docs/man/master/4/zfs.4.html

PostgreSQL's write-ahead-log rule is a closer ordering analogy: information
needed for recovery is made durable before the corresponding data-page change
may become durable. AnonSync is not implementing database WAL here, and the
payload read does not mutate the payload. The transferable principle is only the
ordering: publish the recovery-relevant intent before performing an operation
whose outcome could otherwise disappear at process loss.

Reference:

- https://www.postgresql.org/docs/current/wal-intro.html

## What this proves

Rev0958 proves, within the tested cooperative POSIX model, that:

- newly selected scrub work cannot read a byte before exact durable `Prepared`
  publication and re-observation;
- a fresh owner cannot use the durable verification index for the active digest;
- complete shared scanning detects metadata-hidden corruption even when the
  optional exclusive scrub is mechanically blocked;
- a live owner retains exact process-cache acceleration only after exact record
  re-observation plus either its own commit or a complete current-byte scan;
- lost terminal failure publication leaves a conservative active record; and
- mismatch revocation still precedes allocation-bearing failure presentation.

## What this does not prove

This revision does not provide hostile same-UID protection, kernel-enforced file
immutability, storage-device power-loss proof, filesystem checksum integration,
downgrade safety, quarantine, restore, retention, garbage collection, or a
complete operator repair workflow. POSIX metadata remains a change witness, not
content cryptography. `fsync` behavior still depends on the operating system,
filesystem, mount, device, and failure model. Lexical audit checks are not a
semantic proof.

The power-loss boundary deserves a dedicated harness. Useful next work includes
fault injection at every publish/open/read/finalize cutpoint, process killing
between them, remount or virtual-block-device tests where available, and exact
proof that each restart either forces a current hash or retains an active fence.

## Product and performance follow-through

The current correction deliberately chooses safety over one bounded duplicate:
a fresh owner hashes the active payload in its ordinary complete scan, then may
resume the scrub and reread the next bounded range. The completed current-byte
proof could eventually be handed into scrub progression, just as rev0957 handed
integrity reproof into ordinary convergence, but only with exact owner, metadata,
state-generation, offset, and SHA-256 continuation binding. That optimization is
not needed to close the authority gap and should be implemented only with a
mechanical no-second-read oracle.

A broader durable change-sequence index could eventually replace repeated
namespace traversal, while the complete descriptor-rooted scanner remains the
rebuild oracle. The integrity intent could then become one record in a compact,
versioned recovery journal with explicit migration and downgrade policy. Those
changes should be driven by the first named Resilio uninstall workload rather
than by storage-proof growth for its own sake.
