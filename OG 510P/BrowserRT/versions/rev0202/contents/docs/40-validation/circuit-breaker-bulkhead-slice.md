# Validation slice — circuit-breaker/bulkhead proof

Revision: rev0031

Task id:

```txt
scheduler:circuit-breaker-bulkhead-proof
```

Command:

```bash
node tools/circuit_breaker_bulkhead_probe.mjs --json artifacts/validation/REV0044-CIRCUIT-BREAKER-BULKHEAD-PROBE.json
```

## What it proves

- Controller creation.
- Bulkhead capacity rejection without active-lease mutation.
- Count-window failure threshold opens the circuit.
- Open circuit rejects without active-lease mutation.
- Virtual ticks move open circuits to half-open.
- Half-open probe limits reject excess probes.
- Successful half-open probes close the circuit.
- Failed half-open probe reopens the circuit.
- Slow-call rate can open the circuit independently of outright failures.
- Runtime factory and snapshot validator are wired.
- Required trace events are present.

## Why release-tier

This is fake-provider, virtual-tick, no browser, no OPFS, no wall-clock timer, and no performance measurement. It is cheap enough to belong in the browser-light release gate.

## Non-claims

- No OPFS circuit-breaker/bulkhead proof.
- No browser Worker circuit-breaker/bulkhead proof.
- No production circuit-breaker/bulkhead algorithm claim.
- No latency, throughput, SLO, real-time timer, durability, or cross-browser claim.

## Runtime noun

`CircuitBreakerBulkheadController` is the runtime noun under proof in this slice.
