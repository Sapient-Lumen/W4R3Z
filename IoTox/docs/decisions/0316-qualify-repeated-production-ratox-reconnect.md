# ADR 0316: Qualify repeated production Ratox reconnect

- Status: accepted and implemented
- Date: 2026-09-03

## Context

ADR 0289 implemented exact-session reconnect in the owner-facing terminal command, and ADR 0300
proved that one unchanged production client could cross one genuine total route loss on direct UDP
and forced TCP. That left an important lifecycle question open: could the same invocation and the
same remote PTY survive another complete carrier death after the first successful resume, or had the
first join left hidden one-shot state behind?

A second outage must not be approximated by restarting the client, opening another shell, replaying
the first receipt, or merely repeating the one-loss scenario in a fresh VM. It must occur after
post-resume terminal progress and a healthy heartbeat interval, and it must advance the exact same
session from attachment generation two to three.

## Decision

Add the additive Sandwurm scenario `ratox-cli-reconnect-repeated`. It retains the original
`ratox-cli-reconnect` scenario and v1 lifecycle receipt unchanged. The repeated cell executes the
same real command:

```text
iotox terminal PEER --reconnect
```

under one pseudo-terminal, then drives two ordered interruptions. For each interruption the pair
runner:

1. applies independently seeded 100% netem loss to both task-owned guest TAPs;
2. requires a Ratox heartbeat warning while the authenticated route is still confirmed at the
   prior epoch and on the expected carrier;
3. requires authoritative offline and the same live, running, zero-attached device PTY;
4. records positive packet drops on both TAPs before removing the fault;
5. permits only exact-session resume at a strictly higher authenticated epoch and attachment
   generation; and
6. requires another terminal input/output byte and healthy heartbeat interval before a later fault
   can begin.

The v2 lifecycle receipt binds one PID and process start tick, zero restarts, one session and host
incarnation, ordered epochs, generations 1-to-2-to-3, exact input/output positions 1-to-2-to-3,
retry counts, timing, detach, and exit status zero. The v5 route-loss receipt binds two ordered
faults and their distinct TAP seeds and counters. The verifier rejects a seed/ordinal mismatch,
replacement shell, carrier fallback, stale epoch, discontinuous byte position, or missing host-side
detachment.

The local controller-process fixture also forces two unavailable/resume cycles through one real
CLI process. Direct UDP and forced TCP raw roots and their allowlisted compact exports are recorded
in `docs/evidence/2026-09-03-sandwurm-ratox-cli-reconnect-repeated.md`.

## Consequences

Bounded repeated native-carrier continuity is now qualified above frozen Ratox v1. One production
client and one remote shell survive two sequential authoritative carrier deaths on both direct UDP
and relay-only TCP. The original one-loss proof remains independently verifiable rather than being
reinterpreted by the new receipt grammar.

This is not an hours-long soak, public-network or Tor/I2P qualification, transparent route roaming,
daemon- or host-restart survival, Mosh screen-state synchronization, a live-clone lease, independent
security review, or production activation. The device Agent still owns the PTY, and loss of that
Agent intentionally ends the session. No Ratox peer frame or local terminal packet changed.
