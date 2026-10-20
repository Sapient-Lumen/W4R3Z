# ADR 0134: pause synchronization receives without retiring the job

Status: accepted

Date: 2026-08-21

## Decision

A subscriber may pause and resume one admitted synchronization object through the existing finite-file
control surface:

```text
iotox file-control PEER_PUBLIC_KEY_HEX FILE_NUMBER pause
iotox file-control PEER_PUBLIC_KEY_HEX FILE_NUMBER resume
```

Pause is process-local flow control on one live c-toxcore receive. It does not retire the subscriber
job, release its staging or scheduler reservation, clear its signed active-attempt record, change its
request-selected FileId, advance the authenticated online epoch, or authorize acceptance or
activation. Resume must address the same peer and file number and must retain the same 32-byte
FileId. It clears only the local pause fact; a peer-owned pause remains effective under ADR 0047.

The first synchronization-specific operator contract deliberately reuses `file-control`. There is no
parallel `sync-pause` operation or durable pause request. `sync-status` continues to describe the
job-level state, while the private peer transfer projection is the authoritative live view of file
number, FileId, position, and independent local/peer pause facts. A process or guest restart loses
the transport handle and follows the separate attempt-recovery contract; it never reconstructs a
paused c-toxcore transfer from durable state.

Completion is still ordered normally after resume: every object must arrive completely, pass size
and SHA-256 verification, and commit under its reserved attempt before the signed HEAD can be
accepted last. Activation remains an exact, separate local decision. Pausing partial bytes cannot
make staging, a manifest, or a HEAD authoritative.

## Consequences

- Operators and future schedulers can temporarily stop an individual synchronization receive
  without manufacturing a failed job or a fresh application request.
- Pause retains the full staging-byte and worker reservation. It is therefore bounded by the
  namespace quotas but is not a way to free capacity; cancellation is the explicit release path.
- A stable transport position while paused is evidence about one live provider transfer, not a
  promise that kernels, relays, or peer-side queues contain no outstanding bytes.
- Local resume cannot erase a remote pause, rebind a FileId, cross an online epoch, revive a
  cancelled or disconnected job, or recover a transfer handle after process replacement.
- Automatic pause policy, pause expiry, fairness across multiple sources, and durable pause intent
  remain future scheduler work.

## Evidence

The `sync-file-pause` Sandwurm cell uses two simultaneous source-linked IoTox NixOS guests and one
rate-shaped 8 MiB `range-v1` pull. After positive provider position, the subscriber selects one
active receive, records its exact FileId, invokes the public `file-control` pause, and requires the
same file number and FileId to remain locally paused at one unchanged positive partial position for
20 consecutive 100 ms samples. Accepted-HEAD and activation state must still be absent. It then
resumes that exact transfer, observes active state with local pause cleared and the FileId unchanged,
and requires ordinary accepted-HEAD-last convergence plus exact-token activation.

The direct-UDP and forced-TCP cells, their compact digests, and exact nonclaims are retained in
`evidence/2026-08-21-sandwurm-sync-pause.md`. The strict verifier has positive and forged-evidence
fixtures; it rejects a missing resume, a malformed or mismatched FileId, a zero or complete position,
an insufficient stability window, disagreement between roles, and pause claims in every other
synchronization scenario.
