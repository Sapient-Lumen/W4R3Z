# Storage-lane admission model frontier

Current revision: rev0055

`StorageLaneAdmissionHistoryModelOracle` is the reference-model counterpart to `StorageLaneAdmissionHistoryRunner`.

## Runtime nouns

```txt
StorageLaneAdmissionHistoryRunner       real fake-provider slice
StorageLaneAdmissionHistoryModelOracle  independent reference model
compareStorageLaneAdmissionHistoryToModel(real, model, provider)
```

## Model state

The model tracks:

- `inFlightBytes`;
- `heldLeaseCount`;
- congestion/high-watermark state;
- provider health;
- provider block count;
- operation counts;
- admission rejects by cause;
- critical bypass count;
- no-mutation rejections;
- direct held lease/release counts.

## What the model deliberately ignores

The model does not attempt to simulate the full storage provider, retry scheduler, circuit-breaker implementation, OPFS, browser workers, timers, or real concurrency. It treats the provider-resilience runner as a known fake-provider dependency and verifies the admission boundary around it.

## Invariant pressure

The proof should fail if:

- real admitted/rejected counts drift from the model;
- a rejected operation mutates provider block count;
- a held lease leaks;
- provider-health rejection differs between real and model;
- hard-limit or watermark behavior drifts;
- critical bypass is not represented in both real and model;
- final accounting is non-empty.

## Claim promotion rule

A future session may promote a stronger claim only after adding a named provider, a proof artifact, a trace surface, and explicit non-claim updates. This model by itself does not earn OPFS, browser, performance, durability, or production scheduler claims.
