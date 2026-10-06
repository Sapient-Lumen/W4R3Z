# Validation slice — circuit-breaker/bulkhead model oracle

Carry-forward revision: rev0033.

Manifest task:

```txt
scheduler:circuit-breaker-bulkhead-model-proof
```

Command:

```bash
node tools/circuit_breaker_bulkhead_model_probe.mjs --json artifacts/validation/REV0044-CIRCUIT-BREAKER-BULKHEAD-MODEL-PROBE.json
```

## Evidence required

The proof artifact must show:

- deterministic replay matches;
- real/model agreement after every generated step;
- targeted observations for bulkhead rejection, failure threshold, slow-call threshold, open rejection, half-open success close, half-open failure reopen, forced-open rejection, manual close, and unknown release;
- rejection no-lease-growth evidence;
- final snapshots validate;
- final active lease accounting is empty;
- required trace events exist;
- non-claims are explicit.

## Release posture

This is release-tier, Node-only, fake-provider, and browser-light. It should stay cheap enough to run inside every package gate.

## Non-claims

- No OPFS circuit-breaker/bulkhead model proof.
- No browser Worker circuit-breaker/bulkhead model proof.
- No real wall-clock timer claim.
- No production resilience or SLO claim.
- No exhaustive model checking or formal verification claim.

Runtime noun under test: `CircuitBreakerBulkheadController`.
