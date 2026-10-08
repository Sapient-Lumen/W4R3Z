# Payload-integrity service recovery audit — rev0956

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. A continuously running replacement service must not vanish precisely
when it discovers damage in its private retained payload store. The operator
needs the same process to remain inspectable and stoppable, to identify the
exact failed digest, to stay fail closed while authority is blocked, and to
resume only after current bytes have been re-proved.

Rev0956 therefore stays inside the shipping spine:

```text
payload store -> folder process -> linked-peer service -> anonsync_sync
```

It adds no second daemon, no route-specific integrity behavior, and no competing
synchronization owner. Direct TCP, Tor, and I2P continue to enter the same peer
service and are all blocked by the same payload-authority alarm.

## Failure found

Rev0955 made the storage boundary correctly fail closed. A rotating scrub or a
complete payload scan that observes bytes inconsistent with a digest basename:

1. retains an allocation-independent fixed-width process witness;
2. advances the non-wrapping integrity epoch and permanently revokes older live
   writable payload snapshots;
3. suppresses restart-checkpoint publication for the faulted digest;
4. optionally publishes checksum-framed durable failure evidence; and
5. raises `SyncReplicaFilePayloadStoreIntegrityError`.

The retained service owner did not yet interpret that typed condition as an
operational state. The exception crossed the service command boundary, the
process was destroyed, and teardown removed the owner-only status/stop socket.
The storage reaction was safe, but the product reaction erased the most useful
live diagnostic and forced an external supervisor restart without proving that a
restart could make progress.

The adjacent audit found a second evidence loss in the first owner-level repair:
a successful current-byte reproof cleared the active alarm and retained only
aggregate counters. The exact expected and observed digests—the explanation for
the outage—disappeared at the same moment the service recovered. Rev0956 now
retains the most recent recovered alarm as bounded process-local operator
history. That history is presentation evidence only; it never grants payload or
synchronization authority.

## Owner-level state machine

`SyncReplicaPeerServiceOwner::run_next_or_throw()` is the reusable boundary. It
catches only `SyncReplicaFilePayloadStoreIntegrityError`. Every other exception,
including configuration, allocation, rooted-path, SQLite, protocol, and logic
errors, keeps its prior terminal behavior.

The payload-integrity path has three explicit completed-step dispositions:

```text
payload_integrity_fault_observed
payload_integrity_reproof_backoff_pending
payload_integrity_reproof_completed
```

### Fault observation

The owner copies the canonical expected and observed SHA-256 strings, whether the
durable witness was published, first/last monotonic detection times, and a
saturating detection count. It schedules the next attempt through the same
bounded exponential retry planner used by ordinary peer recovery. The service
step returns normally, so the CLI can publish status and remain responsive to
its local control socket.

The storage witness remains more authoritative than this projection. If string
allocation or later presentation fails, rev0955's fixed-width process witness
still blocks payload authority.

### Faulted interval

While an alarm is active, `run_next_or_throw()` short-circuits before filesystem
wake observation, periodic repair, outbound pull, inbound application service,
or ingress publication event handling. A call may do only one of two things:

- return a bounded backoff-pending step; or
- attempt current-byte reproof after the monotonic deadline.

The network listener and owner-only status/control socket remain alive, but no
ordinary synchronization step is authorized. A numeric listener may accumulate
a bounded kernel backlog while faulted; native I2P publication may remain owned
by its worker. Neither is consumed by the application owner until payload
authority is restored. This is deliberate fail-closed availability, not a claim
that transport is healthy.

`ready()` now requires all three conditions:

```text
initial repair completed
required ingress ready
no active payload-integrity fault
```

The local JSON state is `faulted`, and `ready` is false. If systemd readiness was
already announced before corruption, systemd's one-way `READY=1` startup
protocol does not become a dynamic health oracle. Rev0956 updates `STATUS=` and
the owner-only JSON, but it does not claim to retract the manager's historical
startup completion. A future watchdog or health integration should be explicit
rather than pretending that startup readiness is continuously revocable.

### Current-byte reproof

Recovery ordering is intentionally strict:

1. perform one complete, leased payload-store snapshot;
2. require that snapshot to clear or disprove the store's process-local fault
   using current good bytes or exact absence;
3. run the ordinary folder convergence pass;
4. only after both operations succeed, record exact recovered-alarm history;
5. clear the active service alarm and retry deadline; and
6. account one recovery step and restore readiness eligibility.

If either the complete snapshot or convergence pass throws the typed integrity
error, the outer owner catch records another detection and reschedules. If it
throws any other error, the process retains its existing terminal semantics.
The active service alarm is never cleared merely because a timer fired, a status
request occurred, metadata matched, or an operator overwrote a file.

The explicit snapshot can duplicate a payload-namespace enumeration later in
the convergence pass. It exists because a convergence pass with no local
regular-file candidate is not guaranteed to touch the append-only payload store;
recovering without independently clearing the store witness would be wrong. A
future performance slice may thread the already re-proved immutable payload
snapshot into the folder pass, but only if the pass preserves the same terminal
catalog/replica/root cutpoints. Rev0956 records this as bounded but potentially
large recovery I/O rather than hiding it.

## Operator projection

The status schema advances to `anonsync.peer-service.status.v3` and is rendered
once for both the live owner-only socket and the terminal service report.

### `payload_scrub`

