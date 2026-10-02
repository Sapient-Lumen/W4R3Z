# ADR 0138: retry one fully cleared range attempt

Status: accepted; failed-prefix discard superseded in part by ADR 0230 on 2026-08-29

Date: 2026-08-22

## Decision

A synchronization range transfer may make one automatic same-job retry after its admitted Tox
transfer ends incomplete or complete range bytes fail reconstruction. Retry is permitted only after
the subscriber, under the namespace transaction:

1. discards the exact attempt-derived staging path;
2. finishes the exact stable-device-signed active-attempt record; and
3. fences the exact scheduler attempt and releases its reservation.

Failure or uncertainty in any cleanup step is terminal. The retry uses the identical locally derived
canonical range plan, candidate signed HEAD, authenticated online epoch, peer authority, namespace,
and target object. It allocates a fresh durable scheduler attempt, request message ID, and nonzero Tox
FileId before sending a new range request. The old transport handle and received prefix are never
resurrected or copied into the new attempt.

The product default is one retry; the internal configuration accepts zero through eight so tests and
future policy can disable or further bound it without creating an unbounded loop. The public Agent
path keeps the one-retry default. `sync-status` reports `range-retries` and the saturating total
`range-discarded-bytes`. Successful fetched-byte accounting describes the final complete bundle only;
discarded bytes are separate and never count as reuse.

A local generic `file-control ... cancel` is a transfer fault, so the Agent must deliver that local
terminal outcome to the subscriber just as it delivers a toxcore-originated CANCEL. By contrast,
`sync-cancel JOB_ID` first makes the entire job terminal and therefore cannot trigger this retry.
Authenticated disconnect also retires the old-epoch job under ADR 0132.

## Consequences

- A transient partial range failure no longer forces the operator to restart an otherwise valid
  same-epoch pull.
- Every retry is stale-safe: a late callback for the first file number or FileId has no live attempt
  to target.
- In the original implementation partial bytes saved no bandwidth. ADR 0230 now permits one exact
  private prefix to cross the already-required fresh-attempt fence when the seek-capable receive seam
  is present. It remains bounded fault continuation, not transport-handle continuation.
- A repeated transfer/reconstruction failure is terminal after the one retry. Cleanup uncertainty,
  authority change, epoch loss, invalid manifest, and failure to allocate or send the retry also fail
  closed.
- HEAD acceptance and activation authority are unchanged. Only a complete reconstructed target with
  its exact SHA-256 may commit; the signed HEAD is accepted last and activation remains explicit.

## Evidence

The owned subscriber test fails the first range attempt after half of its bundle, requires the old
staging path to disappear and generation 1 to remain accepted, compares the retry's exact HEAD and
range vector, rejects FileId reuse, completes the second attempt, and observes empty durable attempt
truth plus generation-2 acceptance. The existing corrupt-basis fallback continues afterward.

The genuine `sync-file-range-retry` Sandwurm cell injects a public CLI cancellation only after a
positive provider position on a rate-shaped 1 MiB range. Both direct UDP and forced TCP prove a fresh
FileId, one retry, positive discarded bytes, 3 MiB reuse, exact 1 MiB final fetch, generation-2 HEAD
acceptance, and explicit activation. Both compact exports independently reverify; exact bindings and
failed scientific runs are retained in
`../evidence/2026-08-22-sandwurm-sync-range-retry.md`.
