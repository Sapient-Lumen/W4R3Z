# Wake from amnesia — rev0099

rev0098 closed the native/GCC exploration as shadow-only. rev0099 returns to the DHT substrate and adds a record-plane oracle so the return is explicit.

Remember:

```text
recordplaneoracle: Python owns record truth
substratereentry: only re-enter DHT substrate after native close + record oracle + native spine agree
substratereturnfold: audit path for this pivot
```

The next likely seam is substrate-spine compaction: reconnect record-plane oracle work to mutable/provider/routing pressure without re-opening native authority.
