# ADR 0196: Qualify Ratox under bounded route impairment

Status: accepted and network-qualified for the stated Sandwurm cells, 2026-08-27.

## Context

ADRs 0192 and 0193 deliberately separated c-toxcore carrier truth, local route-boundary health,
confirmed-peer application health, and the Ratox attachment heartbeat. Those seams were constructed
before there was genuine two-guest evidence joining a heartbeat to PTY output under the same route
impairment. Without that evidence, choosing a terminal migration or recovery trigger would conflate
signals with different meanings and failure times.

The terminal must eventually feel resilient under delay, loss, and route failure. It must also avoid
destroying a still-usable authenticated attachment merely because one observation is slow. A route
listener may be reachable while upstream traffic is stalled; a Ratox PONG proves the Ratox peer and
replay path responded but not that the PTY child made progress; PTY output proves progress for those
exact input bytes but not general route health.

## Decision

Freeze four distinct observation layers:

1. **carrier/route presence** is c-toxcore connection truth plus the separately labeled local and
   configured-target observations from ADRs 0192 and 0194;
2. **Ratox heartbeat** is one exact PING/PONG over the current authenticated attachment;
3. **PTY progress** is cumulative acknowledged input followed by output from that same attachment;
4. **user-visible stall** is the elapsed time until that PTY output reaches the local controller.

Bounded partial impairment is a warning and measurement condition. It does not automatically close,
detach, resume, migrate, or reopen an established authenticated session. IoTox stays on the current
route while it continues to make authenticated progress and exposes the independent observations to
the operator. No deadline, failover threshold, or service-level objective is inferred from this one
host/profile/sample.

The qualification scenario is fixed at 120 sequential observations per route: 20 baseline, 80 with
both guest TAP egress paths carrying seeded `netem delay 75ms 15ms loss 2%`, and 20 after exact qdisc
removal. Each observation sends one Ratox heartbeat and then one PTY byte/echo through the real local
terminal controller, Agent, authority/session gates, source-linked provider, remote Agent, and PTY.
The producer records separate heartbeat and terminal captures; the independent pair verifier and a
scenario-specific analyzer recheck their ordinals, clocks, byte sequences, stable session identity,
source/binary identity, qdisc activity/drops, and strict SOCKS containment where applicable.

This sequential heartbeat-before-echo schedule is observational only. It changes no frozen Ratox
wire framing or replay rule. A later experiment may sample concurrent signals, but it must keep their
meanings and evidence separate.

## Consequences

- A slow or missed heartbeat may warn, but it is not authority to mutate a live terminal.
- PTY progress is the closest implemented observation of what the operator experiences. Even it
  does not authorize migration until total-loss retention and resume behavior are qualified.
- Direct UDP had the lowest impaired median but one 2.158-second terminal tail after packet loss.
  Forced TCP and strict generic SOCKS had higher medians and smaller maxima in these samples. That is
  a carrier-shape finding, not a universal route ranking or a reason to prefer TCP.
- Recovery-phase terminal medians returned to their baseline class on every route without a session
  reopen or migration. Internal queue and local-render evidence remained small relative to network
  latency, locating the observed bottleneck outside the Agent's ordinary interactive scheduler.
- The strict `tox-tor` cell proves numeric SOCKS containment through the laboratory forwarder. It is
  not actual Tor, anonymity, circuit, public-relay, or two-peer-over-public-Tor evidence.
- The next recovery-policy gate is exact total route loss: independently observe route absence,
  heartbeat loss, local controller outcome, detached PTY retention, restored authenticated epoch,
  exact session resume, and post-resume PTY progress. Only that gate may justify a mutation policy.

## Qualification

Clean source revision `f5d526c8c7461277b7ad57277fc5ee2177c59386` produced one identical
source-linked binary, SHA-256
`511b29744b5e0477e8da3277e109c998b030fb1d5890aebde3bddab28d41936f`, in all six guest roles.
Compact proofs `pair.tscy1yrt` (direct UDP), `pair.gf5mxexc` (forced TCP), and `pair.p3dt6g9c`
(strict generic SOCKS) independently verify. Every cell completed all 120 heartbeat and PTY
observations with one unchanged Ratox session identity and positive packet drops on both TAPs.

The exact measurements, capture commitments, reproduction commands, and nonclaims are recorded in
`docs/evidence/2026-08-27-sandwurm-ratox-route-impairment.md`.