This object reports process-local scheduling observations without touching the
filesystem during rendering:

- enabled state and configured byte/entry limits;
- the last completed attempt disposition;
- monotonic age, hashed bytes, touched/completed entries;
- durable state generation and completed-cycle count;
- active digest and byte offset when continuation remains;
- whether state was rebuilt; and
- whether a prior durable failure was disproved and cleared.

A fresh process may legitimately have no last report or completed-cycle age.
Rev0956 does not invent wall-clock history that the v1 scrub record never
persisted.

### `payload_integrity`

This object has independent active and recovered domains:

```json
{
  "state": "healthy | faulted",
  "active_fault": null | { ... },
  "most_recent_recovery": null | { ... }
}
```

The active object contains exact expected/observed SHA-256 values, durable
publication truth, detection count, active and last-detection ages, and the
remaining retry delay. The recovery object retains the same exact digest pair,
persistence truth, total detections, fault duration, and recovery age.

Recovered history is deliberately bounded to one event and process lifetime. It
is not a durable audit log, not corruption authority, and not proof that every
payload is currently good. A later active fault may coexist with the previous
recovery record until that later fault itself recovers.

## Real-process proof

The existing configured-service process regression now exercises the complete
shipping path rather than a test-only daemon:

1. bootstrap two configured shares and converge a regular file;
2. locate the exact digest-named source payload and overwrite its bytes in place;
3. wait for schema v3 to report `service_state=faulted`, `ready=false`, and exact
   expected/observed digests;
4. prove the source PID remains unchanged and the owner-only mode-0600 control
   socket still answers;
5. restore the exact payload bytes externally;
6. wait for one complete current-byte reproof and convergence pass;
7. require `service_state=running`, `ready=true`, recovery counters, and exact
   most-recent-recovery evidence under the same PID; and
8. request owner-only drain and prove clean socket removal.

The focused payload-store suite continues to prove allocation-independent
mismatch retention, durable-record loss, repeated same-owner failure, mutation
preflight rejection, snapshot revocation, repair, and current-byte recovery.

## Adjacent refactors and corrections

- Payload-scrub disposition spelling is centralized in the payload-store API.
- The folder process exposes only a narrow retained payload-store accessor; the
  peer service does not reopen or bootstrap storage independently.
- Session I/O errors have explicit nonterminal service dispositions, keeping
  transport churn distinct from integrity failure and from arbitrary exceptions.
- One status renderer serves live and terminal JSON, preventing field drift.
- Age calculations use `steady_clock` and saturating accounting.
- Recovered exact evidence is retained after authority restoration instead of
  being erased at the recovery cutpoint.
- The existing I2P negative-control horizon remains long enough to prove a route
  attempt under compiler load without permitting direct TLS fallback.
- Structural checks bind the typed-only catch, fault-mode short circuit, recovery
  ordering, readiness gate, schema-v3 fields, same-PID process regression,
  recovered history, documentation, and release inclusion.

## Research-informed comparison

The useful precedent is operator behavior, not implementation borrowing.

- systemd's notification protocol separates startup completion (`READY=1`) from
  human-readable runtime `STATUS=` updates. Rev0956 therefore treats its local
  JSON as the current health surface and does not claim that historical startup
  readiness is a revocable health bit. See
  <https://www.freedesktop.org/software/systemd/man/sd_notify.html>.
- Syncthing exposes structured current status and a separate recent-errors
  collection. Retaining one recovered exact alarm is the smallest AnonSync step
  toward that distinction without adding a new persistent error database. See
  <https://docs.syncthing.net/rest/system-status-get.html> and
  <https://docs.syncthing.net/rest/system-error-get.html>.
- Btrfs and OpenZFS expose scrub progress and completion/error state because
  integrity work is an operator-visible lifecycle concern. Their redundant-copy
  repair semantics do not apply to AnonSync's current sole-copy payload store.
  See <https://btrfs.readthedocs.io/en/latest/btrfs-scrub.html> and
  <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-scrub.8.html>.

## What this proves

Rev0956 proves that one exact payload mismatch can become a reusable peer-service
state rather than a daemon-ending accident. While faulted, ordinary sync work is
not scheduled, readiness is false, exact evidence remains queryable through the
same owner-only endpoint, and the same process can recover only after complete
current-byte storage proof plus ordinary convergence. It also proves that a
successful repair no longer erases the most useful exact explanation for the
outage.

## What this does not prove

- The retained history is not durable across restart and has no wall-clock time.
- One completed scrub cycle is not a percentage, ETA, or coverage-age SLO.
- A multi-attempt resumed SHA-256 remains exact-extent evidence rather than a
  point-in-time snapshot against hostile concurrent writers.
- systemd startup readiness is not dynamically revoked after `READY=1`.
- The faulted service does not yet expose a desktop notification, GUI, multi-share
  dashboard, on-demand recheck command, or explicit repair workflow.
- Reproof may enumerate the payload namespace twice before recovery; a very
  large store can make repair detection I/O-expensive.
- There is no quarantine, automatic remote restoration, durable reachability pin
  set, version-retention policy, or crash-safe garbage collection. Automatically
  moving or deleting a sole copy would be unsafe.
- Same-UID hostile writers, public Tor/I2P privacy qualification, cross-platform
  filesystem behavior, rename/directory semantics, changed-block reuse, and the
  first measured Resilio uninstall workload remain open product obligations.
