# Circuit-breaker/bulkhead model frontier

Carry-forward revision: rev0033.

The rev0031 proof established direct examples for `CircuitBreakerBulkheadController`. Rev0032 adds a model oracle so the controller must agree with an independent reference model across generated histories.

## Contract under test

The model oracle covers:

- `tryAcquire()` admits or rejects work.
- Bulkhead capacity rejection must not grow active lease accounting.
- Closed-state releases update a bounded sliding window.
- Failure-rate threshold can open the circuit.
- Slow-call-rate threshold can open the circuit.
- Open state rejects calls.
- Virtual ticks can move open state to half-open.
- Half-open successful probes can close the circuit.
- Half-open failed probes can reopen the circuit.
- Forced-open state rejects calls until manual close.
- Unknown releases do not mutate active lease accounting.

## Reference model rule

The reference model is intentionally smaller than the implementation. It mirrors public semantics, not private trace details. The proof compares stable snapshot fields after each generated operation.

## Why generated histories now

Targeted examples prove that expected cases work. Generated histories are better at catching awkward sequences: unknown releases after transitions, rejections after forced-open, half-open transitions after virtual ticks, and draining outstanding leases after mixed operations.

## What future sessions should not infer

- The model is finite and deterministic.
- The model is not formal verification.
- The model does not cover true concurrent interleavings.
- The model does not use wall-clock timers.
- The model does not prove OPFS, browser, WebGPU, cross-tab, or production provider behavior.

## Next earned stair

The next resilience stair should be provider-integrated histories: run a fake storage-lane operation through circuit/bulkhead plus retry-budget/admission and compare the full policy-chain history to a small reference model. Do that before browser/OPFS spending.

Explicit current non-claim: No OPFS circuit-breaker/bulkhead model proof.
