# Cube audit rev0032

Carry-forward revision: rev0033.

Rev0032 adds a circuit-breaker/bulkhead model oracle and refactors the current resilience office around generated-history evidence.

## Audit/factor work

- Added `scheduler:circuit-breaker-bulkhead-model-proof`.
- Added `facility:circuit-breaker-bulkhead-model-contract-audit`.
- Added current docs for the model frontier and slice.
- Updated current JSON surfaces from rev0031 to rev0032.
- Kept broad release browser-light.
- Kept previous rev0031 artifacts as allowed previous-revision evidence while new package artifacts move to REV0033.
- Preserved non-claims around OPFS/browser/production resilience/formal verification.

## Why this matters

The project now has both targeted examples and generated histories for resilience state-machine behavior. That makes future provider integration safer and reduces the chance that future sessions mistake a one-off proof for a complete policy machine.

## Remaining risks

- The reference model can still mirror implementation mistakes.
- The generated histories are finite.
- Real timers and provider latency remain untested.
- OPFS/browser/cross-tab/provider integration remains unearned.
