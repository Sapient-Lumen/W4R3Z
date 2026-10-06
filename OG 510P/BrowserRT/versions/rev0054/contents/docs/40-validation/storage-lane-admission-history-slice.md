# Validation slice — storage-lane admission history proof

Current revision: rev0054

Manifest id:

```txt
scheduler:storage-lane-admission-history-proof
```

Command:

```bash
node tools/storage_lane_admission_history_probe.mjs --json artifacts/validation/REV0044-STORAGE-LANE-ADMISSION-HISTORY-PROBE.json
```

## What it proves

This release-tier fake-provider slice proves that `StorageLaneAdmissionHistoryRunner` can guard provider-resilience histories with a watermark/provider-health admission layer.

Required observations:

- success under admission executes and releases the admission lease;
- transient provider failure can retry successfully under admission;
- watermark rejection causes no provider mutation;
- critical priority can bypass congestion and still release its lease;
- provider-health rejection causes no provider mutation;
- provider-health recovery admits later work;
- hard-limit rejection causes no provider mutation;
- snapshots validate;
- all admission, breaker, and retry-budget leases are empty at the end;
- boot report records `storageLaneAdmissionHistoryProof`;
- required trace events are present.

## Why this belongs before OPFS

OPFS tests are expensive and browser/CDP-bound. This slice establishes the admission/release/no-mutation contract cheaply before a storage provider with real browser fixture cost enters the stack.

## Non-claims

This slice is fake-provider, deterministic, and browser-light. It does not prove OPFS, browser Worker behavior, real timers, crash recovery, quota, eviction, throughput, latency, fairness SLOs, production admission control, or exactly-once delivery.

Rev0036 note: the generated model-oracle extension is `StorageLaneAdmissionHistoryModelOracle`, proved by `scheduler:storage-lane-admission-model-proof`; this does not replace the targeted history proof.
