# Provider-resilience history contract audit — rev0033

Carry-forward revision: rev0033

This audit keeps the provider-integrated resilience slice legible for future sessions. It checks that the source, runtime exports, IPC exports, type declarations, manifest, impact map, surface inventory, research registry, proof artifact, and non-claim handoff surfaces all point at the same earned slice.

Current runtime slice: `scheduler:provider-resilience-history-proof`. Current audit slice: `facility:provider-resilience-history-contract-audit`.

## Command

```bash
node tools/provider_resilience_history_contract_audit.mjs --json artifacts/audit/REV0044-PROVIDER-RESILIENCE-HISTORY-CONTRACT-AUDIT.json
```

## Future-session rule

Do not promote `ProviderResilienceHistoryRunner` to OPFS, browser Worker, production resilience, or performance language until a new manifest task and proof artifact earn that claim.


Current revision: rev0054


This rev0036 carry-forward audit doc is a future-session coherence guard.
