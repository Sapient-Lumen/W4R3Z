# ADR 0176: Qualify exact auxiliary readiness order

Status: accepted for both corresponding route orders over direct UDP and forced TCP, 2026-08-25.

## Context

ADR 0171 counterbalanced scheduler policy order after every auxiliary route was already ready. It did
not show that the coordinator, reciprocal route binding, immutable-object path, or protected Ratox
depended on which exact auxiliary identity became ready first. Reversing a vector in a mock would not
answer that question because toxcore connection and binding readiness are asynchronous effects.

The first laboratory design started a fixed delay when worker transports finished construction. That
was not a causal readiness gate. Forced TCP could spend the complete delay re-establishing protected
primary authority before the host began observing auxiliary state, making both workers eligible before
the observation. Three earlier direct-UDP attempts also replaced both primary Agents simultaneously
and failed to recover authority. Those were orchestration failures, not route-order evidence.

## Decision

Add two default-off qualification-only `iotox run` options:

```text
--qualify-route-first-worker PUBLIC_KEY_HEX
--qualify-route-other-delay-ms N
```

They are accepted only together, with explicit route workers. The key must be one exact non-primary
member of the authenticated route set. The delay must be 1 through 60,000 milliseconds. Negative,
detached, over-limit, primary, and unknown-key configurations fail before network service.

Every auxiliary transport is still constructed, savedata/key-checked, and assigned its random worker
incarnation before the supervisor thread starts. Only the selected worker is serviced initially. All
other workers remain fail-closed—not merely delayed from construction—until the selected worker has a
confirmed application session and, when route binding is enabled, has sent its local binding and
authenticated the reciprocal binding. The configured delay begins at that causal point. If the
selected worker never reaches it, the other workers remain held. Normal configuration has no selected
key and preserves existing behavior exactly.

The Sandwurm `sync-tree-route-startup-order` cell uses one protected primary plus two signed bulk
identities per guest. It performs savedata-preserving primary Agent restarts through explicit host
barriers, one role at a time. Phase one selects lane 1 on both guests; phase two restarts the same
Agents and selects lane 2. Each phase requires exactly the named local bulk key to be the sole
`lifecycle=ready` route for ten consecutive observations during a 20,000-millisecond post-readiness
hold, then requires both bulk routes ready. Only after both permutations may the ordinary 4 MiB signed
tree converge and the 40-sample protected Ratox probe run.

Direct UDP `pair.nyiqwm8t` and forced TCP `pair.mdacri5e` pass raw and compact verification against
the same exact binary. The maximum first-ready observation is 2,161 ms over UDP and 9,676 ms over
forced TCP. Every role reports two distinct exact first keys, ten stable samples per phase, one
savedata-preserving phase restart, and two final ready bulk routes. Both cells converge the same
artifact, manifest, and signed HEAD and complete all 40 protected Ratox samples below 250 ms.

## Consequences

- Canonical signed route-set order remains authority and is not rewritten to manufacture the result.
- The qualification hold controls worker service eligibility, not toxcore framing, route framing,
  scheduler identity, or production restart policy.
- Startup fails closed when the selected identity cannot authenticate; another route cannot silently
  conceal that failure.
- Primary Agent replacement in this scenario is explicitly rolling. Simultaneous replacement remains
  separate fault science.
- Exact corresponding readiness order is qualified. Random delay distributions, arbitrary partial
  orderings with more workers, and readiness during live faults remain open.
- No byte striping, throughput gain, transparent bonding, physical-path independence, or relay
  diversity is implied.

## Verification

The deterministic worker test proves one exact selected identity is serviced while the other is held,
then both become application-ready only after release. A separate test rejects negative direct-API
delays; CLI tests reject detached, malformed, zero, and over-limit options.

The guest, host runner, strict verifier, and compact exporter recognize one exact scenario. Receipts
bind each phase to the expected local public key, positive sub-delay observation time, at least ten
stable samples, one restart, two final ready routes, native carrier class, signed tree convergence,
and protected Ratox. Raw proofs were independently verified, compacted to 241,664 bytes each, and
replayed before their private guest disks were removed. Exact results and negative observations are
retained in `evidence/2026-08-25-sandwurm-sync-route-startup-order.md`.
