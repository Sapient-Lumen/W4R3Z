# Scheduler model audit — rev0036

Manifest id: `facility:scheduler-model-contract-audit`.

## Purpose

This audit keeps the new model-walk stair visible and coherent for future sessions and records the coherence checks in an explicit audit artifact. It does not prove scheduler correctness. It checks that the model proof, manifest task, impact map, surface inventory, docs, runtime boot surface, receipt, and non-claim surfaces agree.

## Command

```bash
node tools/scheduler_model_contract_audit.mjs --json artifacts/audit/REV0044-SCHEDULER-MODEL-CONTRACT-AUDIT.json
```

## What it checks

- `scheduler:cross-lane-model-walk-proof` exists and is release-tier.
- `facility:scheduler-model-contract-audit` exists and is release-tier.
- The impact map and surface inventory include the new scheduler model surface.
- The proof artifact reports 18 scenarios, at least 3,240 generated/random steps plus scripted setup operations, snapshot comparisons, model agreement, capacity waits, dependency deferral, fallback routing, and required traces.
- `src/browserrt.mjs` exposes the `crossLaneSchedulerModelProbe` boot-report bit.
- The future-session office and non-claims charter preserve the model non-claims.

## Non-claims

- No exhaustive formal verification claim.
- No production scheduler claim.
- No browser Worker scheduler proof.
- No real threaded interleaving proof.
- No latency, throughput, fairness-SLO, or cross-browser claim.

This audit is a coherence guard: it checks docs, manifest, impact map, inventory, proof artifact, runtime export, and non-claim surfaces together.


## rev0036 carry-forward note

This current-revision carry-forward document keeps the older proof/audit boundary visible while rev0036 adds the circuit-breaker/bulkhead model oracle. It does not upgrade any OPFS, browser, production, performance, durability, or formal-verification claim.


## Rev0034 carry-forward note

This is a current-revision carry-forward audit surface retained so release-tier audit tools can run against rev0036 artifacts while the new provider-resilience model proof is the active slice.



Current revision: rev0055
