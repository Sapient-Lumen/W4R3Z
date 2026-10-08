# Open questions — rev0150

1. On a capable machine, does `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh` pass runtime import smoke, produce a dry-run download-plan receipt, materialize the locked TinyLlama snapshot, and then switch into local-only capture?
2. Does the digest receipt cache correctly avoid rehashing unchanged 2.2GB weights across same-snapshot gates while still forcing a full hash on the first acceptance?
3. Does the first real trace produce enough rows for the selector/evaluation receipts, or does `MAX_ROWS=128` need adjustment after one successful local-only run?
4. Are any tools in the REV0150 live closure still doctrine-only and removable from the external packet after the first real run returns actual receipts?
5. After the first trace exists, which fused backend should be the first named-hardware timing comparison: SDPA or FlashAttention, and on what GPU/driver stack?
