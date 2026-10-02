# ADR 0193: Bound persistent route and Ratox heartbeats

Status: accepted construction surface, 2026-08-27.

## Context

ADR 0192 separated c-toxcore carrier truth, local SOCKS-listener reachability, and an optional
confirmed-peer echo. It deliberately left two different jobs open: turning repeated observations
into a stable operator signal, and testing the exact Ratox attachment rather than only its enclosing
peer session.

Ratox v1 also never evicts exact control replay records. Allocating a fresh PING message ID for every
sample would therefore consume the host's finite replay store merely because a healthy terminal had
been left open. Conversely, allowing a missed sample to mutate c-toxcore state or detach a session
would confuse observation with authority.

## Decision

Add the owner-side monitor:

```text
iotox [--watch-ms N] [--sample-ms N] [--failure-samples N]
      [--recovery-samples N] route-health-watch [FRIEND]
```

Sampling is bounded to 100..600000 ms. Failure and recovery thresholds are independently bounded to
1..64 and default to three and two decisive samples. The canonical nine-line operation-39 report is
strictly parsed before it can enter the monitor. Local-boundary and remote-application observations
feed independent latches with `unknown`, `healthy`, `suspect`, and `unavailable` states. An
inconclusive observation clears the current streak but neither changes the latched state nor invents
a success or failure. Counters saturate rather than wrap.

The watch lives in the invoking operator process. It emits observations and transition evidence but
does not persist policy in the Agent, relabel c-toxcore's carrier, advance an online epoch, detach a
terminal, or initiate recovery.

Add a separate Ratox attachment heartbeat. `RatoxClient` allocates exactly one PING message ID per
attachment and reuses the identical canonical frame for every sample. Concurrent local requests
coalesce while that packet is queued. Every valid PONG must correlate to that exact ID. The host may
therefore replay its one cached exact PONG indefinitely while consuming only one never-evicted
exact-control replay entry. Detach, route loss, exit, failure, and a successfully resumed generation
clear the old heartbeat identity; the new attachment allocates its own.

The local terminal client sends one PING per second while attached. After three consecutive sampling
deadlines without a correlated PONG it prints a warning and keeps the session retained. A later PONG
prints recovery. Only authoritative route loss, remote lifecycle, or an explicit local operation may
change attachment state.

No Ratox frame number, payload, header, replay rule, or negotiated feature changes. This is a semantic
use of the already frozen v1 PING/PONG pair.

## Consequences

- `route-health-watch FRIEND` observes the confirmed IoTox application path independently of any
  terminal; the Ratox heartbeat traverses the exact current terminal attachment.
- An exact repeated PONG proves that the remote Agent's current Ratox route and replay service remain
  reachable. It does not prove that the PTY child is making progress, measure terminal output latency,
  establish SOCKS-target/Tor-circuit health, or justify an anonymity claim.
- Three misses are a warning threshold, not a connection-state oracle or automatic resume policy.
- Exact-ID reuse is required for long-lived v1 sessions. Fresh periodic PING identities would turn
  normal liveness sampling into deterministic replay-store exhaustion.

## Qualification

The owned client test completes 2,048 heartbeat cycles with byte-identical PINGs, one stable message
ID, bounded queues, exact PONG correlation, and no growth of the next control ID. Network tests reject
malformed or semantically incoherent route reports and drive both latches across success, suspect,
failure, and recovery thresholds. The whole-binary lifecycle fixture runs the finite watch and proves
independent healthy application state.

A real Agent/controller test crosses the Unix seqpacket surface, authority ledger, transcript-gated
mock peer, Ratox OPEN, three remote PING/PONG exchanges, authoritative route loss, exact RESUME into
generation two, another PING/PONG, and explicit detach. The installed terminal-client process emits
PING, exposes the three-miss warning when PONG is withheld, does not detach itself, and accepts a
later authoritative terminal result.

This is deterministic one-host construction evidence. Actual impaired native/TCP/Tor routes,
terminal output-latency probes, automatic recovery policy, and long-running production thresholds
remain separate qualification gates.
