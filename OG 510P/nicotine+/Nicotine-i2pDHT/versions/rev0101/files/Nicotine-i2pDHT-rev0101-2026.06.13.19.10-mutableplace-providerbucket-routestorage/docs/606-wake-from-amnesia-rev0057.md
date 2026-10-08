# Wake from amnesia — rev0057

Read in this order:

1. `docs/600-rev0057-deadletter-retryquorum-effectreconcile.md`
2. `docs/601-dead-letter-lane-prepared-only.md`
3. `docs/602-retry-quorum-after-recovery-watch.md`
4. `docs/603-effect-reconcile-boundary.md`
5. `tests/test_rev0057_deadletter_retry_reconcile.py`
6. `src/i2p_dht_lab/deadletter.py`
7. `src/i2p_dht_lab/retryquorum.py`
8. `src/i2p_dht_lab/effectreconcile.py`
9. `src/i2p_dht_lab/reconcilefold.py`

Memory hook:

```text
Prepared-only is sticky. Retry does not erase dead-letter memory. Reconcile is exact-boundary only.
```
