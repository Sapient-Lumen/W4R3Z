# ADR 0220: Add fail-closed synchronization route loss policy

Status: accepted deterministic prerequisite, 2026-08-28.

## Context

ADR 0219 showed that initial placement on an authenticated privacy route does not constrain later
whole-object reassignment. Existing behavior is intentionally availability-oriented: after fencing a
lost auxiliary incarnation, the coordinator selects another ready member for the same principal.
That behavior is correct for ordinary jobs and unsafe as an implicit policy for privacy-required jobs.

A signed per-job route-class grammar does not yet exist. It must not be documented as protection
until the Agent has a mechanism that can actually refuse replacement.

## Decision

- Add a separate `SyncRouteFailoverPolicy` with canonical values `available` and `fail-closed`.
  Initial `fixed|adaptive` placement remains a distinct decision.
- Keep `available` as the compatibility default. It preserves every qualified whole-object loss and
  reassignment gate.
- Add explicit `--sync-route-failover available|fail-closed`, accepted only when synchronization and
  route workers are both enabled. Invalid values and context-free use fail before Agent startup.
- Under `fail-closed`, carrier loss still fences the exact attempt, transfer, FileId, and stale
  terminal truth. It does not select or send through any replacement. The job remains
  `awaiting-objects` on its lost carrier until explicit cancellation and a later new pull.
- Expose `auxiliary-failover-policy` and saturating `auxiliary-fail-closed-jobs` in `sync-status`.
  Do not call a blocked job failed or recovered.
- Make the actual-I2P payload cell select fail-closed policy and require zero blocked jobs on its
  successful 128 KiB path. Future loss cells must positively observe the blocked counter.

The deterministic full-Agent gate injects loss after the first incoming byte. `available` retains
the existing completion through a second authenticated route. `fail-closed` records one carrier
loss, one blocked job, zero reassignments, one initial adaptive selection, the original carrier key,
and an `awaiting-objects` job. Parser/renderer and hostile CLI cases are independently frozen.

## Consequences

- IoTox can now enforce a local no-downgrade invariant immediately, even before a signed per-job
  privacy grammar exists.
- This is not yet signed remote intent. It is owner-local Agent configuration applied to every
  multi-route sync job in that process. The next protocol step must bind allowed route classes or
  fail-closed intent to the authorized job without weakening this mechanism.
- Exact-incarnation fail-closed work does not automatically resume when the same route key returns
  under a new worker incarnation. Explicit cancellation/new pull prevents implicit authority and
  transfer-identity rebinding.
- No framing changes are made. Auxiliary chunk/range design and a genuine two-guest actual-I2P loss
  gate remain open.
