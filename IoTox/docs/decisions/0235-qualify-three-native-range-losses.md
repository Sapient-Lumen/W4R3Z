# ADR 0235: Qualify three sequential native bounded-range losses

Status: accepted with genuine direct-UDP and forced-TCP Sandwurm qualification, 2026-08-29.

## Context

ADR 0232 proves two sequential losses of one native `available`-policy range. The deterministic
subscriber fixture already carries one growing prefix through three carriers, but the genuine gate
stops after two losses and ends on the initially stopped identity. A third loss exercises another
complete recovery-before-refault cycle, exhausts one member's two-restart budget, and ends on the
other identity. That is a distinct topology and lifecycle boundary, not merely a larger counter.

The gate must remain bounded. The request hold introduced by ADR 0232 exists only to keep each
replacement range from winning a timing race against recovery of the route needed for the following
fault. It is not production scheduling and must not become an unbounded fault injector.

## Decision

- Keep `--qualify-route-stop-count` default-off and expand its strict bound from `1|2` to `1|2|3`.
  The ordinary default remains one. Four and larger values fail before startup.
- Add a separate `sync-file-range-triple-route-loss` scenario. Reuse the exact 1 MiB selected range,
  256-kbit/s shaping, 262,144-byte fault threshold, two authenticated native auxiliaries, and
  recovery-before-refault ordering from ADR 0232.
- Give only this named cell a signed two-restart budget per bulk member and a 1,800-second guest/
  convergence deadline. Existing scenarios keep their one-restart policy and shorter bounds.
- Hold and release the exact reassigned request after losses one and two. The bounded qualification
  queue must end empty and report exactly two releases; product and one-fault paths remain empty.
- Require exactly three qualification faults, carrier losses, reassignments, stale-terminal fences,
  route recoveries, retained attempts, resumed attempts, and aggregate worker restarts. Cumulative
  retained and resumed bytes must match; discard, fallback, final retained partials, and ordinary
  range-retry accounting must remain zero.
- Require the final carrier to differ from the initially stopped carrier. With two members, this
  proves the expected A-to-B, B-to-A, A-to-B alternation rather than accepting three observations of
  one route event.
- Require the initially stopped savedata identity to return ready after its second bounded restart,
  with `restarts=2`, the signed ceiling `restart-budget=2`, and
  `restart-budget-remaining=0`. Both ready bulk members must still be present at evidence release.
- Preserve range-v1 framing, signed attempts, HEAD and authority formats, FileId construction,
  complete digest verification, accepted-HEAD-last ordering, and explicit activation unchanged.

## Evidence gate

The first genuine direct-UDP attempt correctly reached two losses and two request releases, then
exposed inherited two-loss limits: each signed member had only one restart and the publisher reached
the 1,200-second guest deadline before attempt six progressed. Diagnostic root `pair.7tfxwohw` is
not acceptance evidence. After the lab-only budget/deadline correction, diagnostic root
`pair.6d2wjm68` advanced attempt six to 289,281 bytes but remained at fault count two. This exposed a
qualification-latch bug: next-fault arming depended only on a transient offline-set recovery edge,
while the request release correctly used the stronger current exact-key/new-worker readiness level.
The latch now accepts that same level predicate; ordinary one-fault and production paths cannot
enter the branch.

A third interrupted calibration, `pair.4zvkhl5g`, reached the same second request release but left
attempt six at zero long enough to distinguish it from the arming defect. The triple cell now writes
atomic, content-free publisher `sync-status` and `routes` watchdog snapshots while waiting. Raw
failure diagnostics and compact evidence retain both records; they do not affect peer traffic.

