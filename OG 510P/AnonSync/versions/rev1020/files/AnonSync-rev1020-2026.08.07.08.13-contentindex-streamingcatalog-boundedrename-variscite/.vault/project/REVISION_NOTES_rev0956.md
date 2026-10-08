# AnonSync rev0956

Rev0956 turns a typed payload-integrity mismatch from a daemon-ending exception
into an owner-visible, fail-closed, same-process recovery state. It also retains
exact evidence after recovery and exposes bounded scrub progress without allowing
status rendering to become payload authority.

## Primary implementation

- Added peer-service step dispositions for payload fault observation, bounded
  reproof backoff, and completed reproof.
- `SyncReplicaPeerServiceOwner::run_next_or_throw()` catches only
  `SyncReplicaFilePayloadStoreIntegrityError`; arbitrary exceptions remain
  terminal.
- While faulted, the owner schedules no folder wake, ordinary repair, outbound
  pull, inbound application session, or ingress event step. Calls can only defer
  to the monotonic retry deadline or attempt current-byte reproof.
- Recovery requires a complete leased payload snapshot followed by the ordinary
  folder convergence pass. The active service alarm is cleared only after both
  succeed.
- Readiness now also requires absence of an active payload-integrity fault.
- The authenticated listener and owner-only status/stop socket remain alive so
  the service stays inspectable and drainable under the same PID.
- Added saturating service counters for observed faults, reproof attempts,
  recoveries, and backoff deferrals.
- Added explicit nonterminal inbound/outbound TLS session-I/O dispositions so
  broken sessions do not masquerade as integrity or arbitrary process failure.

## Operator status

- Advanced the live/terminal schema to `anonsync.peer-service.status.v3`.
- Added `payload_scrub` with configured byte/entry limits, the last process-local
  report, monotonic age, bounded work, cycle count, continuation digest/offset,
  state generation, rebuild evidence, and stale-failure-clear evidence.
- Added `payload_integrity.state` and `active_fault` with exact expected and
  observed SHA-256 values, durable-publication truth, detection count, active
  age, last-detection age, and remaining retry delay.
- Added bounded `most_recent_recovery` history retaining the exact digest pair,
  persistence truth, detection count, fault duration, and recovery age after
  authority is restored.
- Reused one canonical renderer for the live status socket and terminal service
  evidence.
- Status acquisition stays on the exact owner thread and the payload scrub
  projection performs no filesystem I/O.

## Audit/refactor

- Moved integrity recovery into the reusable peer-service owner instead of
  leaving it as a CLI-only exception loop.
- Kept the storage owner's fixed-width allocation-independent witness as the
  lower authority boundary; service strings are operator presentation only.
- Corrected the first recovery implementation, which erased exact fault evidence
  immediately after success and retained only aggregate counters.
- Centralized process-local monotonic age and bounded retry reporting.
- Recorded the deliberate recovery cost: the explicit payload reproof can be
  followed by another payload-namespace observation in convergence. Removing
  that duplication safely requires threading the immutable cutpoint into the
  folder pass without weakening its terminal database/root checks.
- Corrected a shared process-test validator that treated the nullable
  `payload_scrub.last_report` field as mandatory. A ready empty share may have
  no process-observed scrub attempt; the corruption fixture still requires a
  concrete report after real payload activity.
- Expanded the structural audit and release verifier across the complete
  storage-to-operator path.

## Tests

- Expanded the configured-service product regression to corrupt one exact
  digest-named payload after convergence, prove `faulted`/not-ready status with
  exact evidence, preserve the same PID and mode-0600 status socket, repair the
  bytes in place, prove complete current-byte reproof and readiness recovery,
  retain exact recovered history, drain cleanly, and remove the socket.
- Expanded payload-store and TLS focused suites for the new projection and
  nonterminal session-I/O behavior.
- Existing allocation-fault, durable-record-loss, snapshot-revocation,
  same-owner, mutation-preflight, repair, and scrub-liveness regressions remain
  in force.

## Deliberate nonclaims

- Recovered history is process-local, not a durable audit log.
- systemd `READY=1` startup completion is not dynamically withdrawn; current
  health is carried by `STATUS=` and the owner-only JSON.
- Reproof can be I/O-expensive and may enumerate the payload namespace twice.
- No quarantine, automatic restore, version retention, reachability pinning, or
  garbage collection policy exists yet.
- Scrub cycle count is not a percentage, ETA, or coverage-age guarantee.
- Status remains local JSON rather than a GUI or multi-share device dashboard.
- The first measured Resilio uninstall workload, cross-platform behavior,
  rename/directories, ordinary conflict/restore UX, changed-block reuse, and
  live public Tor/I2P qualification remain open.
