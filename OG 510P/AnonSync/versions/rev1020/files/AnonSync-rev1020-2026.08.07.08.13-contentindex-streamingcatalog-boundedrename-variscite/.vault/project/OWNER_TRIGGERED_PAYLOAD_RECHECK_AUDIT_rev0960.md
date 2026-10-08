# Owner-triggered payload recheck audit — rev0960

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. A replacement service cannot ask an owner to wait indefinitely for an
optional rotating scrub after a disk, memory, migration, or operator concern.
The owner needs one ordinary, local operation that says: **read the retained
payload bytes now, report the work truthfully, and keep the same daemon usable
through contention, detection, repair, and convergence.**

Rev0960 adds that vertical slice without creating another daemon, another sync
algorithm, or another payload authority. The command is:

```text
anonsync_sync recheck --socket ABSOLUTE_SOCKET
```

The response acknowledges one process-local request generation. Acceptance is
not completion. Completion, retry, byte work, any integrity alarm, and retained
recovery history are read from the existing owner-only status socket.

## Product boundary

This is deliberately a **payload recheck**, not an unqualified promise that
all filesystem state has been scrubbed.

- Every current digest-named object in the private payload store is opened under
  the existing rooted no-follow/no-mount-crossing authority and completely read
  through SHA-256.
- Process-local and durable verification acceleration are mechanically disabled
  for that complete payload snapshot.
- The exact resulting snapshot is moved into the ordinary folder-convergence
  implementation. The pass may observe the user folder, catalog, remote work,
  and replica through their existing rules; it does not run a second complete
  payload-store snapshot or mutation full scan merely because recheck already
  paid for one.
- The command does not yet offer a subpath, one-digest, one-folder-among-many, or
  background-progress API. One service configuration still owns one share and
  one peer.
- A request generation is process-local scheduling evidence. It is not durable
  across daemon exit and is never payload-content authority.

This naming and nonclaim matter. Syncthing exposes an immediate folder scan via
`POST /rest/db/scan`, including optional folder and subpath selection. That is a
useful product precedent for explicit operator work, but it is not evidence that
AnonSync's private content-addressed payload store has been byte-verified. Rev0960
therefore reports its narrower current-byte proof explicitly rather than
borrowing the broader word “scan.”

## Local control authority

The control boundary remains the existing pathname Unix-domain socket rather
than a signal handler or a second management server.

1. The configured parent directory is opened as an authority and re-proved.
2. The pathname socket is created as an exact owner-controlled socket and forced
   to mode `0600`.
3. Every client is checked through connected Unix peer credentials. Client-side
   status, stop, and recheck responses also bind `server_pid` to the actually
   connected peer when Linux exposes that credential.
4. The only new request bytes are exactly `recheck\n`. Extra bytes, alternate
   spelling, oversized input, timeout, or malformed JSON response fail.
5. The socket worker has no folder, SQLite, network, scheduler, or payload-store
   capability. It can only serialize one action under its mutex: latch drain or
   increment the bounded recheck generation. Drain and generation are plain
   mutex-owned values rather than a second atomic synchronization model.

Linux `unix(7)` documents both pathname-socket permission behavior and
`SO_PEERCRED`. It also warns that pathname-socket permission behavior is not a
portable POSIX security promise. Rev0960 is therefore a Linux/headless product
slice, not a cross-platform control-plane claim. A hostile same-UID process is
also outside the current threat promise.

## One linearized action observation

The adjacent refactor removes the separate `stop_requested()` and
`recheck_request_generation()` getters. The owner thread receives one
`SyncLocalStatusSocketActionSnapshot` under the same mutex that serializes
requests.

That consolidation closes two failure shapes:

- the owner cannot observe drain while accidentally omitting a recheck accepted
  immediately before drain; and
- a future caller cannot recreate that split-read race through convenience
  methods after the original run loop has been corrected.

The same mutex and condition variable bind action publication to the retry wait.
The worker changes the predicate while holding the mutex, releases it, and then
notifies. The owner waits with the exact generation it has already observed.
A request accepted just before the wait is therefore visible to the predicate;
a request accepted after the wait begins notifies it. A caller-supplied future
generation is rejected rather than silently turning a bookkeeping defect into a
full backoff delay.

Drain remains ordered with recheck. A request serialized after drain is rejected
without incrementing the generation. Before terminal status is frozen for *any*
stop reason—not only a client `stop` request—the service owner calls
`seal_actions_for_owner_shutdown()`. That operation latches drain and returns the
final generation under the same mutex. A racing recheck is therefore either
linearized before the seal and represented as completed or pending terminal
work, or linearized after the seal and rejected. Signals, cycle limits, runtime
limits, and ordinary local drain now share that exact acceptance boundary. The
CLI prints the strict structured response in either case; protocol success is
not a claim that the requested work completed.

## Generation and coalescing semantics

Let `R`, `S`, and `C` be the requested, started, and completed generations.
The invariant is:

```text
0 <= C <= S <= R
pending == (R > C)
```

