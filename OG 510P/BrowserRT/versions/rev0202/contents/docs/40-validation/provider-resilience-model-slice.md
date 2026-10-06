# Validation slice — provider-resilience model proof

Current revision: rev0055

Manifest id:

```txt
scheduler:provider-resilience-model-proof
```

Command:

```bash
node tools/provider_resilience_model_probe.mjs --json artifacts/validation/REV0044-PROVIDER-RESILIENCE-MODEL-PROBE.json
```

## What it proves

The slice compares `ProviderResilienceHistoryRunner` against `ProviderResilienceModelOracle` over targeted and deterministic generated fake-provider histories.

Required observations:

- 22 scenarios run.
- 18 generated scenarios run.
- more than 90 operations run.
- aggregate real/model outcome agreement holds.
- transient retry success matches the model.
- retry-budget exhaustion matches the model.
- non-idempotent retry rejection matches the model.
- open-circuit rejection matches the model.
- primary success matches the model.
- successes and failures are both present.
- model snapshots validate.
- final breaker and retry-budget lease accounting is empty.
- runtime boot report records `providerResilienceModelProof`.
- required trace events are present.

## Bug class guarded

This slice specifically guards against a retry-budget lease leak where an operation-level max-attempt cap is lower than the retry-policy max-attempt cap.

## Non-claims

This is fake-provider, release-tier, and browser-light. It does not prove OPFS, browser Worker behavior, true concurrent histories, production retry-storm safety, throughput, latency, durability, exactly-once delivery, or formal verification.
