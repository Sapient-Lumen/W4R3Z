# ADR 0065: Gate live Ratox dispatch before network startup

Status: accepted
Date: 2026-08-17

## Context

R1 froze Ratox v1 framing and the pure replay/fencing state machine. R2 added an explicit
`interactive.terminal` capability through authority-ledger v2. R3 added a strict local profile store
and a fork-safe Linux PTY adapter. None of those phases joined an authenticated network epoch to a
live process.

R4 must connect those boundaries without turning a command-line flag, an ordinary Tox friendship,
a stale authority proof, a one-sided feature advertisement, or c-toxcore queue pressure into shell
access or byte loss. The service must also remain absent from default HELLOs until its entire local
construction succeeds. Transport retry, terminal I/O, replay memory, process lifecycle, and audit
records all need finite ownership and explicit failure behavior.

The relevant upstream boundaries are:

- c-toxcore custom-lossless packets are accepted or rejected by one owner-thread API call; local
  send-queue rejection means the caller still owns the exact packet;
- the IoTox session transcript already freezes bilateral feature negotiation per online epoch;
- authority proofs are directional and bound to the current signed ledger head;
- Linux path and process hardening primitives reduce specific attack surfaces but do not constitute
  a complete sandbox.

Primary references reviewed for this decision:

```text
https://github.com/TokTok/c-toxcore
https://toktok.ltd/spec.html
https://man7.org/linux/man-pages/man2/openat2.2.html
https://docs.kernel.org/userspace-api/no_new_privs.html
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://docs.kernel.org/userspace-api/landlock.html
```

## Decision

Introduce a default-off Agent-owned Ratox construction gate and a transport-independent
`RatoxService` coordinator.

### Construction before advertisement

The Agent enables Ratox only when all of the following succeed before toxcore starts:

1. an explicit outer enable flag is present;
2. an explicit profile-store root securely loads for the expected daemon UID;
3. the store contains at least one enabled profile and one enabled principal binding;
4. either an injected `PtyProcessFactory` or an absolute reviewed helper path is available;
5. helper startup and every service bound pass validation; and
6. the coordinator is constructed successfully.

Only then may the Agent add feature bit 23 to the otherwise immutable local HELLO mask. Default
construction and every failed activation retain the ordinary implemented-feature mask with bit 23
clear. The mask becomes immutable once any peer is admitted.

### Exact live packet gate

The Agent routes only custom-lossless packet ID `0xA2` to Ratox. For each packet it reconstructs a
fresh context and requires:

- an application-ready, mutually confirmed IoTox transcript;
- bilateral negotiation of `ratox-interactive-v1` for the current online epoch;
- authority-session state from that same epoch;
- a nonzero authenticated stable principal; and
- an exact-current-ledger-head decision for `interactive.terminal`.

Friend numbers remain transient route handles. Session, attachment, principal, incarnation,
generation, and online-epoch values must all match before input, resize, detach, close, or output ACK
can affect a PTY. The service scopes each live-session replay key to a local domain, authenticated
friend number, and online epoch before the canonical packet bytes. A delayed or parallel route
therefore cannot replay a successful control, conflict with the owning route's message IDs, or retain
an invalid-route reservation.

Exact-route proof loss and durable principal revocation are distinct transitions. Loss of a current
proof fences and closes only sessions whose last successfully attached authority route is that exact
friend/epoch. A signed-ledger revocation invokes principal reconciliation and closes every live or
detached session for that stable principal. Merely presenting a rejected route cannot retarget those
authority-owner fields. For absent ATTACH/RESUME, an unauthorized peer receives a retained denial
before the service reveals whether the session identifier exists.

The Agent serializes each signed authority-head mutation with Ratox packet admission, bounded PTY
progress, and retained transport dispatch. A mutation that completes first is reconciled before a PTY
effect; a bounded Ratox cycle that completes first was admitted under the still-current head. This
closes the check/effect window between `authorized_at()` and process or transport operations without
holding c-toxcore or PTY state inside the authority ledger itself.

