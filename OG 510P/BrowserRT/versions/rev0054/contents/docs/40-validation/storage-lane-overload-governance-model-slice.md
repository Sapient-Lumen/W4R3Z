# Slice: scheduler:storage-lane-overload-governance-model-proof

Current revision: rev0054

This slice is the next fake-provider/release-tier stair after the storage-lane admission-history model. It composes admission, retry-budget, circuit-breaker/bulkhead, storage-lane executor, provider-resilience history, persisted-spill mailbox, and memory block provider behavior under a small model oracle.

## What it proves

The proof exercises targeted and generated histories and requires all of these to be observed:

- success under governance;
- transient provider failure recovered by retry;
- retry-budget exhaustion;
- non-idempotent retry rejection;
- bulkhead rejection;
- open-circuit rejection;
- watermark admission rejection;
- admission provider-health rejection;
- hard-limit rejection;
- critical bypass;
- no provider mutation on rejected finals;
- admission lease release accounting;
- required trace events.

## How to run

```bash
node tools/storage_lane_overload_governance_probe.mjs --json artifacts/validation/REV0044-STORAGE-LANE-OVERLOAD-GOVERNANCE-PROBE.json
node tools/storage_lane_overload_governance_contract_audit.mjs --json artifacts/audit/REV0044-STORAGE-LANE-OVERLOAD-GOVERNANCE-CONTRACT-AUDIT.json
```

## Why this is not browser/OPFS yet

The cost-sensitive cloudtainer plan is to prove semantics with fake providers first. OPFS/browser tests remain explicit-tier spending. This slice protects the contract that OPFS/browser providers should eventually satisfy.

Runtime noun: `StorageLaneOverloadGovernanceModelOracle`.
