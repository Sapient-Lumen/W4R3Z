# ADR 0197: Freeze Ratox total-loss recovery

Status: accepted and network-qualified for the stated Sandwurm cells, 2026-08-27.

## Context

ADR 0196 kept carrier presence, Ratox heartbeat, PTY progress, and visible stall separate under
bounded delay and packet loss. It deliberately left mutation policy open until a real route outage
could join the controller outcome to remote PTY retention and exact resume. A heartbeat timeout is
available much sooner than c-toxcore declares a peer offline, but it does not prove that the
authenticated route is gone. Conversely, waiting only for carrier truth gives a correct but visibly
slow outage signal.

The remaining gate had to establish what survives complete bilateral packet loss, which signal may
change terminal state, and what identity/sequence conditions make recovery safe. A new shell after
reconnection would not answer those questions.

## Decision

Freeze the Ratox total-loss policy as follows:

1. A missed Ratox heartbeat is warning-only. It may update presentation and operator diagnostics,
   but cannot detach, close, resume, migrate, reopen, or relabel an authenticated terminal.
2. Authoritative c-toxcore peer-offline truth detaches the route. The local controller receives the
   typed `unavailable` terminal outcome. The remote Ratox host keeps the exact live PTY and session
   detached, subject to its existing owner-configured retention and resource policy.
3. Reconnection alone does not resume. The controller must observe the same peer confirmed and
   authority-capable on a strictly higher positive online epoch before an explicit `resume_only`
   request for the prior session is eligible.
4. Resume must preserve the session ID, process incarnation, and exact acknowledged input/output
   positions. The attachment generation advances by exactly one. Any mismatch fails closed rather
   than silently opening a replacement shell.
5. The present one-route product performs no automatic cross-route migration. Future route
   selection may automate discovery or presentation, but cannot weaken the authenticated-epoch,
   principal, session, incarnation, generation, or byte-position fences frozen here.

The qualification scenario opens one authority-bound PTY, proves heartbeat and byte `A`, installs
seeded `netem loss 100%` on both guest TAP egress paths, and releases a two-second heartbeat probe.
It requires the heartbeat deadline to expire while carrier/session truth remains confirmed at the
same epoch. It then waits for the authoritative offline event, records the local typed outcome, and
captures the remote host with exactly one live/running, zero-attached session plus its
`peer-detached` journal entry. Only then does it remove both qdiscs. Recovery requires a higher
authenticated epoch, exact generation-two resume at byte position two, a new PONG, and byte `B`.

## Consequences

- IoTox can warn an operator in about two seconds without pretending the route is authoritatively
  gone. In these cells c-toxcore offline truth arrived about 30–31 seconds after loss.
- The user-visible controller attachment ends on authoritative loss, while the useful remote
  process survives. The existing explicit `terminal-resume` operation is therefore the safe
  recovery surface; automatic hidden reopen is not.
- Retention is not immortality. Existing PTY lifetime, cgroup, resource-pressure, revocation,
  process-exit, and owner shutdown rules remain authoritative and may make a later resume fail.
- Route restoration to authenticated readiness measured 0.769 seconds on direct UDP, 2.155 seconds
  on forced TCP, and 4.996 seconds through strict generic SOCKS. Resume OPENED then took 21.123,
  48.940, and 28.034 milliseconds respectively. These are observations, not service-level
  objectives.
- The near-identical roughly 30-second offline times across the three cells locate the mutation
  delay in provider connection-state policy rather than in the Ratox heartbeat or local scheduler.
- The strict-SOCKS cell remains laboratory proxy containment. Actual Tor total-loss/terminal
  recovery, alternate-route handoff, Mosh-style speculative state, and multi-route migration remain
  separate gates.

## Qualification

Compact proofs `pair.0cnril1l` (direct UDP), `pair.qoty7j1x` (forced TCP), and `pair.8jjawnwp`
(strict generic SOCKS) independently verify. All six guest roles used product revision `rev0045`
and binary SHA-256
`511b29744b5e0477e8da3277e109c998b030fb1d5890aebde3bddab28d41936f`.

The direct cell binds source revision `15b57aacd3a86df44896dff1b9a0557dbfc561dc`; the TCP and SOCKS
cells bind `4ba7a861db38bf3193cc106190ef63f571751e73`. The only source delta is the one-line registration
of the already-implemented scenario in the independent verifier's top-level allowlist; the guest
closure, experiment, lifecycle schema, and product binary are unchanged. The three-cell analyzer
accepts this exact evidence while reporting both source revisions rather than hiding the distinction.

Exact timings, hashes, reproduction commands, and nonclaims are recorded in
`docs/evidence/2026-08-27-sandwurm-ratox-route-loss.md`.
