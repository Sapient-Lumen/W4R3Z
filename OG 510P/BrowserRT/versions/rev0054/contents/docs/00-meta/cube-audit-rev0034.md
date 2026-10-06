# Cube audit rev0035 — provider-resilience model oracle

Current revision: rev0054

This audit/refactor pass added the provider-resilience model proof and corrected a real lease-accounting issue discovered while building the model slice.

## What was found

When an operation supplied `maxAttempts` lower than the retry policy's own max attempts, `ProviderResilienceHistoryRunner` could acquire a retry-budget lease after the caller's last allowed attempt. The operation then exited through the loop-exhaustion path with active retry-budget accounting left behind.

## What changed

- Added `src/provider-resilience-model.mjs`.
- Added `ProviderResilienceModelOracle` runtime/export/type surfaces.
- Added `tools/provider_resilience_model_probe.mjs`.
- Added `tools/provider_resilience_model_contract_audit.mjs`.
- Fixed `ProviderResilienceHistoryRunner` so operation-level `maxAttempts` wins before another retry lease is acquired.
- Added docs and manifest surfaces for `scheduler:provider-resilience-model-proof` and `facility:provider-resilience-model-contract-audit`.

## Testing posture

Broad release remains browser-light. The new model proof is release-tier and fake-provider only. Browser/OPFS spending is still deferred until fake-provider histories earn more confidence.
