# Validation slice — storage-lane retry budget

Revision: rev0029
Task: `scheduler:storage-lane-retry-budget-proof`
Artifact: `artifacts/validation/REV0044-STORAGE-LANE-RETRY-BUDGET-PROBE.json`

## Purpose

Prove, in a fake-provider release-tier setting, that storage-lane retries can be governed by an explicit retry-budget/admission controller before a delayed retry is scheduled.

## What it proves

- `RetryBudgetAdmissionController` exists and emits trace events.
- `StorageLaneRetryController` integrates with a retry budget gate.
- A retry consumes a credit, releases active retry accounting, and succeeds only after explicit provider recovery.
- Exhausted retry budget rejects a retry without a second provider mutation.
- Non-idempotent retryable work is rejected by the gate.
- Active retry limit rejects a second active retry.
- Provider-unhealthy state rejects retry admission.
- Primary observation can refill retry credits.
- Critical priority can bypass exhausted credits in the proof, while still releasing active accounting.

## Why this belongs before OPFS/browser spending

OPFS retry behavior will be expensive to test and easy to overclaim. The fake-provider slice lets future sessions settle vocabulary around credits, active retry leases, idempotency, provider health, and trace evidence first.

## Run command

```bash
node tools/storage_lane_retry_budget_probe.mjs --json artifacts/validation/REV0044-STORAGE-LANE-RETRY-BUDGET-PROBE.json
```

## Non-claims

- No OPFS storage-lane retry-budget proof.
- No browser Worker storage-lane retry-budget proof.
- No retry-storm safety or production overload-governance claim.
- No wall-clock timer, throughput, latency, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once delivery claim.
