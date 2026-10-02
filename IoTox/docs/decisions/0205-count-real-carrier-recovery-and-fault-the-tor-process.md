# ADR 0205: Count real carrier recovery and fault the Tor process

Status: accepted, implemented, and bounded-live-qualified, 2026-08-27.

## Context

ADR 0204 attributes one complete signed-tree job to an exact auxiliary member whose network context
is a separately controlled Tor process. It does not show what happens when that process disappears
after positive object progress. The earlier route-loss cells stop an IoTox worker through a
qualification-only hook, so they cannot establish that a surviving native member takes over a job
whose independently supervised privacy transport failed.

The existing `auxiliary-recoveries` counter also advanced only when that synthetic hook requested a
worker restart. An ordinary qualified carrier could disappear and return without incrementing it.
That made the name narrower than the production lifecycle and left actual proxy recovery without a
direct content-free observation.

## Decision

Count one auxiliary recovery when a previously observed offline route key becomes qualified again.
Keep the offline-key set bounded by the signed route inventory and guarded by the existing carrier
mutex. Remove the qualification hook's eager increment: recovery now means the carrier actually
returned, not merely that restart was requested. Existing synthetic-loss evidence must still report
one loss, one reassignment, and one recovery.

Add `sync-tree-route-private-actual-tor-loss` as a distinct Sandwurm cell. It retains the stable-key
ordering from ADR 0204 and rate-limits a 16,777,513-byte treepack transfer to 4 Mbit/s. The larger
qualification object leaves a bounded observation window after the guest binds at least 65,536 but
fewer than all artifact bytes to the exact Tor carrier. The host then:

1. captures authenticated pre-loss Tor STREAM/CIRC, process, socket, and circuit evidence;
2. sends `SIGKILL` to that client Tor process group, not to IoTox or its route worker;
3. waits for the guest to report one carrier loss and one reassignment to a different exact member;
4. starts the same pinned Tor binary with the same private configuration and data directory; and
5. releases the guest only after Tor has bootstrapped again.

Acceptance requires complete signed-tree convergence, one stale terminal, one carrier recovery,
two ready bulk members, zero route-worker restarts for the externally faulted member, and
`qualification-fault=0`. The completed job's final carrier must differ from the stopped Tor member.
The stopped member commitment must agree across the live guest receipt, host process-loss record,
and private-route Tor-member commitment. Pre-loss and recovered client Tor processes must have
different PIDs and independently authenticated control/circuit evidence. The device Tor process
remains continuous. Both TAP captures must retain zero unexpected context packets.

## Consequences

- Recovery telemetry now describes real carrier lifecycle and remains compatible with the synthetic
  loss gates.
- The experiment distinguishes Tor-process failure from route-worker failure: the Tox worker may
  remain alive while its qualified peer association disappears and returns.
- Reassignment can complete the immutable object over a native auxiliary without weakening digest,
  manifest, activation, or authority checks. This is availability behavior, not a claim that mixed
  carriers preserve Tor anonymity.
- The exact loss-detection and Tor-bootstrap durations are retained as measurements, not protocol
  deadlines.
- A passing cell remains one host, one relay record, one time window, and one bounded object. Wider
  relay/exit/time matrices, long soaks, adversarial local proxies, and I2P remain open M8 gates.

## Qualification

Accepted compact proof `pair.iompvehf` ran clean commit `ee74a95` and independently reverified. The
host killed only the client Tor process after 74,034 object bytes. The guest then recorded exactly
one carrier loss, one reassignment to the native auxiliary, two stale terminals, one real carrier
recovery, two ready bulk members, and zero IoTox route-worker restarts while the signed
16,777,513-byte treepack converged. Pre-loss and recovered Tor evidence has distinct process/control
identities, the device Tor process remained continuous, and both TAP captures contain zero
unexpected-context packets. See
`../evidence/2026-08-27-sandwurm-actual-tor-process-loss.md`.
