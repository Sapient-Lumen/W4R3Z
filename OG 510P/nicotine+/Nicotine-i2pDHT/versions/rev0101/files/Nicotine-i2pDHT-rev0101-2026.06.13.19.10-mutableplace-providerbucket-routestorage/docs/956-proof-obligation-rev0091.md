# Proof obligation — rev0091

Proof obligations pinned by tests:

- Oracle seal accepts only when loader seal, Python oracle, fallback, and memory flags agree.
- Oracle seal rejects parser/crypto/transport/persistence native surfaces.
- Preflight routes only to the load gate and forbids load/dispatch.
- Re-entry journal preserves preflight/oracle/fallback/fault memory.
- Replay, rollback, forks, previous-link mismatch, digest drift, and low diversity remain quarantine surfaces.
- Fold map, fold registry, surface ledger, native spine, and predecessor fold all pass.
