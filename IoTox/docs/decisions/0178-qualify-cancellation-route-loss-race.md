# ADR 0178: Qualify the cancellation and route-loss race

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADRs 0175 and 0177 qualified the two deliberately separated orders around one live auxiliary pull:
loss followed by reassignment and cancellation, and settled cancellation followed by carrier loss.
Neither result exercised cancellation and exact-worker failure from one shared observable edge. A
race could still allow authority state and transport state to disagree: cancellation might become
terminal while loss recovery assigns missing objects elsewhere, or a transport-cancel failure might
leave a locally fenced tombstone that cannot be settled safely.

Host-wide link loss is too broad because it also removes the protected primary and the unaffected
bulk identity. An immediate byte-threshold fault has no observable interval in which the ordinary
local cancellation command can contend with that exact worker stop.

## Decision

Add one bounded delay to the existing default-off progress-first qualification seam:

```text
--qualify-route-stop-after-bytes N
--qualify-route-fault-delay-ms N
```

The delay is valid only with the byte-threshold seam and is limited to 1 through 60,000 milliseconds.
After one active incoming auxiliary transfer reaches the byte threshold, the Agent freezes its exact
route key, worker incarnation, position, and monotonic deadline. Status publishes
`qualification-fault-armed=1`. At the deadline the Agent stops only that frozen worker; a zero delay
retains the historical same-service-pass behavior. This is laboratory control, not production route
policy.

The Sandwurm `sync-tree-route-cancel-race` cell arms after at least 65,536 object bytes, then gives
both the Agent fault deadline and the client cancellation path 500 milliseconds from the same
observed arm edge. Worker stop and the ordinary `sync-cancel` operation are independent until route
loss fencing/reassignment and cancellation serialize on the existing authority-effect mutex. The
accepted terminal outcomes are therefore explicit:

- `cancel-first`: the pull is terminal before reassignment, so loss count is one, reassignment is
  zero, and its retained final carrier remains the stopped carrier;
- `loss-first`: loss fencing wins and assigns once before cancellation, so the terminal pull retains
  the distinct replacement carrier.

Both outcomes require one carrier loss, no more than one reassignment, one route recovery, work
drained to zero, no incoming transfer or staging, and no accepted HEAD or activation. Adaptive
selection count must equal initial admission plus the observed reassignment count.

Cancellation already fences local durable and scheduler truth before transport cleanup. If the
target worker disappears inside that effect, the first command may return typed `unavailable` even
though the job is terminal. The cell permits exactly one ordinary `sync-cancel` cleanup retry only
after that typed result. Existing subscriber semantics make the retry settle the same tombstone
without repeating the transport-cancel effect; any other error, a second retry, or residual state
fails the gate.

Direct UDP `pair.h6kg4fcr` and forced TCP `pair.z9egqd57` both selected `cancel-first`. Each required
one exact cleanup retry, reported one loss, zero reassignment, two stale terminals, one recovery,
restored both bulk identities, and completed 40 protected Ratox samples below 250 ms against the same
binary.

## Consequences

- A carrier loss racing ordinary cancellation cannot reopen or migrate a pull once cancellation has
  won the authority-state serialization point.
- Transport cleanup failure remains visible and typed. Idempotent retry settles an already-fenced
  pull instead of disguising the edge as success or repeating the external effect.
- The verifier also accepts and self-tests the bounded `loss-first` linearization even though the two
  accepted 500/500 ms cells observed `cancel-first`.
- Route recovery restores capacity only. It cannot accept a HEAD, activate a tree, or revive the
  terminal pull.
- No protocol framing, signed inventory, authority capability, scheduler identity, or production
  default changes.
- This is one shared-arm timing cell per carrier, not a probability distribution or proof over every
  scheduler interleaving. Randomized delays, startup during faults, multiple affected pulls on one
  carrier, larger-object/common-link QoS, relay diversity, and long-running production policy remain
  open.

## Verification

CLI coverage rejects zero, detached, and over-limit delay values. The genuine guest, pair runner,
strict verifier, compact exporter, and shell registry recognize the race scenario and require strict
zero defaults elsewhere. Both role receipts agree on outcome, delays, and cleanup-retry count; only
the client may claim direct observation. Pair verification binds outcome to reassignment count and
final/stopped carrier equality, as well as cancellation, route recovery, protected Ratox, carrier
class, receipts, binary, and every compact-file digest.

Both raw cells passed strict verification. Their 241,664-byte compact exports independently replayed
after export. Exact results and nonclaims live in
`evidence/2026-08-26-sandwurm-sync-route-cancel-race.md`.
