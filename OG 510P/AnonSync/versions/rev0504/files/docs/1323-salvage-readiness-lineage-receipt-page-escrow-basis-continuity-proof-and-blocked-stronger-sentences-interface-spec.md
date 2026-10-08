## Salvage-readiness lineage receipt

### Stores
- Recovery family requested
- Secret escrow basis
- Database continuity basis
- Locator basis
- Current salvage floor
- Active recovery lane
- Failure dependencies still in force
- Blocked stronger sentence

### Example receipt language
- `Encrypted bytes remain, but RW escrow is not proven; salvage claim capped at ciphertext retention.`
- `RW escrow is proven and original database continuity survives; reconnect-and-download lane remains available.`
- `Ciphertext directory still exists but encrypted folder was removed and re-added; same path survived, continuity proof did not.`
- `Local decrypt may be possible, but exact db locator depends on logs not yet preserved; guaranteed rescue sentence blocked.`

### Requirement
Every serious encrypted-backup, disaster-recovery, or source-failure review must leave behind one receipt that a later operator can read without having to rediscover hidden prerequisites from old support prose.
