# Wake from amnesia — rev0058

Start here:

1. Read `docs/610-rev0058-finalityledger-retryescrow-pruneguard.md`.
2. Run `tests/test_rev0058_finality_retryescrow_pruneguard.py`.
3. Inspect `src/i2p_dht_lab/finalityledger.py`, `retryescrow.py`, and `pruneguard.py`.
4. Confirm `src/i2p_dht_lab/finalityfold.py` passes.

Mnemonic:

```text
reconcile says what happened locally;
finality says whether it can be terminal;
retry escrow says whether it may be retried;
prune guard says what memory must survive.
```
