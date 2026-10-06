# Provider-resilience model contract audit — rev0035

Current revision: rev0054

Manifest id:

```txt
facility:provider-resilience-model-contract-audit
```

Command:

```bash
node tools/provider_resilience_model_contract_audit.mjs --json artifacts/audit/REV0044-PROVIDER-RESILIENCE-MODEL-CONTRACT-AUDIT.json
```

The audit reruns `scheduler:provider-resilience-model-proof` and then checks source/runtime/export/docs/manifest/impact/inventory/research/non-claim coherence.

## Audit focus

- `src/provider-resilience-model.mjs` exports `ProviderResilienceModelOracle`.
- `src/provider-resilience-history.mjs` carries the operation-level max-attempt leak fix.
- `src/browserrt.mjs`, `src/ipc.mjs`, and `src/types.d.ts` expose model-oracle surfaces.
- Manifest, impact map, and surface inventory cover the proof and audit tasks.
- Research registry carries the rev0035 model/history sources.
- Future-session handoff docs carry provider-resilience model non-claims.

## Non-claims

The audit proves cube coherence only. It does not prove runtime performance, OPFS/browser behavior, production resilience, exactly-once delivery, or formal verification.
