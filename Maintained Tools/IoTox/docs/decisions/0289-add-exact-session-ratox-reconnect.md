# ADR 0289: add exact-session Ratox reconnect

Status: accepted 2026-09-01.

## Context

Ratox v1 already retains a device-side PTY across authoritative route loss and permits explicit
resume only on a higher authenticated application epoch. The ordinary CLI nevertheless exits on
that loss, forcing an operator to copy the session ID and invoke `terminal-resume`. The missing
ergonomic layer is local lifecycle, not a new terminal or transport protocol.

Automatic retry must not interpret a heartbeat miss as route truth, open a replacement shell, attach
on the old epoch, change peer/principal/profile, or conceal loss of the session after either Agent
restarts.

## Decision

Add `iotox terminal PEER_PUBLIC_KEY_HEX --reconnect`. After the initial OPEN succeeds, the CLI retains
only the exact returned session ID, host incarnation, and attachment generation. An authoritative
local `unavailable` ends the current attachment and enters a fixed 500 ms, signal-interruptible retry
loop. Every attempt reconnects to the same owner-local socket and sends `resume_only` for the exact
peer and session. The existing Agent/Ratox client remains the authority: it refuses an absent route,
an unchanged epoch, changed principal/peer, lost session, or conflicting controller.

The CLI additionally refuses a successful response unless session and incarnation are byte-exact and
generation increases. It never changes the request back to new-session mode. `not_found`, authority/
identity disagreement, protocol errors, and resource conflicts terminate visibly. `--reconnect` is
interactive-only and cannot be combined with `--batch` or `terminal-resume`.

## Consequences

One ordinary terminal invocation can cross repeated carrier outages while the same controller Agent,
device Agent, and retained PTY survive. Input already accepted by the local Agent stays governed by
Ratox's existing exact input ACK/replay path; the CLI creates no second input journal. Output resumes
from the Agent's returned cursor and preserves explicit output-gap reporting.

The process test forces authoritative loss, refuses two resume attempts, then returns generation 2.
It proves exactly one OPEN, one successful RESUME, retained output rendering, and clean detach. This
does not prove genuine Tox outage duration, daemon/host restart survival, Mosh screen-state prediction,
roaming UDP, or a long-running deployment soak. Peer and local-terminal framing remain unchanged.