A healthy transition from no pending request to a new request may bypass an old
automatic retry cutpoint so operator intent is responsive. Once an actual
recheck attempt establishes fresh integrity or lease backoff, later requests
coalesce without clearing that cutpoint. A request storm therefore cannot turn
bounded retry into a hot `flock` loop.

One complete proof may settle multiple accepted generations. The target is the
largest generation observed before the attempt starts. Requests accepted while
the owner is already performing that proof remain pending for a later proof;
rev0960 does not claim that bytes read before a request was accepted satisfy that
request.

The counters distinguish:

- accepted generations observed by the service owner;
- generations coalesced into already-pending work;
- actual attempts;
- successful completions;
- completions that also recovered an integrity fault;
- exact snapshot handoffs; and
- either possible duplicate complete-scan route.

## Current-byte authority path

`SyncReplicaFilePayloadStore::snapshot_rechecking_current_bytes_or_throw()` is a
thin public name over the ordinary complete snapshot implementation with
`PayloadVerificationReusePolicy::RequireCurrentBytes`.

The complete scanner still owns all of the important proof:

- exact current identity/lease anchor and minimum-reader generation;
- independent rooted directory cursor;
- bounded namespace inventory and reserved-name classification;
- private single-link regular-file type, owner, mode, device, and mount checks;
- stable descriptor metadata before and after the read;
- exact digest-name comparison;
- final pathname and directory reproof;
- configured entry, payload, aggregate, and transient capacity; and
- one bounded stale-observation retry before any snapshot authority publishes.

For an explicit recheck, the implementation additionally asserts that reused
entry and byte counts are zero and that hashed entry/byte counts equal the exact
snapshot totals. This assertion turns “disable acceleration” from an intention
into an executable invariant at the returned authority boundary.

`ReadOnlyInspect` cannot invoke the operator recheck path because a forensic
owner is intentionally byte-cold and mutation-free. Writable service ownership
is required.

## Exact handoff into ordinary convergence

The first implementation risk was obvious waste: perform a forced complete
payload scan, discard it, and let ordinary convergence immediately enumerate and
hash the same private namespace again.

Rev0960 instead moves the exact `SyncReplicaFilePayloadStoreSnapshot` into
`run_convergence_pass_with_payload_snapshot_or_throw()`. The existing exact-owner
handoff rules remain load-bearing: folder identity, retained store owner,
verification-cache identity, owner thread, root attestation, path, limits, and
integrity epoch must all match. Durable identity bytes alone are insufficient.

The pass reports:

```text
payload_recheck_snapshot_handoffs
payload_recheck_convergence_snapshot_observations
payload_recheck_convergence_mutation_full_scans
```

The real-process oracle requires one handoff and zero for both duplicate routes.
The complete snapshot is not treated as a substitute for catalog, local-folder,
remote-work, replica, or terminal-cutpoint reproof; it replaces only the payload
observation already paid for.

The status refactor also removes a second form of waste and drift: live and
terminal `payload_recheck` JSON are now emitted through
`render_sync_replica_peer_service_payload_recheck_status_json()`. The common
real-process terminal parser now rejects duplicate object keys, matching the
already-strict live command oracle instead of silently accepting parser-dependent
operator evidence. A schema change
or field correction has one renderer rather than two hand-maintained copies.

The adjacent package audit found the same duplication pattern in release policy:
the rev0960 mandatory-file set had been inserted twice. Set union made the
runtime result look harmless, but two textual policy branches were latent drift.
The verifier now has one branch and the structural audit requires its occurrence
count to be exactly one.

## Contention, mismatch, and recovery

Linux `flock(2)` locks are advisory and associated with an open file description.
AnonSync uses the exact reader-fenced identity inode as its cooperative anchor.
A nonblocking exclusive writer held by another legitimate same-host operation
therefore causes typed lease contention rather than generic corruption.

For an explicit recheck:

- lease contention retains the same daemon, listener, owner-only socket, route,
  ingress state, active integrity alarm, and pending generation;
- one bounded service-owned retry cutpoint prevents a hot lock loop;
- a later accepted generation coalesces without defeating that new backoff; and
- the failed lock acquisition grants no payload-store authority, although an
  enclosing idempotent network or convergence turn may already have committed
  independent progress and is therefore re-observed rather than “rolled back.”

If current bytes do not match their digest name, the same typed payload-integrity
exception used by background scrub and ordinary convergence enters the retained
fail-closed service state. Readiness becomes false, synchronization authority is
withheld, the exact expected/observed digest pair is exposed, and the accepted
operator generation remains pending.

After external repair, the pending explicit recheck again forces current bytes.
Only successful ordinary convergence of that exact snapshot may:

- advance `C` to the target generation;
- clear the active fault;
- retain immutable process-local recovery history;
- refresh native-I2P readiness at the restoration cutpoint; and
- restore ordinary scheduling.

Automatic integrity recovery and operator recheck now share one completion
helper. They differ only in the snapshot acquisition policy and accounting.
This avoids two subtly divergent implementations of the authority-restoration
cutpoint.

