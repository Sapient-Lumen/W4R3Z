# ADR 0055 — Durable offline command outboxes are signed scheduled state

- Status: accepted for M5 implementation
- Date: 2026-08-15 America/New_York
- Supersedes: the process-memory retry cadence in ADR 0029 and the v2 storage limit in ADR 0036
- Preserves: ADR 0038 operation policy and ADR 0040 FIFO-as-ingress-only

## Context

IoTox already commits an exact command identity and canonical bytes before transport or execution.
That closes the central duplicate/crash hole, but it is not yet a complete offline lifecycle:

- a local command can only be created after a live confirmed session;
- retry timing is mostly process memory rather than signed restart state;
- one counter mixes request, receipt, and result delivery attempts;
- there is no pre-send cancellation window or scheduling priority;
- global record count is bounded, but unfinished per-peer work is not;
- an absolute frame expiry silently assumes the wall clock is trustworthy;
- a store write failure is safe in practice but has no frozen outbox rule.

These gaps must be closed while the operation set is still read-only. M5 does not authorize a
physical or settings mutation.

## Decision

### One signed store, three artifact lanes

The signed command store advances from `IOTXCMD2` to `IOTXCMD3`. A v2 snapshot is verified with its
original signature and strict decoder, translated to conservative v3 scheduling defaults, and
atomically rewritten before the agent starts. If the rewrite fails, startup fails and the v2 file
remains authoritative.

Each durable record owns independent schedules for:

```text
request   outgoing exact COMMAND
receipt   incoming exact RECEIVED acknowledgement
result    incoming exact terminal COMMAND_RESULT
```

Every schedule freezes attempt count, last attempt, next eligible attempt, and last transport error.
The request identity, canonical bytes, priority, expiry, and clock requirement are immutable.

### Offline admission and explicit identity

The local typed entrance may reserve a registered read-only command for an existing Tox public key
while that friend is offline or its IoTox/authority session is not ready. The command receives its
persistent sender epoch and random nonzero message ID and is committed before the CLI or FIFO
reports admission. It uses the current IoTox protocol version; an incompatible future session blocks
delivery rather than rewriting the record.

FIFOs remain byte-framing ingress. They own no queue, identity, retry, or cancellation state.

### Cancellation-before-start

A new outgoing record has a one-second persisted admission delay. It may be cancelled only while:

```text
lifecycle = reserved
request attempts = 0
```

Once an attempt has been committed, a crash could have occurred after transport acceptance but
before the post-send store update. Cancellation is therefore refused even when the visible lifecycle
still says `reserved`. IoTox v1 has no remote-cancellation claim. `cancelled` is a local terminal
state with no fabricated remote result.

### Expiry and clock quality

Expiry remains the outer frame's absolute `expiry_unix_ms`; priority is local and is not smuggled
into wire flags. A TTL can be converted to an absolute expiry only when the daemon was explicitly
started with trusted-wall-clock policy and the current time has not moved behind the signed store's
high-water mark beyond the configured tolerance. A trusted startup checkpoints current time into
the signed journal. During that process lifetime, monotonic elapsed time also detects a backward
wall-clock step; loss of trust is sticky until restart after clock repair.

When wall-clock quality is uncertain:

- a new TTL-bearing local request is refused;
- a received expiring request is durably acknowledged but not authorized or started;
- an existing expiring outgoing request is held rather than declared expired;
- non-expiring read-only work may continue.

With a trusted clock, expiry before the first attempt is locally terminal and unambiguous. After any
attempt, the sender stops retrying at expiry but records `timed-out-unconfirmed`; it never invents a
remote result. A retained uncertain timeout may resolve once if the peer's exact authenticated
result arrives late. Cancellation and never-attempted expiry remain irrevocably local. Current
operations are read-only, so this uncertainty cannot hide a physical effect.

### Retry and synchronization

Delivery uses exact frozen bytes. Before each transport call, IoTox commits the incremented attempt,
attempt time, and next eligible time. A crash at any later instruction therefore leaves a safe exact
retry. Local toxcore `unavailable` and `resource_exhausted` remain retryable; other errors are
observable and block automatic retry.

The default delay is exponential from one second to five minutes with stable 0–25% jitter derived
from the durable key and artifact lane. A live process advances schedule time from a steady-clock
anchor. An untrusted restart resumes at signed high-water time and conservatively waits any
unproven delay; trusted wall time may account for elapsed offline time. Restart cannot reset or
accelerate untrusted retry state. An outgoing request continues exact synchronization until
receipt/result or expiry, including after one copy entered the local Tox queue. Incoming
receipt/result retries stop after local queue acceptance; a sender's exact request replay is the
application-level recovery trigger and causes an exact artifact replay without moving a signed
deadline backward.

Eligible requests are ordered by high, normal, then low priority, followed by next-attempt time,
creation time, peer key, sender epoch, and message ID. Priority never bypasses authorization,
expiry, clock, or quota checks.

### Quota and retention

In addition to the 1,024-record and 8 MiB absolute ceilings, the defaults are:

```text
unfinished records total              256
unfinished records per peer/direction  32
canonical bytes per peer/direction    256 KiB
```

Exact duplicates do not consume quota. Incoming terminal execution remains unfinished until its
receipt and result have both entered the local Tox queue, so it cannot be pruned merely because the
operation ended. Only the oldest fully delivered terminal history may be pruned. Persisted work is
rechecked against configured quotas at open. Unfinished work is never evicted to admit newer or
higher-priority work. Quota exhaustion is an explicit local or protocol resource failure.

### Full disk and shutdown

No transport attempt starts unless its pre-attempt schedule commit succeeds. A failed insert/update
leaves the prior in-memory and on-disk snapshot authoritative. If transport accepted a packet and
the post-send update fails, the pre-attempt record still contains the exact identity, bytes, attempt,
and delayed retry; restart can only replay the same logical command.

Shutdown first closes command admission, then stops FIFO/control ingress, then stops the event
scheduler and transport. No new outbox attempt begins after shutdown starts. Store transactions are
synchronous; already committed unfinished work remains scheduled for restart.

## Consequences

- Offline submission becomes honest durable admission rather than an availability error.
- Timeout, cancellation, transport acceptance, remote receipt, and remote result remain distinct.
- A valid older v2 journal is upgraded without discarding identity or evidence.
- The signed full-snapshot strategy gains fields and write amplification; an append/log store remains
  a future format decision.
- Mutating operations still require operation-specific idempotency, effect reservation, remote
  cancellation/compensation, and target power-cut evidence before registration.

## Rejected alternatives

- **Put the queue in the FIFO:** bytes disappear and have no durable identity.
- **Reset retry after restart:** permits restart-driven traffic amplification.
- **Cancel any locally unacknowledged send:** a crash window makes remote start possible.
- **Treat system time as automatically trustworthy:** headless devices commonly boot with stale time.
- **Delete low-priority unfinished work at quota:** silently loses admitted intent.
- **Change frame flags for local priority:** creates an undeclared wire protocol.
