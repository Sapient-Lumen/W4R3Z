# Simulation and chaos frontier

Revision: rev0028

BrowserRT will not scale if every logic bug requires launching Chromium, creating real workers, writing OPFS files, and hoping timing behaves. The future testing facility needs three layers:

```txt
real browser proofs     prove platform integration
fake provider tests     prove runtime contracts cheaply
simulation/chaos tests  prove behavior under schedules and faults
```

## Deterministic simulation target

A future simulator should replace:

- time;
- worker scheduling;
- storage provider;
- queue wakeups;
- provider failures;
- capability changes;
- tab visibility;
- mesh messages.

The simulator should write a seeded history so a failure can be replayed.

## Jepsen-style history pressure

Future chaos artifacts should have:

```txt
seed
operations
faults
observations
invariant checkers
minimal failure summary
```

BrowserRT chaos should not be only "randomly kill things." It should ask: after cancellation was acknowledged, did any cancelled task complete? After a worker died, did object refs leak? After quota pressure, did storage spill/fail policy match the contract?

## Metamorphic pressure

Metamorphic tests can vary legal runtime choices while preserving expected semantics:

- `capacity = 1` vs `capacity = 8`;
- one worker vs many workers;
- clone vs transfer fallback;
- different scheduling orders preserving dependencies;
- fake provider vs browser provider;
- eager teardown vs delayed teardown.

The invariant is not timing equality. The invariant is ownership safety, result safety, cancellation safety, and trace completeness.

## Current status

Rev0008 does not implement simulation or chaos. It records the frontier so future tests do not become giant nondeterministic browser blobs.