The next instrumented calibration, diagnostic root `pair.ge_y8h28`, proved that the sixth request
was not the blocker. Both publisher bulk transports were running at online epoch two, yet both were
stuck with `application-ready=0`, no local or authenticated remote binding, and an authentication
failure after the subscriber had restarted both corresponding worker identities. A HELLO accepted
into the local toxcore queue during the peer's preceding offline application epoch could be rejected
there while the sender treated enqueue as a one-shot success. ADR 0236 now retries the exact frozen
HELLO and CAPABILITIES records at a one-second cadence until confirmation, exposes their attempt
counters in route diagnostics, and adds a deterministic accepted-but-unobserved-packet regression.
It changes no range, binding, authority, or wire format. `pair.ge_y8h28` remains diagnostic rather
than acceptance evidence.

The first post-handshake-fix UDP run, diagnostic root `pair.fdskk7te`, then advanced far enough to
fail closed at the next independent resource boundary: attempt six reported 542,916 exact retained/
resumed bytes, zero discard/fallback, and `sync scheduler attempt tombstone bound is exhausted`.
The hidden four-record scheduler ceiling covered one manifest plus the initial range and two
replacements, but not the replacement required after loss three. ADR 0237 now derives this fence
history bound from the validated host-local namespace request quota, exports its current/bound
counters, and raises only the triple fixture from four to the exact required five. No tombstone is
evicted. `pair.fdskk7te` is diagnostic, not acceptance evidence.

The next UDP run, diagnostic root `pair.g6nix_0l`, completed the third loss, third exact reassignment,
all three recoveries, and the range itself. Its receipt then failed on an evidence-only assertion
which read `restart-budget` as a decrementing remainder. That field has always rendered the signed
ceiling; the coordinator separately records consumption in `restarts`. ADR 0238 adds the explicit
derived `restart-budget-remaining` field and makes the gate require the unambiguous tuple
`restarts=2 restart-budget=2 restart-budget-remaining=0`. The diagnostic remains non-acceptance
evidence because the guest deliberately failed before releasing its signed receipt.

A clean post-correction rerun, diagnostic root `pair.iodmwn14`, did not enter the fault gate. Both
guests had two authenticated range-capable auxiliaries and the baseline moved its expected byte
volume, but the subscriber never emitted generation-1 completion before the bounded host timeout.
Read-only recovery of its stopped disk found the complete 4 MiB artifact committed, no manifest,
no staging inode, and an empty durable-attempt set at high-water four. This localizes the stall to
pre-successor baseline object scheduling/offer truth, not restart-budget rendering or range
handoff. The triple fixture now projects atomic content-free client and publisher `sync-status` plus
`routes` snapshots during baseline convergence and includes them in a bounded host-timeout error;
successful baseline completion removes those transient diagnostics before acceptance evidence.
`pair.iodmwn14` remains diagnostic.

Clean direct-UDP root `pair.3iufekzy` and forced-TCP root `pair.zleebk2k` complete all substantive
postconditions. They retain/resume 862,359 and 871,956 bytes respectively through three exact
handoffs, advance attempts 4 through 7, report three lifecycle events and worker restarts, release
two held requests, exhaust the initially stopped route at the unambiguous `2/2/0` consumed/ceiling/
remaining tuple, and converge with zero discard or fallback. One identical production binary serves
both cells. Each raw result passes the strict offline verifier, exports without secrets into a
176,128-byte compact root, and passes the same verifier again. The owned CLI, runner, verifier,
exporter, shell, Nix-evaluation, build, and unit checks pass. The exact bindings are retained in
`evidence/2026-08-29-sandwurm-sync-range-triple-route-loss.md`.

## Consequences

This makes three sequential native range-carrier losses a named, reproducible gate without
widening ordinary scheduling or wire semantics. It also proves exact restart-budget exhaustion is a
healthy final state when the route is ready and its last failure has cleared.

The accepted cells close exactly this bounded three-loss row. They do not prove four-plus losses,
repeated late or final-chunk races, randomized timing, daemon/guest restart
of a range bundle, I2P or Tor continuation, concurrent multi-source striping, two physical hosts, or
a performance improvement.
