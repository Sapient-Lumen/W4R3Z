# rev0059 — settlementstore-tombmesh-canaryjoin

rev0059 folds a sibling rev0058 branchlet back into the spoken finality/retry/prune line.

The risk this turn is branch split-brain:

```text
finality ledger accepted
+ retry escrow accepted
+ prune guard accepted
+ hidden settlement/attestation/tombstone branchlet existed
    ≠ safe local settlement
    ≠ safe tombstone repair
    ≠ safe future terminal receipt
```

New/folded surfaces:

- `attestationpack.py` — typed signed component-digest packs.
- `settlementlane.py` — sticky post-reconcile settlement memory.
- `tombstonerepair.py` — tombstone/revocation repair pressure after settlement.
- `settlementstore.py` — joined finality/settlement/prune/attestation/tombstone boundary.
- `terminalreceipt.py` — signed terminal receipt after finality and prune agree.
- `settlementfold.py` — rev0059 audit/refactor fold preserving rev0058 finalityfold predecessor history.

Strong sentence:

> A valid finality marker and a valid settlement entry are still two observations until the store joins them at the exact boundary.

The old alternate rev0058 settlement branchlet is preserved under `artifacts/branchlets/rev0058_settlement_attestation_tombrepair/` so wake-from-amnesia history remains visible while active code now follows the rev0059 joined path.

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production settlement store, no production attestation protocol, no production tombstone repair protocol, no finality consensus, no global reputation, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
