# ADR 0131: cancel synchronization pulls before cleanup

Status: accepted

Date: 2026-08-21

## Decision

Every live subscriber pull receives one nonzero process-local `job_id`. The identifier is the
original signed-HEAD request message ID and is collision-checked against the Agent's bounded retained
job set. `sync-pull` returns it, `sync-status` projects it without content, and:

```text
iotox sync-cancel JOB_ID
```

sends the exact unsigned 64-bit identifier through the owner-private same-user local control socket.
This adds operation 73 and advances that private protocol to v1.28. The command does not require a
live peer or remote authority: it withdraws a local subscriber decision. Job IDs are deliberately not
durable global identifiers and are never accepted from a remote peer.

Cancellation first changes the retained job state to terminal `cancelled` while holding the
subscriber lock. Only then may it call transport or filesystem seams. HEAD results, object results,
file offers, and terminal file callbacks select only their corresponding active state, so no late
event can revive the job, publish an object through it, or advance accepted HEAD after the boundary.

For every admitted binding, coordinator close requests c-toxcore cancellation at most once, clears
the admitted marker regardless of that control result, removes the attempt-derived staging file,
finishes the stable-device-signed active-attempt record, and fences the scheduler attempt. Scheduler
close also fences reservations that never received a file offer. Local cleanup continues when a
remote CANCEL cannot be enqueued: transport notification failure is not authority for keeping local
resources live.

The first command returns such a transport or cleanup failure and retains the cancelled tombstone.
An exact retry resumes or acknowledges cleanup without repeating a transport-cancel effect already
attempted. A new pull for the same peer, epoch, and namespace may replace the cancelled tombstone only
after cancellation is settled. Completed or failed jobs cannot be relabelled as cancelled, and an
unknown or zero ID fails explicitly.

Daemon restart does not reconstruct these process-local tombstones. The signed active-attempt
journal is the durable truth: startup recovery fences lost Tox handles and either completes or
discards exact attempt-scoped staging before networking begins.

## Consequences

- Operators can stop one exact pull without identifying it by mutable friend number plus namespace.
- Cancellation means IoTox has withdrawn local admission and fenced future commit. It does not prove
  that a remote sender observed CANCEL or stopped emitting packets.
- A late completion can still reach the Agent event queues, but it has no active subscriber binding
  and cannot accept a HEAD.
- Already committed immutable objects remain valid reusable content. Cancellation never rolls back a
  completed job, rewrites an accepted HEAD, changes activation, or deletes shared content-store
  objects.
- The bounded job tombstone makes status and exact retry intelligible without creating another
  durable state format or rollback root.
- Genuine-provider cancellation after positive transfer progress is a separately verified Sandwurm
  gate; it does not widen the local semantic claim into remote acknowledgement.

## Evidence

The subscriber check now proves pre-HEAD cancellation, idempotent retry, ignored late HEAD, two
admitted request-selected FileId receives, terminal state before cleanup, injected transport-cancel
failure, exact retry without a repeated transport effect, staging removal, empty signed active truth,
ignored late completion, and unchanged accepted HEAD. A new transfer-coordinator check independently
proves close cancels once, removes staging, clears durable attempt truth, fences capacity, and refuses
a late completed event. CLI, local-protocol, and live-Agent checks cover malformed IDs, operation 73,
v1.28, and absent-job refusal.

One new direct check grows the owned registry from 507 to 508. The complete 26-target GCC/CTest suite
and the complete 41-target Clang 21 ASan/UBSan suite pass; five delegated-cgroup checks skip in the
non-delegated construction shell by design. Rate-shaped 8 MiB direct-UDP and forced-TCP Sandwurm
cells both cancel two admitted receives after positive c-toxcore position and retain no accepted or
activated HEAD. Exact receipts are recorded separately rather than implied by this decision.
