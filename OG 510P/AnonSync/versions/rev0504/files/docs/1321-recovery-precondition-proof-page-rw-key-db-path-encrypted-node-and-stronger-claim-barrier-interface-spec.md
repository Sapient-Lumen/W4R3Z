## Recovery-precondition proof

### Goal
Prove the strongest honest rescue sentence without pretending that encrypted backup presence alone settles recovery.

### Proof ladder
1. **Ciphertext presence proof** — the encrypted node still holds bytes or Archive residue.
2. **Continuity proof** — the same Sync database lineage for that encrypted share still survives.
3. **Secret proof** — the RW key needed for decryption or reconnect is escrowed and retrievable.
4. **Locator proof** — the database artifact or shareID/db path needed for decrypt is locatable now.
5. **Lane proof** — the product can name the exact recovery lane: reconnect-and-download, local CLI decrypt, or another typed path.
6. **Blocked stronger sentence** — what the product still refuses to claim, such as guaranteed full restore without source or guaranteed operator simplicity.

### Strong-language barriers
Do not say `safe backup` unless secret escrow and continuity proof are both present.
Do not say `recoverable from encrypted node` unless the lane proof names how decryption will actually happen.
Do not say `restorable later` if db-path discovery still depends on logs/support that are not themselves proven available.
Do not say `archive can rescue this` when the only surviving peer is encrypted and read-only under source delete state.
