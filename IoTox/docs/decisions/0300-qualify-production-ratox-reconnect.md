# ADR 0300: Qualify production Ratox reconnect across real route loss

- Status: accepted and implemented
- Date: 2026-09-02

## Context

ADR 0289 proved the `terminal --reconnect` state machine against a controlled local server. ADR
0197 separately proved that a private terminal controller could cross genuine Tox route loss while
the remote Agent retained its PTY. Neither gate proved the operator claim that one unmodified
production CLI process survives the real transport outage and resumes that exact retained PTY.

That distinction matters. A test that speaks the private terminal socket can validate protocol
mechanics while missing PTY/raw-terminal behavior, retry timing, local process lifetime, output
rendering, selector resolution, or CLI detach semantics.

## Decision

Add the Sandwurm `ratox-cli-reconnect` scenario and
`tools/ratox-cli-reconnect-probe.py`. The probe forks one pseudo-terminal and executes the real
`iotox terminal PEER --reconnect` command. It never opens or encodes the private terminal socket.
The pair runner then:

1. proves one input/output byte and one healthy production heartbeat interval;
2. installs independently seeded 100% netem loss on both task-owned guest TAPs;
3. requires the CLI heartbeat warning while the authenticated session still reports its original
   carrier and epoch;
4. waits for authoritative toxcore offline, then requires the device to retain exactly one live,
   running, zero-attached PTY and a matching `peer-detached` event;
5. removes both qdiscs and permits the same CLI process to retry;
6. accepts only the same session and incarnation at a higher authenticated online epoch and
   attachment generation;
7. proves the next exact input/output sequence, healthy heartbeat, local `~d` detach, and process
   exit status zero.

The lifecycle receipt binds the CLI PID and `/proc/PID/stat` start ticks, zero process restarts,
session commitment, incarnation, generations, epochs, retry count, byte sequences, phase ordering,
and output commitment. The generic terminal and heartbeat captures remain separately joined.
`terminal-sessions` now preserves its single trailing record newline after metadata sanitization;
otherwise a valid numeric `output-next` field was rendered with a trailing `?` and could not be
machine-read during the retained-PTY observation.

Direct UDP and forced TCP use the same source-linked IoTox binary. The independently verified raw
and content-free compact cells are recorded in
`docs/evidence/2026-09-02-sandwurm-ratox-cli-reconnect.md`.

## Consequences

The ordinary IoTox owner experience now has a genuine two-guest proof: one terminal invocation can
survive total carrier loss and resume one exact live shell above both native UDP and relay-only TCP.
No replacement process or shell can satisfy the verifier, and a mere heartbeat warning still cannot
authorize state mutation.

This remains route continuity, not daemon-independent terminal supervision. Device-Agent death,
host reboot, PTY death, session eviction, identity change, unchanged epoch, or incompatible profile
still terminates rather than manufacturing continuity. One outage per route on one construction
host is not a duration SLO, repeated-loss soak, public-network qualification, Tor/I2P qualification,
Mosh screen-state convergence, or production security certification. Ratox v1 and the local terminal
protocol remain unchanged.
