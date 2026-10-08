# Substrate re-entry after native close

`substratereentry.py` is the gate back to generic I2P DHT design after the native branch.

It joins:

```text
rev0098 native branch close
rev0099 Python-owned record-plane oracle
native fold-spine through rev0099
exact substrate boundary
family/path diversity
hard-negative and record-plane memory preservation
```

The accepted state is `accept_return_to_dht_substrate`. It means the cube may continue designing DHT substrate semantics, not that the DHT is production-ready.

Native promotion still requires a future explicit design branch. The old branch remains closed.