### Coordinator ownership

`RatoxService` owns the join between profile resolution, the pure session state, and one PTY
controller per live session. It does not own toxcore, authority, wall clock, or a network thread.
It provides:

- pre-effect reservations for OPEN, ATTACH, RESUME, and controls;
- exact route-scoped duplicate replay and conflicting-message rejection;
- whole-frame input staging with ACK only after complete nonblocking PTY commit;
- retained output history, cumulative ACK, replay, and explicit gaps;
- bounded live sessions, tombstones, admission entries/bytes, outbound packets/bytes, and events;
- attachment replacement and stale-token fencing;
- offline epoch detach without falsely claiming PTY persistence across daemon restart;
- HUP, TERM, KILL, reap, exit publication, and bounded shutdown drain; and
- round-robin cursors across live sessions so global per-cycle bounds cannot starve later PTYs.

### Transport ownership

Outbound Ratox frames remain in service-owned fixed storage until c-toxcore accepts them. A retryable
SENDQ failure leaves the exact front packet untouched. The Agent removes it only after acceptance.
A demonstrably stale or non-retryable route is detached and its retained traffic is discarded under
the same lifecycle transition rather than silently regenerated.

Each retained packet also carries an explicit terminal-authority dependency. Successful admission
results, stream data, acknowledgements, and controls require a fresh exact friend/epoch/principal
decision immediately before send, including after replay. A canonical `DENIED` result created for an
authenticated but unauthorized OPEN/ATTACH/RESUME is the only no-authority exception; it contains no
terminal bytes or accepted attachment identity and remains bounded by the ordinary route/epoch gate.

The Agent sends at most 32 Ratox packets per event-pump cycle. The service separately bounds PTY
write operations, PTY reads, and generated output frames per service cycle.

### Runtime evidence

The private runtime tree publishes Ratox activation and bounded counters plus a rotating
`ratox-events` journal. Lifecycle records may contain route number, online epoch, stable principal,
session identity, frame type, generation/incarnation, sequence positions, and typed error code.
They must never contain terminal bytes, argv, environment values, cwd, filesystem paths, profile
IDs, or error strings.

## Consequences

An explicitly configured experimental Agent can now negotiate bit 23 and dispatch a real Ratox v1
packet through transcript, authority, replay, profile, and PTY boundaries. Normal configurations
continue to advertise no Ratox support. One-sided feature advertisement cannot open the gate.
Queue pressure does not lose an accepted service frame, and one busy PTY cannot monopolize bounded
service work indefinitely.

The construction is intentionally narrower than a release claim. There is no operator terminal
client, no live-PTY recovery after daemon restart, no two-physical-host end-to-end qualification,
no public enablement policy, and no complete namespace/cgroup/seccomp/LSM confinement profile.
R5 through R8 remain independent client, recovery, laboratory, and production-support gates.

## Rejected alternatives

- **Advertise bit 23 whenever a profile path is nonempty.** A path is not proof that policy,
  ownership, bindings, helper, or bounds are valid.
- **Select the HELLO bit before construction and clear it on failure.** A negotiated feature mask
  must be immutable for an online epoch; activation therefore completes before transport startup.
- **Treat ownership or Tox friendship as terminal authority.** Only an exact current signed grant of
  `interactive.terminal` passes the gate.
- **Pop before calling c-toxcore and regenerate after SENDQ.** That loses exact packet ownership and
  can reorder or duplicate terminal bytes.
- **Begin every bounded service cycle at the first session.** A hot first PTY can starve all later
  sessions despite finite per-cycle work.
- **Write diagnostic strings or process policy into the runtime journal.** Operational convenience
  does not justify retaining terminal content or local execution policy.
- **Claim rlimits, UID changes, or `no_new_privs` form a complete sandbox.** They are useful controls,
  not namespace, cgroup, syscall, filesystem, or LSM confinement.