## Mechanical process oracle

The configured-service regression exercises the shipping executable rather than
only a C++ seam:

1. Start two linked peer services and converge a real nested file.
2. Hold the exact product v3 identity inode under an exclusive writer lease.
3. Send two CLI `recheck` requests and require exact PID-bound generations 1 and
   2.
4. While the lease remains held, query status and prove one pending coalesced
   obligation, one typed newly observed lease conflict, bounded retry, same PID,
   retained socket, and truthful network-outcome classification.
5. Under that same exclusive lease, replace a digest-named object's bytes with a
   stable wrong image.
6. Release the lease and require the pending explicit recheck to detect the
   exact mismatch and revoke readiness without process exit.
7. Change the corrupt image again and prove durable-persistence presentation is
   not falsely transferred to a different observed digest.
8. Restore the exact bytes under the same writer boundary.
9. Require the same PID to force-read current bytes, complete generation 2,
   report at least one hashed object and the expected bytes, hand the exact
   snapshot once into convergence, perform zero duplicate complete payload scans
   and zero mutation full scans, restore readiness, and retain exact recovery
   history.
10. Drain cleanly and prove socket removal.

The focused local-socket test separately proves strict request bytes, generation
advance, wait wakeup, coalescing prerequisites, client-drain ordering, owner-side
shutdown sealing, idempotent sealing, post-seal rejection without generation
advance, continued read-only status, PID binding, malformed response rejection,
namespace replacement rejection, and mode/parent checks.

## Research-informed product comparison

Primary references consulted for this slice:

- Syncthing, `POST /rest/db/scan`: an established replacement-class product
  exposes explicit immediate scan as an operator action and allows folder or
  subpath selection. AnonSync still lacks that selection and must not imply it.
  <https://docs.syncthing.net/rest/db-scan-post.html>
- Linux `unix(7)`: pathname sockets, Linux permission behavior, and
  `SO_PEERCRED`; the page explicitly warns that socket-file permission behavior
  is not portable POSIX security. <https://man7.org/linux/man-pages/man7/unix.7.html>
- Linux `flock(2)`: shared/exclusive nonblocking locks, open-file-description
  association, advisory semantics, and network-filesystem caveats.
  <https://man7.org/linux/man-pages/man2/flock.2.html>
- systemd `sd_notify(3)`/service reload guidance: long-lived services can expose
  explicit state transitions to the service manager. Rev0960 does not misuse a
  configuration reload signal for a data-integrity operation; it keeps the
  command on the owner-only socket and continues ordinary READY/fault status.
  <https://www.freedesktop.org/software/systemd/man/sd_notify.html>

## What this proves

Rev0960 proves, within the tested Linux/headless boundary, that a local owner can
request a complete current-byte payload proof from the running service; that the
request is strictly admitted, generation-accounted, coalesced, and backoff-safe;
that shutdown has an exact final admission cutpoint; that the exact proof enters
the existing convergence algorithm without an immediate duplicate payload scan;
and that stable corruption can be diagnosed and repaired in the same PID while
the owner-only control endpoint remains available.

## What this does not prove

Rev0960 does not provide durable command queuing across daemon exit, per-path or
per-folder selection, live byte-progress events, cancellation, parallel scrub,
filesystem-wide forced reads, quarantine, automatic restore, bounded version
history, reachability pins, garbage collection, hostile same-UID isolation,
portable Unix-socket security, network-filesystem lock equivalence, universal
power-loss behavior, rename/directory/metadata semantics, many-share ownership,
selective sync, live public Tor/I2P privacy qualification, or a measured first
Resilio uninstall workflow.


## Validation evidence

GCC 14.2.0 Debug completed a fresh 527/527-edge graph and exact-source
no-work re-attestation. The complete 258/258 registry passed serially in
134.10 seconds; the independent 39/39 product lane passed in 54.26 seconds.
Focused suites passed 84 resumable-SHA, 19 scrub-state, 26 verification-index,
519 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-
operation, 296 SQLite-owner, 360 folder-owner, 110 sync-once, 2043 TLS, 17
integrity-evidence, and 69 local-status-socket checks.

Clang 17.0.0 ASan/UBSan completed a fresh 238/238-edge product graph and
exact-source no-work re-attestation. All 39/39 product tests passed serially
with leak detection in 124.68 seconds, with no retained compiler, linker,
sanitizer, runtime-error, or leak diagnostic.

The structural authority audit passed 166/166 checks. The exact rev0959 parent
SHA-256 matched and passed 41/41 wrapper-aware ZIP checks. The binary-aware
rev0960 patch reconstructed 16/16 changed active files byte-for-byte and by
mode. The active implementation projection binds 567 files / 25,420,532 bytes
at SHA-256 61fed36a59412827b9aec3e5d6604c37fecf5107de647cadef28422bf4086788.

These results establish the tested Linux/headless boundary only. The package
publication checks remain separate from semantic runtime tests and must all pass
against the exact final wrapper before release.
